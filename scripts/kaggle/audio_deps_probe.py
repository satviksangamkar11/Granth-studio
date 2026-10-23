"""Environment probe for the pilot's audio stack (no model download, no token, no network): which packages import, which versions, is CUDA usable.

  python scripts/kaggle/audio_deps_probe.py [--json FILE]

It only reports; it never installs. Missing packages are listed with the reason, so a Kaggle session can decide what to pip-install (pins come from each model card after access is granted).
"""
from __future__ import annotations

import argparse
import importlib
import importlib.metadata
import json
import sys

PACKAGES = {"torch": "torch", "torchaudio": "torchaudio", "transformers": "transformers", "onnxruntime": "onnxruntime", "soundfile": "soundfile", "numpy": "numpy",
            "huggingface_hub": "huggingface_hub", "f5_tts": "f5-tts", "IndicTransToolkit": "IndicTransToolkit", "sentencepiece": "sentencepiece", "librosa": "librosa"}


def probe(packages: dict[str, str] = PACKAGES, importer=importlib.import_module, version=importlib.metadata.version) -> dict:
    report: dict = {"python": sys.version.split()[0], "packages": {}, "missing": []}
    for module, dist in packages.items():
        try:
            importer(module)
        except Exception as exc:                      # any import failure (missing, broken binary) is reported, never raised
            report["packages"][module] = {"ok": False, "error": f"{type(exc).__name__}: {str(exc)[:120]}"}
            report["missing"].append(module)
            continue
        try:
            number = version(dist)
        except Exception:
            number = None
        report["packages"][module] = {"ok": True, "version": number}
    try:
        torch = importer("torch")
        report["cuda"] = {"available": bool(torch.cuda.is_available()), "devices": [torch.cuda.get_device_name(i) for i in range(torch.cuda.device_count())]}
    except Exception:
        report["cuda"] = {"available": False, "devices": []}
    return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--json")
    args = parser.parse_args(argv)
    report = probe()
    text = json.dumps(report, indent=2)
    if args.json:
        open(args.json, "w", encoding="utf-8").write(text)
    print(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
