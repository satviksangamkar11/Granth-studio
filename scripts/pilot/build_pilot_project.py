"""Generate the PROVISIONAL 45-second pilot project (Adhyay 1, ovi 87-119 selection) as ordinary GranthStudio project files under ./pilot.

  python scripts/pilot/build_pilot_project.py [--out pilot]

Everything is derived from docs/pilot/SOURCE_APPROVAL_SHEET.md: the six narrated ovis, the three scenes, source references by ovi number and printed page. It invents nothing:
actions, details and props are the text's own words; anything about composition (modest framing) is flagged `artistic: true`. The Marathi is the assistant's transcription from the
page images and the Hindi lines are assistant drafts: both are PROVISIONAL TEST material, `docs/pilot/SOURCE_APPROVAL_SHEET.md` stays UNSIGNED, and this project is NOT Granth canon.
The research is NOT approved here (`research approve` is a named human step); tests approve a temporary copy with a synthetic approver to exercise the compiler.
"""
from __future__ import annotations

import argparse
import shutil
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
PROVISIONAL = "PILOT TEST ONLY (provisional, owner's creative confirmation 2026-10-23); not Granth canon"

NARRATOR = "chr_narrator"
OVI = {  # sequence number: (printed page, Marathi as transcribed, Hindi assistant draft)
    87: ("10", "उष्ट्या पत्रावळी रस्त्यावर । टाकिल्या होत्या साचार । घराचिया समोर । त्या देविदास विप्राच्या",
         "देविदास ब्राह्मण के घर के सामने रास्ते पर जूठी पत्तलें फेंकी हुई थीं।"),
    94: ("11", "शीत पडल्या दृष्टीप्रत । तें मुखी उचलुनी घालीत । हे करण्याचा हाच हेत । अन्न परब्रह्म कळवावया",
         "जो भी भात का दाना उनकी दृष्टि में आता, उसे उठाकर वे मुँह में डाल लेते; ऐसा करने का उद्देश्य यही था कि अन्न ही परब्रह्म है, यह बताया जाए।"),
    97: ("11", "बंकटलाल आगरवाला । होता रस्त्यानें चालला । त्याने हा प्रकार पाहिला । आपल्या त्या स्नेह्यासह",
         "बंकटलाल अग्रवाल रास्ते से चले जा रहे थे; उन्होंने अपने उस मित्र के साथ यह सब देखा।"),
    109: ("11", "ह्या पत्रावळीच्या शोधना । कां हो करितां कळेना । क्षुधा असेल आपणां । तरी तरतूद करूं अन्नाची",
          "\"इन पत्तलों को आप क्यों खंगाल रहे हैं, समझ नहीं आता। यदि आपको भूख हो तो हम अन्न का प्रबंध कर देंगे।\""),
    114: ("12", "देविदासें तैसें केलें । पक्कान्नांनीं भरलेले । पात्र आणून ठेविलें । द्वारासमोर स्वामींपुढे",
          "देविदास ने वैसा ही किया; पकवानों से भरी थाली लाकर द्वार के सामने स्वामी के आगे रख दी।"),
    119: ("12", "बंकटलाल तें पाहून । पंताशी करी भाषण । ह्या वेडा म्हणालो आपण । ती नि:संशय झाली चुकी",
          "यह देखकर बंकटलाल पंत से बोले: \"हमने इन्हें पागल कहा, वह निःसंशय हमारी भूल थी।\""),
}
LINES = [("d_0001", 87, "a01_s01", "a01_s01_sh01"), ("d_0002", 94, "a01_s01", "a01_s01_sh03"), ("d_0003", 97, "a01_s02", "a01_s02_sh01"),
         ("d_0004", 109, "a01_s02", "a01_s02_sh03"), ("d_0005", 114, "a01_s03", "a01_s03_sh01"), ("d_0006", 119, "a01_s03", "a01_s03_sh03")]


def page_for(ovi: int) -> str:
    """Printed page of an ovi in e-shree-gajanan-vijay-granth.pdf (checked on the rendered pages 5-7: ovi 84-89 on printed page 10, 90 spans 10-11, 91-113 on 11, 114-121 on 12)."""
    return "10" if ovi <= 89 else "10-11" if ovi == 90 else "11" if ovi <= 113 else "12"


def ref(ovi: int) -> str:
    printed = page_for(ovi)
    low, _, high = printed.partition("-")
    pdf = f"{int(low) - 5}-{int(high) - 5}" if high else str(int(low) - 5)
    return f"Adhyay 1 ovi {ovi} (printed page {printed}; PDF page {pdf})"


