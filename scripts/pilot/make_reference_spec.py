"""Writes docs/pilot/REFERENCE_LIBRARY_SPEC.md: exact Nano Banana prompts for the Adhyay 1-6 reference library, composed from ONE style block so every prompt carries identical wording.

Run: python scripts/pilot/make_reference_spec.py
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

STYLE = ("1950s vintage Indian devotional book illustration, authentic mid-century opaque gouache and egg tempera painting on aged matte ivory cardstock, "
         "soft hand-painted sepia contour linework, chalky matte gouache wash shading, flat hand-brushed tonal planes, warm natural mineral pigments of raw sienna, "
         "burnt umber, warm ochre, terracotta, and muted sage green, subtle paper grain texture, clean traditional graphic composition")
TAIL_CHAR = "plain aged ivory paper background, single figure only, centred, no text, no labels, no signature, no watermark. Square 1024x1024."
TAIL_OBJECT = "plain aged ivory paper background, single object only, centred, no text, no labels, no signature, no watermark. Square 1024x1024."
TAIL_PLACE = "no people, no text, no labels, no signature, no watermark. Square 1024x1024."
SAME_PERSON = "Use the attached image of this same person as the identity and style reference: same face, same age, same build, same illustration style. "
STYLE_ONLY = "Use the attached image only as the style reference (same illustration style, line weight, colours and paper). "

MAHARAJ = ("a young man in the prime of youth with a radiant complexion, strong upper arms and neck and a broad chest, short dark hair, clean-shaven, calm face, "
           "wearing only a plain white loincloth")
MAHARAJ_NO_CLOTH = MAHARAJ.replace(", wearing only a plain white loincloth", "")
BANK = "a young merchant of the 1870s, humble open expression, wearing a white dhoti, a long sage-green coat, a cloth turban and a folded shoulder cloth"

# (heading, file, kind, subject, who)   kind: exists | same (attach the person) | char | place | object
P1 = [
    ("maharaj_seated_front", "maharaj.jpg", "exists", None, None),
    ("maharaj_seated_three_quarter", "maharaj_seated_3q.jpg", "same", "seated cross-legged, body turned three-quarter to the left, calm face turned slightly toward the viewer, eyes lowered to the tip of the nose", MAHARAJ),
    ("maharaj_seated_profile", "maharaj_seated_profile.jpg", "same", "seated cross-legged in strict side profile facing left, eyes lowered, hands resting in the lap", MAHARAJ),
    ("maharaj_seated_back", "maharaj_seated_back.jpg", "same", "seen from behind, seated cross-legged, back and shoulders visible, head slightly bowed", MAHARAJ),
    ("maharaj_seated_eating", "maharaj_seated_eating.jpg", "same", "seated cross-legged on the ground, lifting a few grains of rice from a leaf plate on the ground toward his mouth, calm unhurried expression, a small hand-made clay pipe in his other hand", MAHARAJ),
    ("maharaj_face_calm", "maharaj_face_calm.jpg", "same", "close-up head and shoulders portrait, serene face, eyes lowered to the tip of the nose, radiant complexion", MAHARAJ),
    ("maharaj_face_smile", "maharaj_face_smile.jpg", "same", "close-up head and shoulders portrait, a gentle laugh, eyes open and bright, radiant complexion", MAHARAJ),
    ("maharaj_walking", "maharaj_walking.jpg", "same", "walking quickly to the right with long strides, as if running like the wind, full body, hair and loincloth moving", MAHARAJ),
    ("bankatlal_standing_front", "bankatlal.jpg", "exists", None, None),
    ("bankatlal_three_quarter", "bankatlal_3q.jpg", "same", "standing, body turned three-quarter to the right, head toward the viewer, hands folded respectfully in front", BANK),
    ("bankatlal_profile", "bankatlal_profile.jpg", "same", "standing in strict side profile facing right, stepping forward humbly, hands folded", BANK),
    ("bankatlal_back", "bankatlal_back.jpg", "same", "seen from behind, standing, turban, coat and shoulder cloth visible", BANK),
    ("bankatlal_seated", "bankatlal_seated.jpg", "same", "seated cross-legged on the ground, hands in his lap, attentive expression", BANK),
    ("bankatlal_walking", "bankatlal_walking.jpg", "same", "walking along a road to the left, full body, relaxed stride", BANK),
    ("devidas", "devidas.jpg", "exists", None, None),
    ("damodarpant_distinct (REDO: the pilot one shares Devidas's body)", "damodarpant.jpg", "char",
     "a village record-keeper of the 1870s, shorter and heavier build than the other men, round face, short grey-flecked moustache and beard, wearing a plain white cloth cap, "
     "a short plain cotton jacket over a dhoti and a folded shoulder cloth, hands clasped in front, standing, head to knees", None),
]
P2 = [
    ("maharaj_pitambar", "maharaj_pitambar.jpg", "same", "seated cross-legged after his bath, wearing a yellow silk pitambar wrapped at the waist and over one shoulder, a garland of flowers and a streak of saffron paste on the forehead, radiant", MAHARAJ_NO_CLOTH),
    ("maharaj_garlanded", "maharaj_garlanded.jpg", "same", "seated cross-legged, many flower garlands around the neck, cool sandal paste on the chest and forehead, a white loincloth, serene", MAHARAJ_NO_CLOTH),
    ("maharaj_padmasana", "maharaj_padmasana.jpg", "same", "seated in padmasana (lotus pose) on a rock, hands on the knees, eyes closed in deep meditation, a white loincloth", MAHARAJ_NO_CLOTH),
    ("bankatlal_in_cart", "bankatlal_cart.jpg", "same", "seated in a simple wooden bullock cart, one hand on the rail, calm expression", BANK),
    ("bhavaniram", "bhavaniram.jpg", "char", "Bankatlal's father, a kind, dignified elderly man of the 1870s with a white moustache, a white turban, a long white coat and a dhoti, standing, hands folded", None),
    ("house_exterior", "loc_bankatlal_house_exterior.jpg", "place", "the front of a prosperous merchant's two-storey house in a Vidarbha village of the 1870s, a heavy wooden front door with a brass lock, a low stone verandah step, a tiled roof, bright daylight", None),
    ("house_interior_seating", "loc_bankatlal_house_seating.jpg", "place", "the seating room of a merchant's house of the 1870s, a low carved wooden seat (pat) and a cushioned seat (gadi) on a clean floor, oil lamps, a doorway", None),
    ("maruti_temple", "loc_shegaon_maruti_temple.jpg", "place", "a grand old village Maruti (Hanuman) temple in Shegaon of the 1870s, a wide stone platform, a pillared front hall, a small spire, a neem tree, bright daylight", None),
    ("prop_chilim", "prop_chilim.jpg", "object", "a small hand-made unfired raw clay chilim (smoking pipe)", None),
    ("prop_gourd", "prop_gourd.jpg", "object", "a dried gourd water vessel (tumba)", None),
    ("prop_gadva", "prop_gadva.jpg", "object", "a brass gadva (small water pot with a wide mouth)", None),
    ("prop_pat", "prop_pat.jpg", "object", "a low carved wooden seat (pat)", None),
    ("prop_leaf_plates", "prop_leaf_plates.jpg", "object", "a small pile of used dry leaf plates (patravali)", None),
]
P3 = [
    ("ramajipant", "ramajipant.jpg", "char", "a very old village elder (Ramajipant Deshmukh) of the 1870s, thin, slightly bent, white moustache, white turban, dhoti and shoulder cloth, a walking stick, calm virtuous face, standing", None),
    ("kashi_gosavi", "kashi_gosavi.jpg", "char", "a wandering gosavi from Kashi: a saffron rag wound on his head, a cloth shoulder bag under his LEFT armpit, wearing only a torn loincloth, a rolled deerskin on his back, standing", None),
    ("janakiram", "janakiram.jpg", "char", "a village goldsmith of the 1870s, hostile suspicious expression, a leather apron over a dhoti, a cloth cap, standing", None),
    ("madhav_elderly", "madhav.jpg", "char", "a frail man past sixty, very weak thin limbs, white stubble, a white cap, dhoti and shawl, standing with a stoop", None),
    ("narsingji", "narsingji.jpg", "char", "a Maratha man of the 1870s, strong build, moustache, a saffron turban, a long coat over a dhoti, standing", None),
    ("vrajbhushan", "vrajbhushan.jpg", "char", "a learned pandit of the 1870s, shaved head with a tuft, sacred thread, a white dhoti and shoulder cloth, a small brass sandhya vessel in hand, standing", None),
    ("khandu_patil", "khandu_patil.jpg", "char", "a generous village headman (patil) of the 1870s, broad moustache, a red turban, a white coat and dhoti, standing, hands on hips", None),
    ("bhaskar_farmer", "bhaskar.jpg", "char", "a village farmer, big strong muscular build, bare chest, a small cloth on his head, a dhoti, an earthen pot balanced on his head, standing", None),
    ("loc_shankar_temple", "loc_shegaon_shankar_temple.jpg", "place", "an old Shiva (Shankar) temple in Shegaon, a paved stone floor at the back, a neem tree nearby, bright daylight", None),
    ("loc_pimpalgaon_forest_temple", "loc_pimpalgaon_forest_temple.jpg", "place", "an old stone Hemadpanti-style Shiva temple deep in a forest at sunset, a small stream in front, an open sanctum with a pindi", None),
    ("loc_field_well", "loc_bankatlal_field_well.jpg", "place", "a village field with a well full of water, dense shade trees, tamarind trees with a wild bee hive, bright monsoon light", None),
    ("loc_sand_bank_dawn", "loc_chandrabhaga_sand_bank.jpg", "place", "a wide river sand bank at dawn, a bright sky, birds flying east, a few distant trees", None),
]
GROUPS = [("P1 - needed for the pilot re-render (do these first)", P1), ("P2 - recurring in Adhyay 2-6", P2),
          ("P3 - one-off characters and locations (make when that adhyay is scheduled)", P3)]

INTRO = """# Reference library spec (Adhyay 1-6) - exact Nano Banana prompts

