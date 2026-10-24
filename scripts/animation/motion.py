"""Command-line entry for the code-driven camera motion (the code lives in src/granthstudio/motion.py since R3, docs/ARCHITECTURE_V3_2_PROPOSAL.md).

  python scripts/animation/motion.py render SPEC.json OUT.mp4
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))
from granthstudio.motion import *  # noqa: E402,F401,F403
from granthstudio.motion import main  # noqa: E402

if __name__ == "__main__":
    sys.exit(main())
