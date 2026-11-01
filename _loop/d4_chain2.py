import subprocess
from pathlib import Path
R = Path(r"D:ai work\granthstudio")
for n in ("wpD4b", "wpD4c"):
    r = subprocess.run(["uv","run","python","scripts/source/fix_loop_stable.py","--job",f"_loop/jobs/research_{n}.json"], cwd=R, capture_output=True, text=True)
    (R/"_loop"/f"research_{n}.run.log").write_text(r.stdout + r.stderr, encoding="utf-8")
    if r.returncode != 0: break
