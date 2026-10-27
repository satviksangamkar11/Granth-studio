"""Read-only audit of D:/aai work/flow_outputs/adhyay_NN (default 01). Writes final_review/AUDIT_LOCAL.md. Never changes or deletes any image.
Checks: every planned shot has a file; per-version png + 2K jpg pair, size 2752x1536, not a duplicate of another shot; flow_log.jsonl lines vs files on disk;
progress lines DONE with a missing file; loose files in the flow_outputs root; stray files in shots/; which version is the 'best' (highest vNN) per shot. Needs canon/drafts/A<N>_flow_shot_jobs.json."""
import hashlib, json, re, sys
from collections import defaultdict
from pathlib import Path
from PIL import Image

N = sys.argv[1] if len(sys.argv) > 1 else "01"
ROOT = Path("D:/aai work/flow_outputs")
A = ROOT / f"adhyay_{N}"
SH = A / "shots"
JOBS = Path(f"D:/aai work/granthstudio/canon/drafts/A{int(N)}_flow_shot_jobs.json")
if not JOBS.exists():
    sys.exit(f"no job file {JOBS}: this audit needs the chapter's shot job list")
out = []
def say(s=""): out.append(s)

planned = [j["shot_id"] for j in json.loads(JOBS.read_text(encoding="utf-8"))]
files = defaultdict(dict)   # shot -> version -> {png, jpg}
stray = []
for f in sorted(SH.iterdir()):
    m = re.match(r"(SH_S\d+_\d+)__candidate_(v\d+)(__2K_source)?\.(png|jpg)$", f.name)
    if m:
        files[m.group(1)].setdefault(m.group(2), {})["jpg" if m.group(3) else "png"] = f
    else:
        stray.append(f.name)
say(f"# Local audit adhyay_{N}")
say(f"planned shots {len(planned)}; shots with files {len([s for s in planned if s in files])}")
say("")
say("## Shots: versions, files, size, best")
bad = []
hashes = defaultdict(list)
for s in planned:
    if s not in files:
        say(f"- {s}: MISSING"); bad.append(s); continue
    vs = sorted(files[s])
    notes = []
    for v in vs:
        d = files[s][v]
        if "png" not in d or "jpg" not in d: notes.append(f"{v}: missing {'png' if 'png' not in d else 'jpg'}"); continue
        if Image.open(d["png"]).size != (2752, 1536): notes.append(f"{v}: png size {Image.open(d['png']).size}")
        if Image.open(d["jpg"]).size != (2752, 1536): notes.append(f"{v}: jpg size {Image.open(d['jpg']).size}")
        hashes[hashlib.sha256(d["jpg"].read_bytes()).hexdigest()].append(f"{s}/{v}")
    say(f"- {s}: versions {', '.join(vs)}; best {vs[-1]}" + (f"; PROBLEMS: {'; '.join(notes)}" if notes else ""))
    if notes: bad.append(s)
say("")
say("## Duplicate images (same bytes under different shot/version)")
dups = [v for v in hashes.values() if len(v) > 1]
say("none" if not dups else "\n".join(f"- {', '.join(v)}" for v in dups))
say("")
say("## flow_log.jsonl vs disk")
logged = set(); missing = []
for l in (A / "flow_log.jsonl").read_text(encoding="utf-8").splitlines():
    try: r = json.loads(l)
    except Exception: continue
    for k in ("file", "source_jpg"):
        if r.get(k):
            pp = Path(r[k]) if Path(r[k]).is_absolute() else A / r[k]
            logged.add(pp.name)
            if not pp.exists(): missing.append(f"{r.get('image_id')} {k}: {r[k]}")
say("log lines whose file is missing on disk: " + ("none" if not missing else "; ".join(missing)))
unlogged = [f.name for s in files for v in files[s].values() for f in v.values() if f.name not in logged]
say("files on disk not in flow_log: " + ("none" if not unlogged else ", ".join(unlogged)))
say("")
say("## Progress file: DONE lines whose file is missing")
pm = []
for l in (A / "shots_progress.jsonl").read_text(encoding="utf-8").splitlines():
    try: r = json.loads(l)
    except Exception: continue
    f = r.get("file")
    if r.get("status") == "DONE" and f:
        p = Path(f) if Path(f).is_absolute() else A / f
        if not p.exists(): pm.append(f"{r['shot_id']}: {f}")
say("none" if not pm else "\n".join("- " + x for x in pm))
say("")
say("## Loose / stray files")
loose = [f.name for f in ROOT.iterdir() if f.is_file()]
say(f"in {ROOT} root ({len(loose)}): " + (", ".join(loose) if loose else "none"))
say(f"in shots/ not matching the naming ({len(stray)}): " + (", ".join(stray) if stray else "none"))
say("")
say("## Other folders")
for sub in ("references", "layers", "rejected", "final_review"):
    d = A / sub
    say(f"- {sub}: {len(list(d.iterdir())) if d.exists() else 'absent'} entries")
say("")
say(f"RESULT: {'ALL OK' if not bad and not dups and not missing and not pm else 'ISSUES: ' + ', '.join(bad)}")
(A / "final_review").mkdir(exist_ok=True)
(A / "final_review" / "AUDIT_LOCAL.md").write_text("\n".join(out), encoding="utf-8")
print("\n".join(out[:6]), "\n...\n", out[-1])