def fact(fid: str, text: str, ovis: list[int], artistic: bool = False) -> dict:
    return {"id": fid, "text": text, "source_refs": [ref(o) for o in ovis], "artistic": artistic}


def canon_entry(entry_id: str, name: str, evidence: str, aliases: list[str] | None = None, **extra) -> dict:
    return {"id": entry_id, "canonical_name": name, "aliases": aliases or [], "status": "pending", "evidence": [evidence, PROVISIONAL], **extra}


def research() -> dict:
    def scene(scene_id, location, characters, props, description, actions, details, lines):
        return {"scene_id": scene_id, "source_refs": sorted({r for f in [*actions, *details] for r in f["source_refs"]}), "location": location,
                "characters": characters, "props": props, "description": description, "actions": actions, "visual_details": details, "continuity": [],
                "dialogue": [{"id": d, "speaker": NARRATOR, "text": OVI[o][1], "source_ref": ref(o)} for d, o, s, _ in LINES if s == scene_id]}
    maharaj, devidas, bankat, pant = "chr_gajanan_maharaj", "chr_devidas", "chr_bankatlal", "chr_damodarpant"
    return {"schema_version": 1, "adhyay": 1, "open_questions": [],
            "overview": "PILOT TEST ONLY: three consecutive moments of Adhyay 1 (ovi 84-121) narrated by six verbatim ovis. " + PROVISIONAL,
            "scenes": [
        scene("a01_s01", "loc_devidas_house_road", [maharaj, NARRATOR], ["prp_leaf_plates", "prp_gourd_vessel", "prp_clay_chilam"],
              "Used leaf plates lie on the road in front of Devidas's house; Gajanan Maharaj sits there and picks up grains of rice (ovi 87-94).",
              [fact("act_s1_sit", "Gajanan Maharaj sits on the road in front of Devidas's house among the thrown leaf plates", [87, 88, 93]),
               fact("act_s1_pick", "He picks leftover grains of rice from the leaf plates and puts them in his mouth", [93, 94])],
              [fact("det_s1_vest", "He wears an old vest of worn cloth; he has a gourd for drinking water and a hand-made clay chilam in his hand", [88, 89, 90]),
               fact("det_s1_gaze", "His gaze rests steadily on the tip of his nose and his expression is calm", [91]),
               fact("det_s1_frame", "Shown seated and framed from the waist up, a modest composition", [92], artistic=True)], []),
        scene("a01_s02", "loc_devidas_house_road", [maharaj, bankat, pant, NARRATOR], ["prp_leaf_plates"],
              "Bankatlal Agarwal and Damodarpant Kulkarni see him, think him mad, and Bankatlal asks him why he searches the plates (ovi 97-110).",
              [fact("act_s2_watch", "Bankatlal Agarwal and his friend Damodarpant Kulkarni, walking along the road, see Gajanan Maharaj searching the leaf plates", [97, 98]),
               fact("act_s2_ask", "Bankatlal steps forward and respectfully asks him why he searches the leaf plates; Maharaj gives no answer and only looks at them both", [108, 109, 110])],
              [fact("det_s2_plates", "Leaf plates lie on the road around him", [87, 93])], []),
        scene("a01_s03", "loc_devidas_house_road", [maharaj, devidas, bankat, pant, NARRATOR], ["prp_sweet_dishes_plate", "prp_leaf_plates"],
              "Devidas sets a plate of sweet dishes before him, he eats, and Bankatlal admits to Pant that calling him mad was a mistake (ovi 114-121).",
              [fact("act_s3_place", "Devidas brings a plate filled with sweet dishes and sets it down at the door in front of Maharaj", [114]),
               fact("act_s3_eat", "Maharaj sits down to the plate and eats, mixing all the dishes into one", [115, 118]),
               fact("act_s3_admit", "Bankatlal tells Pant that calling him mad was undoubtedly a mistake", [119])],
              [fact("det_s3_midday", "It is midday", [118])], [])]}