Generated by `scripts/pilot/make_reference_spec.py` from the Adhyay 1-6 research (frozen canon), 2026-10-24. Status: PROPOSED. The owner generates, the assistant ingests. Every look the frozen text does not state is an ARTISTIC choice for the owner to approve. Nothing here is canon or validated.

## How to use
1. One Nano Banana session per person. Attach that person's existing image from `assets/pilot_refs/set_v1/` first, so the face and style stay the same across all views. For a new person or a place or an object, attach any existing image only as the style reference.
2. Paste the prompt exactly. Square 1024x1024, one subject per image, no logo, watermark or text (crop it out if the app adds one).
3. Save under the file name shown in `D:\\aai work\\pilot_refs\\set_v2\\`, then tell me. I hash the files, write `manifest.json` (view, pose and costume per image), run Codex and the tests, then use them.
4. Do P1 first; the pilot re-render needs only P1. P2 and P3 can wait.

## What the Adhyay 1-6 text needs
- Only **Gajanan Maharaj** and **Bankatlal** recur across all six adhyays, so only they get full view sets. Everyone else is one image. Bhavaniram also recurs in A2-A3.
- Gajanan is almost always **seated** (road, plate, pat, padmasana, rock, sand, cart, palanquin). Standing or walking is rare but strong ("like the wind"). A **back view** is needed (A6 ovi 110). Costume variants: loincloth (default), pitambar after the bath (A2), garlands and sandal paste (A2, A4, A5).
- At most about four named people appear together; crowds are background. Interiors needed: Bankatlal's house (A2-A6) and temples.
- Stated by the text: Gajanan is in the prime of youth, radiant complexion, strong upper arms and neck, broad chest, nose-tip gaze, calm, almost naked (owner ruling: minimal loincloth, modest framing). Bankatlal is a young man (A2 ovi 13) and an Agarwal merchant. Hair, beard, skin tone, height and most clothing are NOT stated, so they are artistic.

