"""Universal Flow image system v2 (2026-11-01): job builder, continuity sheet, Codex review parsing and choice, filing record. No network, no Flow, no Codex."""
from __future__ import annotations

import copy
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts" / "flow"))
import build_jobs_v2 as bj  # noqa: E402
import neighbour_sheet as ns  # noqa: E402
import review_shot as rs  # noqa: E402
import download_queue as dq  # noqa: E402

SERIES = json.loads((ROOT / "config" / "flow_series.json").read_text(encoding="utf-8"))


def series_at(tmp: Path) -> dict:
    s = copy.deepcopy(SERIES)
    s["outputs_root"] = str(tmp)
    return s


def png(path: Path, colour=(200, 120, 60), size=(2752, 1536)) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    Image.new("RGB", size, colour).save(path)
    return path


def spec(**shot) -> dict:
    s = {"shot_id": "SH_S2_09", "scene": "S2", "method": "generate", "characters": ["GM_v01"], "place": "ROAD",
         "action": "The young ascetic sits still on the road.", "light": "Light: clear late-morning sun."}
    s.update(shot)
    return {"adhyay": 1, "slot_order": {"S2": ["SH_S2_08", "SH_S2_09", "SH_S2_04"]}, "shots": [s]}


# ------------------------------------------------------------------ builder
def test_prompt_has_exact_count_strict_sheet_sentence_one_style_chip_and_no_filtered_words(tmp_path):
    job = bj.build(spec(), series_at(tmp_path), 1)[0]
    assert "Exactly 1 person:" in job["prompt"] and "NOT a tank top" in job["prompt"] and "legs uncovered" in job["prompt"]
    assert job["chips"] == ["GM_v01", "Village road in front house"] and job["people_count"] == 1
    assert job["prompt"].endswith("No text, no letters, no modern objects, no halo.")
    for w in SERIES["forbidden_words"]:
        assert not __import__("re").search(w, job["prompt"], __import__("re").I), w


def test_no_people_prompt_and_unaccepted_sheet_warning(tmp_path):
    job = bj.build(spec(characters=[]), series_at(tmp_path), 1)[0]
    assert "No people in the picture." in job["prompt"] and "Show only these people" not in job["prompt"]
    job2 = bj.build(spec(characters=["DK_v01"]), series_at(tmp_path), 1)[0]
    assert job2["unaccepted_sheets"] == ["DK_v01"]


def test_neighbours_prefer_the_final_then_the_newest_candidate_and_version_is_next_free(tmp_path):
    s = series_at(tmp_path)
    ch = tmp_path / "adhyay_01"
    png(ch / "shots" / "SH_S2_09__candidate_v01.png")
    png(ch / "shots" / "SH_S2_04__candidate_v01.png")
    png(ch / "shots" / "SH_S2_04__candidate_v03.png")
    (ch / "final").mkdir(parents=True)
    (ch / "final" / "FINAL_IMAGE_LIST_A1.json").write_text(json.dumps([{"shot_id": "SH_S2_08", "version": "v04", "final_file": str(ch / "final" / "SH_S2_08.png")}]), encoding="utf-8")
    job = bj.build(spec(), s, 1)[0]
    assert job["file_version"] == "v02" and job["flow_title"] == "SH_S2_09__v02"
    assert job["previous_shot"]["flow_title"] == "SH_S2_08__v04" and job["previous_shot"]["source"] == "final"
    assert job["next_shot"]["flow_title"] == "SH_S2_04__v03" and job["next_shot"]["source"] == "newest candidate"


@pytest.mark.parametrize("bad, msg", [
    (dict(characters=["XX_v01"]), "not in config"),
    (dict(place="MOON"), "unknown place"),
    (dict(method="paint"), "generate or edit"),
    (dict(method="edit"), "an edit needs"),
    (dict(method="edit", base_edit_id="e1", edit_instruction="Make it nicer"), "an edit needs"),
    (dict(action="He sits, naked, on the road."), "forbidden words"),
    (dict(shot_id="SH_S2_99"), "not in slot_order"),
])
def test_bad_specs_are_refused(tmp_path, bad, msg):
    with pytest.raises(bj.SpecError, match=msg):
        bj.build(spec(**bad), series_at(tmp_path), 1)


def test_a_valid_edit_job_and_wrong_adhyay(tmp_path):
    job = bj.build(spec(method="edit", base_edit_id="e1", edit_instruction="Change only the vest. Keep everything else exactly the same: pose, place."), series_at(tmp_path), 1)[0]
    assert job["method"] == "edit" and job["attempt_cap"] == 8 and job["base_edit_id"] == "e1"
    with pytest.raises(bj.SpecError, match="not 2"):
        bj.build(spec(), series_at(tmp_path), 2)