def canon_files() -> dict[str, dict]:
    def doc(kind, entries):
        return {"schema_version": 1, "kind": kind, "entries": entries, "identity_decisions": []}
    return {
        "characters": doc("characters", [
            canon_entry("chr_gajanan_maharaj", "Shri Gajanan Maharaj", "Adhyay 1 ovi 88-92, 111", ["Gajanan", "गजानन", "समर्थ"]),
            canon_entry("chr_devidas", "Devidas Paturkar", "Adhyay 1 ovi 84-87", ["Devidas", "देविदास"]),
            canon_entry("chr_bankatlal", "Bankatlal Agarwal", "Adhyay 1 ovi 97", ["Bankatlal", "बंकटलाल"]),
            canon_entry("chr_damodarpant", "Damodarpant Kulkarni", "Adhyay 1 ovi 98", ["Damodarpant", "दामोदरपंत", "Pant", "पंत"]),
            canon_entry(NARRATOR, "Narrator (the author, voice only)", "the verses are narration", ["Narrator"], voice_only=True)]),
        "locations": doc("locations", [canon_entry("loc_devidas_house_road", "The road in front of Devidas's house", "Adhyay 1 ovi 87", ["रस्ता"])]),
        "props": doc("props", [canon_entry("prp_leaf_plates", "Used leaf plates", "ovi 87", ["पत्रावळी"]), canon_entry("prp_gourd_vessel", "Gourd water vessel", "ovi 89", ["भोपळा"]),
                               canon_entry("prp_clay_chilam", "Clay chilam", "ovi 90", ["चिलीम"]), canon_entry("prp_sweet_dishes_plate", "Plate of sweet dishes", "ovi 114", ["पक्कान्न"])]),
        "terminology": doc("terminology", [canon_entry("term_parabrahma", "परब्रह्म", "ovi 94", [], protected=True, hi_allowed=["परब्रह्म"])]),
    }


def designs() -> list[dict]:
    """Appearance prompts for the provisional test: ONLY what the text says, or a plainly artistic interpretation (artistic: true). The assistant drafted them; the owner reviews them."""
    def design(canon_id, prompt, ovis, artistic):
        return {"canon_id": canon_id, "prompt": prompt, "source_refs": [ref(o) for o in ovis] or [PROVISIONAL], "artistic": artistic}
    return [
        design("chr_gajanan_maharaj", "a young man in the prime of youth with a radiant complexion, strong upper arms and neck and a broad chest, wearing only an old worn vest, "
               "seated calmly with a steady, inward gaze at the tip of the nose, shown seated and framed from the waist up", [88, 91, 111], True),
        design("chr_devidas", "a devout Brahmin householder of the village in a plain dhoti and shoulder cloth (appearance is not given in the text)", [84, 85], True),
        design("chr_bankatlal", "a local man of the village walking along the road in everyday dress of the period (appearance is not given in the text)", [97], True),
        design("chr_damodarpant", "a local man of the village, a friend of Bankatlal, in everyday dress of the period (appearance is not given in the text)", [98], True),
        design("loc_devidas_house_road", "a village road in front of a house, midday sun, used leaf plates on the ground (the rest of the setting is an artistic interpretation)", [87, 118], True),
    ]


def manifest() -> dict:
    def shot(sid, tier, vid, duration, dialogue, actions, **extra):
        item = {"shot_id": sid, "tier": tier, "visual_id": vid, "duration_s": duration, "dialogue_ids": dialogue, "action_ids": actions, **extra}
        if tier == 1:
            item["frames"] = 49
        return item
    def sc(n, chars, props, shots):
        return {"scene_id": f"a01_s0{n}", "research_scene": f"a01_s0{n}", "location": "loc_devidas_house_road", "characters": chars, "props": props, "lighting": "day_outdoor", "shots": shots}
    m, d, b, p = "chr_gajanan_maharaj", "chr_devidas", "chr_bankatlal", "chr_damodarpant"
    return {"schema_version": 1, "episode_id": "ep01", "adhyay": 1, "research_version": 1,
            "visuals": [{"visual_id": f"vis_s{n}_kf", "source": "keyframe", "path": f"kf/vis_s{n}_kf.png", "sha256": None} for n in (1, 2, 3)],
            "scenes": [
                sc(1, [m, NARRATOR], ["prp_leaf_plates", "prp_gourd_vessel", "prp_clay_chilam"], [
                    shot("a01_s01_sh01", 0, "vis_s1_kf", 6.0, ["d_0001"], ["act_s1_sit"]),
                    shot("a01_s01_sh02", 1, "vis_s1_kf", 2.04, [], ["act_s1_pick"]),
                    shot("a01_s01_sh03", 0, "vis_s1_kf", 6.5, ["d_0002"], [])]),
                sc(2, [m, b, p, NARRATOR], ["prp_leaf_plates"], [
                    shot("a01_s02_sh01", 0, "vis_s2_kf", 5.5, ["d_0003"], ["act_s2_watch"]),
                    shot("a01_s02_sh02", 1, "vis_s2_kf", 2.04, [], ["act_s2_ask"]),
                    shot("a01_s02_sh03", 0, "vis_s2_kf", 6.5, ["d_0004"], [])]),
                sc(3, [m, d, b, p, NARRATOR], ["prp_sweet_dishes_plate", "prp_leaf_plates"], [
                    shot("a01_s03_sh01", 0, "vis_s3_kf", 5.0, ["d_0005"], ["act_s3_place"]),
                    shot("a01_s03_sh02", 1, "vis_s3_kf", 2.04, [], ["act_s3_eat"]),
                    shot("a01_s03_sh03", 0, "vis_s3_kf", 6.5, ["d_0006"], ["act_s3_admit"])])]}