## Distinctness rule
No two people may share a body, pose or costume template (the pilot's Devidas and Damodarpant twin problem). The prompts give each person a different build or garment.
"""


def prompt(kind: str, subject: str, who: str | None) -> str:
    if kind == "same":
        return f"{SAME_PERSON}{STYLE}. {who}, {subject}, {TAIL_CHAR}"
    tail = {"char": TAIL_CHAR, "place": TAIL_PLACE, "object": TAIL_OBJECT}[kind]
    return f"{STYLE_ONLY}{STYLE}. {subject}, {tail}"


def build() -> str:
    out = [INTRO]
    for title, items in GROUPS:
        out.append(f"\n## {title}\n")
        for name, fname, kind, subject, who in items:
            out.append(f"### {name} -> `{fname}`\n")
            if kind == "exists":
                out.append(f"Already exists in `assets/pilot_refs/set_v1/{fname}`. Keep it; copy it into set_v2 under the same name.\n")
            else:
                out.append("```text\n" + prompt(kind, subject, who) + "\n```\n")
    return "\n".join(out)


if __name__ == "__main__":
    target = ROOT / "docs" / "pilot" / "REFERENCE_LIBRARY_SPEC.md"
    target.write_text(build(), encoding="utf-8")
    print(target, build().count("```text"), "prompts")
