"""Style exploration with Nano Banana Pro: 3 characters x 4 art styles = 12 images. The identity comes from the owner's approved reference (set_v2); the STYLE comes only from the text.
Uses gemini_test.py helpers (key read from the secrets folder, never printed, scrubbed). Every request is journalled PREPARED -> SENT -> COMPLETED/UNKNOWN; a timeout is recorded
as UNKNOWN and is NOT re-sent automatically (it may have been billed). Usage: python gemini_styles.py --out DIR [--model gemini-3-pro-image]"""
from __future__ import annotations

import argparse
import base64
import hashlib
import importlib.util
import json
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("gemini_test", HERE / "gemini_test.py")
gt = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gt)

CHARACTERS = {
    "maharaj": ("maharaj_youth.webp", "a young ascetic man in the prime of youth, radiant complexion, strong neck and broad chest, short dark hair, clean-shaven, calm eyes lowered to the nose-tip, wearing only a plain white loincloth, seated cross-legged, hands resting on his knees, full body, front view"),
    "bankatlal": ("bankatlal.webp", "a young merchant of the 1870s with a neat moustache and a humble open expression, wearing a terracotta-red turban, a cream knee-length wrap-over coat tied at the side and a white dhoti with a thin red border, standing, hands folded respectfully, full body, three-quarter front view"),
    "devidas": ("devidas.webp", "a devout Brahmin householder with greying temples, a small round forehead mark and a sacred thread across the chest, wearing a white dhoti and a white shoulder cloth with a thin red border, standing calm and dignified, full body, front view"),
}
STYLES = {
    "ravi_varma": ("Raja Ravi Varma calendar-art style (1880s-1900s Indian academic oil painting)",
                   "rich oil painting with soft blended brushwork, warm chiaroscuro lighting, realistic anatomy and drapery folds, glowing jewel-toned colours, gentle luminous halo of light behind the figure, dark warm studio-style background fading to amber"),
    "comic": ("Indian mythological comic-book style (mid-20th-century illustrated story books)",
              "bold clean black ink outlines of even weight, flat saturated opaque colours with simple hard-edged cel shadows, strong readable silhouettes, expressive but simple faces, plain pale yellow background, printed picture-book look"),
    "kalighat": ("Kalighat / Bengal Pattachitra folk painting style",
                 "confident flowing brush contours, flat bold colour fills with a soft wash for rounded volume, minimal shading, simplified large eyes and stylised features, sparse composition with the figure filling the page, plain textured paper background"),
    "cel": ("hand-painted 2D cel-animated feature film style",
            "clean delicate line art with coloured lines, soft cel shading in two tones, expressive animation-ready face, clear silhouette and simple readable shapes, painterly soft watercolour-textured background wash, gentle warm daylight"),
}
STYLES_NEW = {
    "pahari": ("Pahari (Basohli / Kangra) hill-court miniature painting",
               "flat-colour devotional miniature painting, bold colour fields in deep blue, saffron yellow and vermilion red, fine flowing ink contour lines, pale monochrome sky band, simple architectural framing, stylised frontal figure with almond-shaped eyes, gold-leaf accents on textiles, tempera on handmade paper, no shading gradients"),
    "tanjore": ("Thanjavur (Tanjore) gold-and-gesso devotional panel painting",
                "raised white gesso relief on jewellery and ornaments, gold-leaf accents, small inset glass gems, saturated vermilion, emerald and deep blue background, symmetrical frontal composition, arched pillared frame with floral scrollwork, calm serene face, wood-panel texture, flat ornamental surface"),
    "shadow_puppet": ("Karnataka leather shadow-puppet (Togalu Gombeyatta) figure",
                      "translucent cut-hide puppet figure with articulated jointed limbs, punched perforation patterns, vegetable-dyed red, green and yellow hide, dark outlines, flat profile figure, backlit warm glow on a pale screen, no three-dimensional shading"),
    "phad": ("Rajasthani phad scroll painting",
             "painting on cloth with bold dark outlines, flat two-dimensional figure, vegetable-dye reds, ochres, indigo and mustard, dense folk ornamentation, a few small banner flags, visible cloth texture, no perspective depth, no shading"),
    "warli": ("Warli tribal wall-painting style",
              "white rice-paste figure on an earthy mud-brown ground, body built from two triangles and a circle head with a simple dot-and-line face, stick-like limbs, geometric sun circle, freehand naive line, minimal palette of white and ochre, flat surface, no shading"),
    "bengal_wash": ("Bengal School wash painting",
                    "soft translucent sepia and ink washes, misty graded background, delicate brush outlines fading into the wash, muted earth palette of ochre and grey, a single luminous focal figure, calm devotional mood, handmade paper texture, minimal hard edges, no heavy black outline"),
}
STYLES_TEXT = {
    "mid_century": ("mid-century modern limited-animation style",
                    "simplified geometric shapes instead of realistic anatomy, flat blocks of colour slightly offset from the outlines, bold angular stylised shapes, minimal detail, limited warm palette of ochre, teal and brick red, textured paper-like background"),
    "flat_vector": ("flat vector illustration style",
                    "clean flat digital shapes, no textures, no outlines or only a thin consistent outline, no lighting or dimensional shading, minimal simple colours, highly readable composition, simplified rounded faces"),
    "woodcut": ("woodcut / linocut print style",
                "handmade carved-block texture, strong black and white contrast with a single warm ochre colour, thick emphasised carved lines, bold light-and-shadow shapes, rough ink edges, off-white paper"),
    "paper_collage": ("layered paper-cut collage storybook style",
                      "flat figures cut from coloured paper with slightly torn edges, visible paper fibre texture, layered pieces with small drop shadows, jointed limbs made of separate paper pieces, simple dot eyes, pop-up storybook feel"),
    "silhouette": ("backlit paper-silhouette cutout style",
                   "delicate hand-cut black paper silhouette of the figure with fine cut-out lace-like details in the clothing, glowing warm amber and orange backlit ground, flat graphic stage, no facial shading"),
    "picture_book": ("painted picture-book watercolour and ink style",
                     "soft watercolour washes with loose ink line drawing, gentle granulated pigment on textured paper, warm earthy palette, tender expressive faces, hand-painted children's picture-book illustration"),
}
TASK_TEXT = ("Draw one single full-body figure, centred, on a plain background, square image, no text, no labels, no watermark, no border. Subject: {subject}. Art style: {style_name}: {style_desc}.")
TASK = ("Use the attached image ONLY to know who this person is (face, age, build and the costume pieces). Ignore its painting style completely and redraw the person from scratch in the style below. "
        "One single figure only, centred, plain background, square image, no text, no labels, no watermark, no border. Subject: {subject}. Art style: {style_name}: {style_desc}.")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--model", default="gemini-3-pro-image")
    ap.add_argument("--set", choices=("first", "new", "text"), default="first")
    a = ap.parse_args()
    styles = {"first": STYLES, "new": STYLES_NEW, "text": STYLES_TEXT}[a.set]
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    journal = out / "journal.json"
    rows = []

    def save(row):
        journal.write_text(gt.scrub(json.dumps(rows, indent=2)), encoding="utf-8")

    for sk, (sname, sdesc) in styles.items():
        for ck, (ref, subject) in CHARACTERS.items():
            row = {"style": sk, "character": ck, "state": "PREPARED", "model": a.model}
            rows.append(row)
            save(row)
            if a.set == "text":
                parts = [{"text": TASK_TEXT.format(subject=subject, style_name=sname, style_desc=sdesc)}]        # NO reference image: the subject text alone
            else:
                text = {"text": TASK.format(subject=subject, style_name=sname, style_desc=sdesc)}
                image = gt.b64_image(gt.V2 / ref)
                parts = [text, image] if a.set == "first" else [image, text]      # new set: reference image first, then the instruction (Google's prompting guide order)
            body = {"contents": [{"parts": parts}], "generationConfig": {"responseModalities": ["IMAGE"], "imageConfig": {"aspectRatio": "1:1"}}}
            row["state"] = "SENT"
            save(row)
            t0 = time.time()
            status, data = gt.call(f"/v1beta/models/{a.model}:generateContent", body, timeout=240)
            row["wall_s"], row["http"] = round(time.time() - t0, 1), status
            if status == 0:
                row["state"] = "UNKNOWN"                      # the request may have completed and been billed: not re-sent automatically
                row["error"] = data.get("error")
            elif status != 200:
                row["state"], row["error"] = "FAILED", data.get("error")
            else:
                img = None
                for cand in data.get("candidates", []):
                    for part in cand.get("content", {}).get("parts", []):
                        inline = part.get("inlineData") or part.get("inline_data")
                        if inline and inline.get("data"):
                            img = base64.b64decode(inline["data"])
                if img:
                    f = out / f"{sk}__{ck}.png"
                    f.write_bytes(img)
                    row.update(state="COMPLETED", file=f.name, sha256=hashlib.sha256(img).hexdigest(), usage=data.get("usageMetadata", {}).get("totalTokenCount"))
                else:
                    row["state"], row["error"] = "FAILED", "no image: " + json.dumps(data)[:200]
            save(row)
            print(gt.scrub(json.dumps({k: row[k] for k in ("style", "character", "state", "wall_s") if k in row})), flush=True)
    return 0 if all(r["state"] == "COMPLETED" for r in rows) else 1


if __name__ == "__main__":
    raise SystemExit(main())