def timelines() -> dict[str, dict]:
    mr = {"schema_version": 1, "language": "mr", "adhyay": 1, "entries": [
        {"dialogue_id": d, "shot_id": sh, "speaker": NARRATOR, "text": OVI[o][1]} for d, o, s, sh in LINES]}
    hi = {"schema_version": 1, "language": "hi", "adhyay": 1, "entries": [
        {"dialogue_id": d, "shot_id": sh, "speaker": NARRATOR, "text": OVI[o][2],
         "alignment": {"mr_dialogue_id": d, "match": "adapted", "reviewed": False}} for d, o, s, sh in LINES]}
    return {"mr": mr, "hi": hi}


NOTICE = ("# PROVISIONAL PILOT TEST FILE: generated by scripts/pilot/build_pilot_project.py; NOT approved research, NOT Granth canon, NOT a release text.\n"
          "# Marathi = the assistant's transcription from the page images (to be proofread); Hindi = assistant draft. See docs/pilot/SOURCE_APPROVAL_SHEET.md (unsigned).\n")


def write(path: Path, document) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(NOTICE + yaml.safe_dump(document, allow_unicode=True, sort_keys=False, width=200), encoding="utf-8")


def approve_provisional_canon(project, approver: str) -> None:
    """Run-time only: mark the pilot's canon entries approved for the PROVISIONAL TECHNICAL TEST, naming who said so. Never applied to the shipped files."""
    for name in ("characters", "locations", "props", "terminology"):
        path = project.canon_dir / f"{name}.yaml"
        document = yaml.safe_load(path.read_text(encoding="utf-8"))
        for entry in document["entries"]:
            entry["status"] = "approved"
            entry["evidence"] = [*entry.get("evidence", []), f"approved for the provisional technical test by {approver}"]
        write(path, document)


def build(out: Path) -> Path:
    out.mkdir(parents=True, exist_ok=True)
    config = out / "config"
    config.mkdir(exist_ok=True)
    for name in ("models.yaml", "quality_gates.yaml", "runtime.yaml", "pilot.yaml"):
        shutil.copyfile(ROOT / "config" / name, config / name)
    templates = out / "workflows" / "comfyui"
    templates.mkdir(parents=True, exist_ok=True)
    for template in (ROOT / "workflows" / "comfyui").glob("*.json"):                         # the repository's templates, unchanged (stubs/candidates stay UNVALIDATED)
        shutil.copyfile(template, templates / template.name)
    write(config / "project.yaml", {"schema_version": 1, "artifacts_dir": "../../granthstudio-artifacts-pilot", "research_dir": "research", "canon_dir": "canon",
                                    "episodes_dir": "episodes", "benchmarks_dir": "benchmarks", "timezone": "Asia/Calcutta"})
    for name, document in canon_files().items():
        write(out / "canon" / f"{name}.yaml", document)
    shutil.copyfile(ROOT / "canon" / "style.yaml", out / "canon" / "style.yaml")                         # the frozen style v1 file, unchanged
    write(out / "canon" / "visual_assets.yaml", {"schema_version": 1, "style": None, "designs": designs(), "assets": []})
    write(out / "research" / "adhyay_01" / "research.yaml", research())
    write(out / "episodes" / "adhyay_01" / "manifest.yaml", manifest())
    for language, document in timelines().items():
        write(out / "episodes" / "adhyay_01" / f"{language}.yaml", document)
    (out / "README.md").write_text("PROVISIONAL pilot project (ovi 87/94/97/109/114/119). Research is NOT approved, canon is not Granth canon, Hindi lines are drafts, "
                                   "no voices are recorded. See docs/pilot/SOURCE_APPROVAL_SHEET.md.\n", encoding="utf-8")
    return out


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--out", type=Path, default=ROOT / "pilot")
    print(build(parser.parse_args().out))
