"""Builds canon/drafts/A1_flow_regen_jobs.json (v02 redo jobs) from A1_flow_shot_jobs.json + the review fixes (docs: flow_outputs/adhyay_01/REGENERATE_LIST_A1.md).
Same job format as the shot jobs; flow_title is <shot>__v02; stray bracketed story notes are removed; changed character sets drop the old cue entries."""
import json, re
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
jobs = {j["shot_id"]: j for j in json.loads((ROOT / "canon/drafts/A1_flow_shot_jobs.json").read_text(encoding="utf-8"))}
CUE = {"GM_v01": "GM_v01 (the calm young ascetic (short dark hair, worn grey-white vest)", "BA_v01": "BA_v01 (Bankatlal", "DK_v01": "DK_v01 (Damodarpant", "DV_v01": "DV_v01 (Devidas"}
ROAD, CATTLE = "Village road", "Cattle drinking"
V = "the young ascetic wears the same open frayed grey-white vest and white waist cloth as the reference sheet, chest visible under the open vest, same face and build as the sheet"
FIX = {  # shot: (chars, place, added sentences, [prompt phrases to cut])
 "SH_S4_03": (["GM_v01", "BA_v01", "DK_v01"], ROAD, "Exactly three people: Bankatlal in the cream turban and sage coat on the left, one Damodarpant in the terracotta turban and white dhoti on the right, and the young ascetic seated between them among the leaf plates. Draw no second Damodarpant.", []),
 "SH_S5_06": (["GM_v01"], ROAD, "One single full-frame image with no inset, no border and no picture-in-picture. The young ascetic sits on the ground at the leaf plate, his right hand mixing all the food on the plate into one heap. The house is the same tiled mud-brick house with the plain wooden door as the village road reference.", []),
 "SH_S7_04": (["GM_v01"], ROAD, "Show only the young ascetic, alone in the frame. The people he laughs at are out of frame and must not be drawn; the right side of the frame is open dusty ground.", []),
 "SH_S9_02": (["GM_v01", "BA_v01", "DK_v01"], CATTLE, "The " + V.replace("the young ascetic wears", "young ascetic wears") + ". No tank top, no shorts.", []),
 "SH_S9_08": (["GM_v01"], CATTLE, "The young ascetic is the adult from the reference sheet, wearing the open frayed grey-white vest and a white waist cloth. Behind him the wide open plain stretches under the noon sky.", []),
 "SH_S9_11": (["BA_v01", "DK_v01"], CATTLE, "Exactly two people: Bankatlal in the cream turban and sage coat, and one Damodarpant in the terracotta turban, small by the trough. No third person.", []),
 "SH_S5_03": (["DV_v01", "GM_v01"], ROAD, "Same tiled mud-brick house with the plain wooden door and the low plinth step of the village road reference; no carved doorway and no stone stairs.", []),
 "SH_S9_03": ([], CATTLE, "Close insert filling the frame: only the stone rim of the trough in the foreground, shallow muddy water with a cow's muzzle at the left edge, and the brass gadva with vetiver roots on the rim at right. No houses and no sky.", []),
 "SH_S9_04": (["GM_v01"], CATTLE, "Medium close-up of the slim young ascetic with the same narrow face and short hair as the reference sheet, head in sheet proportions, speaking calmly with one palm open upward.", []),
 "SH_S9_06": (["GM_v01", "BA_v01", "DK_v01"], CATTLE, "Camera behind the two men: their backs and turbans frame the left and right edges, and the young ascetic seated in the middle looks up at their faces, his open hand held toward them.", []),
 "SH_S9_10": (["GM_v01", "BA_v01", "DK_v01"], CATTLE, "The young ascetic is the adult from the reference sheet with the open frayed grey-white vest and white waist cloth, running in full side view. Bankatlal and Damodarpant half-kneel by the trough, the brass gadva set on the ground beside them.", []),
 "SH_S3_03": (["BA_v01", "DK_v01"], ROAD, "Bankatlal turns his head toward Damodarpant, who looks back at him, the two facing each other in profile across the frame.", []),
}
out = []
for sid, (chars, place, add, _) in FIX.items():
    j = dict(jobs[sid])
    p = re.sub(r" \((?!short|cream|terracotta|shaved|the calm|Bankatlal|Damodarpant|Devidas)[^)]*\)", "", j["prompt"])   # stray story notes
    m = re.search(r"(Use the attached characters exactly as in their reference sheets: )(.*?)(; same faces|, same faces|; same)", p)
    if m:
        parts = [x for x in re.split(r"(?<=\)); ", m.group(2)) if any(c in x for c in chars)]
        p = p[:m.start(2)] + "; ".join(parts) + p[m.end(2):] if parts else p[:m.start()] + p[m.end():].lstrip("; ")
    if not chars:
        p = p.replace("Show only the attached characters and no other people.", "No people in the picture.")
    p = p.replace(" Full-frame 16:9", " " + add + " Full-frame 16:9", 1)
    j.update(prompt=p, characters=chars, place_search=place, flow_title=f"{sid}__v02", status="TODO", chars_in_prompt=len(p))
    out.append(j)
(ROOT / "canon/drafts/A1_flow_regen_jobs.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
print(len(out), "regen jobs")
bad = [j["shot_id"] for j in out if re.search(r"loincloth|naked|\bbare\b|Maharaj", j["prompt"])]
print("filtered words in:", bad)
print(out[0]["prompt"]); print(); print(out[8]["prompt"])