def test_real_new_shot_jobs_build():
    s = json.loads((ROOT / "canon" / "drafts" / "A1_image_spec_new_shots.json").read_text(encoding="utf-8"))
    jobs = bj.build(s, SERIES, 1)
    assert [j["shot_id"] for j in jobs] == ["SH_S2_09", "SH_S2_10", "SH_S2_11", "SH_S7_10", "SH_S7_11", "SH_S7_12"]
    assert not any("ref_temple" in c for j in jobs for c in j["chips"])                     # no style image chip (it leaked a temple)


# ------------------------------------------------------------------ continuity sheet
def test_sheet_has_three_neighbour_tiles_and_the_reference_row(tmp_path):
    a, c = png(tmp_path / "a.png", (10, 10, 200)), png(tmp_path / "c.png", (10, 200, 10))
    ref = png(tmp_path / "ref.png", (200, 200, 200), (800, 600))
    job = {"flow_title": "SH_X__v01", "previous_shot": {"file": str(a), "flow_title": "SH_A"}, "next_shot": None, "sheets": [str(ref)]}
    out = ns.build_sheet(job, str(c), tmp_path / "s.jpg")
    with Image.open(out) as im:
        assert im.width == 3 * ns.W + 4 * ns.PAD and im.height > ns.H + ns.REF_H
        mid = im.getpixel((ns.PAD + ns.W + ns.PAD + ns.W // 2, ns.PAD + ns.LABEL + ns.H // 2))
        left = im.getpixel((ns.PAD + ns.W // 2, ns.PAD + ns.LABEL + ns.H // 2))
        assert mid[1] > 150 and left[2] > 150                      # candidate in the middle, previous on the left


def test_pair_sheet_puts_both_candidates_between_the_neighbours(tmp_path):
    a = png(tmp_path / "a.png", (10, 10, 200))
    c1, c2 = png(tmp_path / "c1.png", (10, 200, 10)), png(tmp_path / "c2.png", (200, 10, 10))
    job = {"flow_title": "SH_X__v01", "previous_shot": {"file": str(a), "flow_title": "SH_A"}, "next_shot": None, "sheets": []}
    out = ns.build_sheet(job, [str(c1), str(c2)], tmp_path / "s.jpg")
    with Image.open(out) as im:
        w = 720
        assert im.width == 4 * w + 5 * ns.PAD
        y = ns.PAD + ns.LABEL + 200
        assert im.getpixel((ns.PAD + w + ns.PAD + w // 2, y))[1] > 150 and im.getpixel((ns.PAD + 2 * (w + ns.PAD) + w // 2, y))[0] > 150


# ------------------------------------------------------------------ review parsing (fail closed)
def block_text(label: str, results=None, fix="none", edit="none", regen="none", verdict="PASS") -> str:
    results = results or {}
    lines = [f"{label} Q{i}: {results.get(i, 'PASS')} - reason {i}" for i in range(1, 7)]
    return "\n".join(lines + [f"{label} FIX: {fix}", f"{label} EDIT_INSTRUCTION: {edit}", f"{label} REGEN_SENTENCE: {regen}", f"{label} VERDICT: {verdict}"])


def test_all_pass_is_pass_and_labels_are_kept_apart():
    t = block_text("A") + "\n" + block_text("B", {4: "BLOCK"}, fix="regenerate", regen="Keep the gourd.", verdict="BLOCK")
    a, b = rs.parse(t, "A"), rs.parse(t, "B")
    assert a["verdict"] == "PASS" and b["verdict"] == "BLOCK" and b["regen_sentence"] == "Keep the gourd." and b["fix"] == "regenerate"


def test_any_block_is_block_even_if_the_reviewer_says_pass():
    r = rs.parse(block_text("A", {4: "BLOCK"}, verdict="PASS"), "A")
    assert r["verdict"] == "BLOCK" and r["fix"] == "regenerate"         # a block without a fix falls back to regenerate
    r2 = rs.parse(block_text("A", {2: "BLOCK"}, fix="edit", edit="Change only the door. Keep everything else exactly the same: people.", verdict="BLOCK"), "A")
    assert r2["fix"] == "edit" and r2["edit_instruction"].startswith("Change only")


def test_missing_answer_or_unsure_or_no_verdict_is_unsure():
    full = block_text("A")
    assert rs.parse(full.replace("A Q6: PASS - reason 6\n", ""), "A")["verdict"] == "UNSURE"
    assert rs.parse(block_text("A", {2: "UNSURE"}, verdict="PASS"), "A")["verdict"] == "UNSURE"
    assert rs.parse(full.replace("A VERDICT: PASS", ""), "A")["verdict"] == "UNSURE"
    assert rs.parse("", "A")["verdict"] == "UNSURE"
    assert rs.parse(block_text("A"), "B")["verdict"] == "UNSURE"        # B's lines missing -> B unsure, never borrowed from A


def test_a_bad_edit_instruction_becomes_regenerate():
    assert rs.parse(block_text("A", {1: "BLOCK"}, fix="edit", edit="make it better", verdict="BLOCK"), "A")["fix"] == "regenerate"


def test_choose_keeps_only_a_pass_and_prefers_fewer_advisories():
    def r(c, v, adv=0):
        ans = {f"Q{i}": {"result": "ADVISORY" if i <= adv else "PASS", "reason": ""} for i in range(1, 7)}
        return {"candidate": c, "label": c, "verdict": v, "answers": ans, "fix": "regenerate" if v == "BLOCK" else "none", "edit_instruction": None, "regen_sentence": "s"}
    assert rs.choose([r("a", "PASS", 2), r("b", "PASS", 0)])["chosen"] == "b"
    assert rs.choose([r("a", "BLOCK"), r("b", "PASS")])["chosen"] == "b"
    assert rs.choose([r("a", "BLOCK"), r("b", "UNSURE")])["decision"] == "BLOCK"
    assert rs.choose([r("a", "UNSURE"), r("b", "UNSURE")])["decision"] == "UNSURE"


def test_codex_command_is_read_only_sol_medium_with_all_images(tmp_path):
    cmd = rs.codex_command([tmp_path / "s.jpg", tmp_path / "a.png", tmp_path / "b.png"], tmp_path / "o.md", codex="codex")
    assert cmd[cmd.index("-m") + 1] == "gpt-6.1-sol" and "model_reasoning_effort=medium" in cmd
    assert cmd[cmd.index("-s") + 1] == "read-only" and cmd.count("-i") == 3 and cmd[-1] == "-"


def test_one_codex_call_reviews_both_candidates_and_failure_is_unsure(tmp_path):
    a, b = png(tmp_path / "A.png", (90, 90, 90), (800, 450)), png(tmp_path / "B.png", (90, 90, 90), (800, 450))   # screenshots are fine
    job = {"shot_id": "SH_S2_09", "flow_title": "SH_S2_09__v02", "prompt": "p", "prompt_sha256": "h", "people_count": 1,
           "previous_shot": None, "next_shot": None, "sheets": []}
    calls = []

    def ok(cmd, prompt):
        calls.append(cmd)
        assert "For EACH candidate (A, B)" in prompt and "exactly 1 visible people" in prompt
        Path(cmd[cmd.index("-o") + 1]).write_text(block_text("A", {5: "BLOCK"}, fix="regenerate", regen="Medium shot.", verdict="BLOCK") + "\n" + block_text("B"), encoding="utf-8")
        return 0, ""
    out = rs.review(job, [a, b], runner=ok)
    assert len(calls) == 1 and calls[0].count("-i") == 3
    assert out["choice"] == {"decision": "PASS", "chosen": str(b), "label": "B"} and Path(out["sheet"]).is_file()
    assert json.loads(a.with_name("A__review.json").read_text(encoding="utf-8"))["model"] == "gpt-6.1-sol"
    bad = rs.review(job, [a, b], runner=lambda cmd, p: (1, "boom"))
    assert bad["choice"]["decision"] == "UNSURE" and all(r["verdict"] == "UNSURE" for r in bad["results"])


# ------------------------------------------------------------------ download queue (the separate download step)
def test_queue_add_status_and_collect_by_exact_title(tmp_path):
    root, dl = tmp_path / "out", tmp_path / "dl"
    dl.mkdir()
    eid = "97d2bca6-2111-45a4-aefb-55d2c5159858"
    dq.add(root, 1, "SH_S2_09", "v02", eid, model="Nano Banana Pro")
    dq.add(root, 1, "SH_S2_10", "v02", eid)
    with pytest.raises(ValueError):
        dq.add(root, 1, "SH_S2_11", "2", eid)
    with pytest.raises(ValueError):
        dq.add(root, 1, "SH_S2_11", "v02", "not-an-id")
    assert [i["flow_title"] for i in dq.status(root, 1)["pending"]] == ["SH_S2_09__v02", "SH_S2_10__v02"]
    (dl / "SH_S2_09__v02_11dddaad_2K.jpg").write_bytes(b"x")
    (dl / "SH_S2_09__v02b_22eeeeee_2K.jpg").write_bytes(b"x")          # the other x2 image: never taken for v02
    (dl / "SH_S2_1__v02_33ffffff_2K.jpg").write_bytes(b"x")            # a different title: never taken
    assert dq.find_download(dl, "SH_S2_09__v02").name == "SH_S2_09__v02_11dddaad_2K.jpg" and dq.find_download(dl, "SH_S2_10__v02") is None
    seen = []

    def fake(cmd, env):
        seen.append(cmd)
        with (root / "adhyay_01" / "flow_log.jsonl").open("a", encoding="utf-8") as f:
            f.write(json.dumps({"image_id": cmd[3], "version": cmd[4]}) + "\n")
        return subprocess.CompletedProcess(cmd, 0, "filed", "")
    rep = dq.collect(root, 1, dl, run=fake)
    assert rep[0].startswith("FILED SH_S2_09__v02") and rep[1].startswith("WAITING SH_S2_10__v02") and len(seen) == 1
    assert seen[0][-1] == "Nano Banana Pro" and seen[0][4] == "v02"
    assert [i["flow_title"] for i in dq.status(root, 1)["filed"]] == ["SH_S2_09__v02"]



# ------------------------------------------------------------------ filing record
def test_filing_records_the_actual_job_prompt_and_the_model_shown(tmp_path):
    root = Path("D:/aai work/flow_outputs/adhyay_98")
    if root.exists():
        shutil.rmtree(root)
    try:
        src = tmp_path / "SH_T_01__v01_2K.jpg"
        Image.new("RGB", (2752, 1536), (90, 30, 30)).save(src, quality=90)
        jobs = tmp_path / "jobs.json"
        jobs.write_text(json.dumps([{"shot_id": "SH_T_01", "prompt_sha256": "abc123", "chips": ["GM_v01", "ref_temple"]}]), encoding="utf-8")
        env = dict(os.environ, FLOW_ADHYAY="98", FLOW_OPERATOR="haiku", PYTHONIOENCODING="utf-8")
        p = subprocess.run([sys.executable, str(ROOT / "scripts" / "flow" / "file_flow_download.py"), str(src), "SH_T_01", "v01", "edit/e1", "GM_v01|ref_temple", "test", "shots", str(jobs), "Nano Banana Pro"],
                           capture_output=True, text=True, env=env)
        assert p.returncode == 0, p.stderr
        rec = json.loads((root / "flow_log.jsonl").read_text(encoding="utf-8").splitlines()[-1])
        assert rec["prompt_sha256"] == "abc123" and rec["prompt_source"].startswith("jobs v2") and rec["model_shown"] == "Nano Banana Pro"
        assert rec["operator"] == "haiku" and rec["chips"] == ["GM_v01", "ref_temple"] and (root / "shots" / "SH_T_01__candidate_v01.png").is_file()
    finally:
        if root.exists():
            shutil.rmtree(root)


def test_props_add_their_sentence_chip_and_sheet_and_unknown_props_are_refused(tmp_path):
    job = bj.build(spec(props=["LEAF_PLATES"]), series_at(tmp_path), 1)[0]
    assert "stitched together from several dry leaves" in job["prompt"] and job["props"] == ["LEAF_PLATES"]
    assert job["chips"] == ["GM_v01", "Village road in front house", "Storybook illustration prop"]
    assert job["sheets"][-1].endswith("PR_LEAF_PLATES__v01__accepted.png")
    with pytest.raises(bj.SpecError, match="props not in config"):
        bj.build(spec(props=["SWORD"]), series_at(tmp_path), 1)


def test_only_accepted_neighbours_become_chips(tmp_path):
    s = series_at(tmp_path)
    ch = tmp_path / "adhyay_01"
    png(ch / "shots" / "SH_S2_04__candidate_v01.png")                       # newest candidate only: never attached
    (ch / "final").mkdir(parents=True)
    (ch / "final" / "FINAL_IMAGE_LIST_A1.json").write_text(json.dumps([{"shot_id": "SH_S2_08", "version": "v04", "final_file": "x.png"}]), encoding="utf-8")
    job = bj.build(spec(), s, 1)[0]
    assert job["neighbour_chips"] == ["SH_S2_08__v04"] and job["neighbour_sentence"].startswith("Match the attached neighbouring shot")


def test_reference_chips_and_sentence_for_a_close_up(tmp_path):
    job = bj.build(spec(place=None, reference_chips=["SH_S2_05__v02"], reference_sentence="Match the attached close-up shot."), series_at(tmp_path), 1)[0]
    assert job["chips"] == ["GM_v01", "SH_S2_05__v02"] and "Match the attached close-up shot. Full-frame" in job["prompt"] and "Setting:" not in job["prompt"]
