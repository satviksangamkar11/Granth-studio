"""Saves the Shri Gajanan Vijay text from hindujagruti.org (21 Adhyay pages) as a WORKING COPY, one JSONL per Adhyay: {adhyay, ovi, printed_no, text}.
The owner's printed PDF stays the authority; this copy is checked against it (compare_pdf.py). Usage: python fetch_hj.py [--out canon/source_hj]"""
import argparse
import hashlib
import html
import json
import re
import time
import urllib.request
from pathlib import Path

PAGES = [764, 763, 762, 761, 760, 759, 758, 757, 756, 755, 753, 752, 746, 745, 744, 743, 742, 741, 740, 739, 738]   # Adhyay 1..21, checked 2026-10-25
BASE = "https://www.hindujagruti.org/hinduism-for-kids-marathi/{}.html"
DIG = str.maketrans("०१२३४५६७८९", "0123456789")
MARK = re.compile(r"॥\s*([०-९]+)\s*॥")


def article_text(raw: str) -> str:
    m = re.search(r"<article.*?</article>", raw, re.S)
    body = m.group(0) if m else raw
    body = re.sub(r"<(script|style).*?</\1>", "", body, flags=re.S)
    body = re.sub(r"<br\s*/?>|</p>|</div>|</h\d>", "\n", body)
    text = html.unescape(re.sub(r"<[^>]+>", "", body))
    return re.sub(r"[ \t\u00a0]+", " ", text)


def split_ovis(text: str):
    """Ovi n ends with its mark ॥n॥ (print drops the hundreds digit after 100). Returns [(seq, printed, text)]; out-of-sequence marks are kept inside the text."""
    out, exp, start = [], 1, 0
    for m in MARK.finditer(text):
        n = int(m.group(1).translate(DIG))
        if n in (exp, exp % 100):
            chunk = text[start:m.start()]
            if exp == 1:                                   # drop the page title / invocation before ovi 1
                chunk = chunk.split("॥ श्रीगणेशाय नमः ॥")[-1]
            out.append((exp, n, " ".join(chunk.split())))
            exp += 1
            start = m.end()
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="D:/aai work/granthstudio/canon/source_hj")
    a = ap.parse_args()
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    summary = []
    for i, page in enumerate(PAGES, 1):
        raw = urllib.request.urlopen(urllib.request.Request(BASE.format(page), headers={"User-Agent": "Mozilla/5.0"}), timeout=60).read().decode("utf-8")
        text = article_text(raw)
        (out / f"adhyay_{i:02d}_raw.txt").write_text(text, encoding="utf-8")
        ovis = split_ovis(text)
        with (out / f"adhyay_{i:02d}.jsonl").open("w", encoding="utf-8") as f:
            for seq, printed, t in ovis:
                f.write(json.dumps({"adhyay": i, "ovi": seq, "printed_no": printed, "text": t}, ensure_ascii=False) + "\n")
        summary.append({"adhyay": i, "page": page, "ovis": len(ovis), "sha256": hashlib.sha256(raw.encode()).hexdigest()})
        print(i, page, len(ovis), flush=True)
        time.sleep(1)
    (out / "SOURCE.json").write_text(json.dumps({"source": "hindujagruti.org (working copy; owner's printed PDF is the authority)",
                                                 "fetched": time.strftime("%Y-%m-%d"), "adhyays": summary, "total_ovis": sum(s["ovis"] for s in summary)}, indent=2, ensure_ascii=False), encoding="utf-8")
    print("total", sum(s["ovis"] for s in summary))


if __name__ == "__main__":
    main()
