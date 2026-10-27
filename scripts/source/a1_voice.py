"""Adhyay 1 voice system (DRAFT voices, NOT VALIDATED until the owner has listened).
  package : writes the text-to-speech job (A1_tts_input.json), a private Kaggle dataset folder and a Kaggle script-kernel folder (GPU, Internet on) under D:/kaggle_upload
  ingest  : reads the finished job's a1_voice.zip (or its folder), verifies every wav against the manifest hash, MEASURES each clip's real duration, writes
            canon/audio/A1_voice_measured.json (committed) and the owner's listening sheet; the wavs go to artifacts/audio/a1/ (git-ignored)
Then:  python scripts/source/a1_audio.py build --run <split run> --measured canon/audio/A1_voice_measured.json   (replaces the ESTIMATED durations with measured ones)
  python scripts/source/a1_voice.py package --plan canon/audio/A1_audio_plan.json
  python scripts/source/a1_voice.py ingest --zip D:/kaggle_upload/a1_voice_out/a1_voice.zip"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import shutil
import sys
import wave
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
_spec = importlib.util.spec_from_file_location("a1_voices", ROOT / "scripts" / "source" / "a1_voices.py")
voices = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(voices)
KAGGLE = Path("D:/kaggle_upload")
OWNER = "satviksangamkar54321"
DATASET, KERNEL = "granthstudio-a1-tts-input", "granthstudio-a1-tts"


def sha256_file(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def wav_seconds(p: Path) -> float:
    with wave.open(str(p), "rb") as w:
        return w.getnframes() / float(w.getframerate())


def package(plan_path: Path, out: Path = KAGGLE) -> dict:
    plan = json.loads(plan_path.read_text(encoding="utf-8"))
    spec = voices.build_input(plan)
    ds, kd = out / "a1_tts_dataset", out / "kernel_a1_tts"
    for d in (ds, kd):
        shutil.rmtree(d, ignore_errors=True)
        d.mkdir(parents=True)
    (ds / "A1_tts_input.json").write_text(json.dumps(spec, ensure_ascii=False, indent=1), encoding="utf-8")
    (ds / "dataset-metadata.json").write_text(json.dumps({"title": DATASET, "id": f"{OWNER}/{DATASET}", "licenses": [{"name": "CC0-1.0"}]}, indent=2), encoding="utf-8")
    shutil.copy(ROOT / "scripts" / "audio" / "a1_tts_run.py", kd / "a1_tts_run.py")
    (kd / "kernel-metadata.json").write_text(json.dumps({"id": f"{OWNER}/{KERNEL}", "title": KERNEL, "code_file": "a1_tts_run.py", "language": "python", "kernel_type": "script",
                                                         "is_private": True, "enable_gpu": True, "enable_tpu": False, "enable_internet": True,
                                                         "dataset_sources": [f"{OWNER}/{DATASET}"], "competition_sources": [], "kernel_sources": [], "model_sources": []}, indent=2), encoding="utf-8")
    return {"jobs": len(spec["jobs"]), "dataset_dir": str(ds), "kernel_dir": str(kd), "input_sha256": sha256_file(ds / "A1_tts_input.json")}


def ingest(src: Path, work: Path, out_json: Path, sheet: Path, audio_dir: Path, plan_path: Path = ROOT / "canon" / "audio" / "A1_audio_plan.json") -> dict:
    """Verify, measure, write. Never trusts the job's own 'seconds': they are re-measured from the wav files."""
    folder = work
    shutil.rmtree(folder, ignore_errors=True)
    folder.mkdir(parents=True)
    if src.is_dir():
        shutil.copytree(src, folder, dirs_exist_ok=True)
    else:
        with zipfile.ZipFile(src) as z:
            for n in z.namelist():                                           # refuse path tricks in the archive
                if n.startswith("/") or ".." in Path(n).parts:
                    raise SystemExit(f"unsafe path in the archive: {n}")
            z.extractall(folder)
    man = json.loads((folder / "tts_manifest.json").read_text(encoding="utf-8"))
    rows, problems = {}, []
    expected = {j["id"] for j in voices.build_jobs(json.loads(plan_path.read_text(encoding="utf-8")))}
    got = {r["id"] for r in man["lines"]}
    problems += [f"{i}: missing from the job manifest" for i in sorted(expected - got)] + [f"{i}: not an expected job" for i in sorted(got - expected)]
    for r in man["lines"]:
        if not r["ok"]:
            problems.append(f"{r['id']}: the job failed ({r.get('error')})")
            continue
        p = (folder / r["wav"]).resolve()
        if folder.resolve() not in p.parents:
            problems.append(f"{r['id']}: the wav path leaves the job folder")
            continue
        if not p.exists() or sha256_file(p) != r["wav_sha256"]:
            problems.append(f"{r['id']}: the wav is missing or does not match the manifest hash")
            continue
        secs = wav_seconds(p)
        if secs < 0.3 or secs > 60:
            problems.append(f"{r['id']}: implausible duration {secs:.2f} s")
        rows[r["id"]] = {"lang": r["lang"], "voice": r["voice"], "speaker": r["speaker"], "seconds": round(secs, 3), "wav_sha256": r["wav_sha256"], "text": r["text"]}
    lines = {}
    for rid, r in rows.items():
        lid = rid.rsplit(".", 1)[0]
        lines.setdefault(lid, {})[r["lang"]] = r["seconds"]
    if problems:                                                         # fail closed: publish nothing from a bad job
        return {"clips": len(rows), "problems": problems, "lines_with_both_languages": 0}
    measured = {"status": "MEASURED from generated speech (DRAFT voices, NOT VALIDATED until the owner has listened)", "model": man.get("model"), "model_commit": man.get("model_commit"),
                "sampling_rate": man.get("sampling_rate"), "split_sha256": man.get("split_sha256"), "problems": problems, "clips": rows, "lines": lines}
    out_json.write_text(json.dumps(measured, ensure_ascii=False, indent=1), encoding="utf-8")
    audio_dir.mkdir(parents=True, exist_ok=True)
    for r in man["lines"]:
        if r["id"] in rows:
            dst = audio_dir / r["wav"]
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy(folder / r["wav"], dst)
    L = ["# Adhyay 1 voices: listening sheet (DRAFT, NOT VALIDATED)", "",
         f"Model `{man.get('model')}`. {len(rows)} clips generated; durations below are MEASURED from the audio. Files: `{audio_dir}`. Listen to each clip and mark what to change "
         "(the voice description in `scripts/source/a1_voices.py`, or the text). Hindi is a draft adaptation.", "", f"Problems: {len(problems)}" + ("".join(f"\n- {p}" for p in problems) if problems else ""), "",
         "| Line | Voice | Marathi file | s | Hindi file | s |", "|---|---|---|---|---|---|"]
    for lid in sorted(lines, key=lambda x: (int(x.split("-")[0][1:]), int(x.split("-L")[1]))):
        mr, hi = rows.get(f"{lid}.mr"), rows.get(f"{lid}.hi")
        L.append(f"| {lid} | {(mr or hi)['voice']} ({(mr or {}).get('speaker', '-')}/{(hi or {}).get('speaker', '-')}) | wav/mr/{lid}.mr.wav | {(mr or {}).get('seconds', '-')} | wav/hi/{lid}.hi.wav | {(hi or {}).get('seconds', '-')} |")
    sheet.write_text("\n".join(L) + "\n", encoding="utf-8")
    return {"clips": len(rows), "problems": problems, "lines_with_both_languages": sum(1 for v in lines.values() if "mr" in v and "hi" in v)}


def balance_gain_db(clip, target_dbfs: float, max_db: float = 10.0) -> float:
    """Gain (dB) that brings a clip's ACTIVE speech (10 ms frames above -40 dBFS) to the target RMS level, limited to +-max_db."""
    import numpy as np
    x = clip.astype(np.float64) / 32768.0
    fr = x[: len(x) // 480 * 480].reshape(-1, 480)
    act = np.sqrt((fr ** 2).mean(axis=1)) > 0.01
    if not act.any():
        return 0.0
    rms_db = 20 * np.log10(np.sqrt((fr[act] ** 2).mean()))
    return float(max(-max_db, min(max_db, target_dbfs - rms_db)))


def mix(lang: str, timing: dict, audio_dir: Path, out_wav: Path, rate: int = 44100, target_dbfs: float | None = None) -> dict:
    """The film's audio for one language: every core line placed at its measured beat start inside its scene; scenes follow each other at 6 s per planned shot (the picture length), so the
    Marathi and Hindi tracks are exactly as long as the picture and play in sync. Mono 16-bit, one clip never overlaps another (a beat window is the LONGER language)."""
    import numpy as np
    total = int(round(timing["planned_picture_s"] * rate))
    track = np.zeros(total + rate, dtype=np.int32)
    t0, placed, index = 0.0, 0, []
    for sc in timing["scenes"]:
        end = int(round((t0 + sc["planned_shots"] * 6) * rate))
        busy = []
        for b in sc["beats"]:
            p = audio_dir / "wav" / lang / f"{b['line']}.{lang}.wav"
            with wave.open(str(p), "rb") as w:
                if w.getframerate() != rate or w.getnchannels() != 1 or w.getsampwidth() != 2:
                    raise SystemExit(f"{p.name}: expected mono 16-bit {rate} Hz")
                clip = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.int32)
            gain = balance_gain_db(clip, target_dbfs) if target_dbfs is not None else 0.0          # equal speech loudness for every voice (narrator and characters)
            if gain:
                clip = np.round(clip * 10 ** (gain / 20)).astype(np.int32)
            off = int(round((t0 + b["start_s"]) * rate))
            if off + len(clip) > end or off + len(clip) > total:
                raise SystemExit(f"{b['line']}: the clip runs past the end of its scene")
            if any(off < e and s0 < off + len(clip) for s0, e in busy):
                raise SystemExit(f"{b['line']}: the clip overlaps an earlier one")
            busy.append((off, off + len(clip)))
            track[off:off + len(clip)] += clip
            placed += 1
            index.append({"line": b["line"], "scene": sc["scene"], "voice": b["voice"], "at_s": round(t0 + b["start_s"], 2), "seconds": round(len(clip) / rate, 2), "gain_db": round(gain, 2)})
        t0 += sc["planned_shots"] * 6
    track = track[:total]
    peak = int(np.max(np.abs(track))) or 1
    out = (track * (0.89 * 32767 / peak)).astype(np.int16)                      # peak at about -1 dBFS
    with wave.open(str(out_wav), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(rate)
        w.writeframes(out.tobytes())
    return {"lang": lang, "lines_placed": placed, "seconds": round(total / rate, 2), "index": index}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("package")
    p.add_argument("--plan", default=str(ROOT / "canon" / "audio" / "A1_audio_plan.json"))
    q = sub.add_parser("ingest")
    q.add_argument("--zip", required=True)
    m = sub.add_parser("mix", help="the full film audio per language, in sync, from the measured timing plan")
    m.add_argument("--timing", default=str(ROOT / "canon" / "audio" / "A1_timing_plan.json"))
    m.add_argument("--audio-dir", default=str(ROOT / "artifacts" / "audio" / "a1"))
    m.add_argument("--target-dbfs", type=float, default=None, help="balance every clip's active speech to this RMS level (e.g. -22) so narration and characters sit at one loudness")
    a = ap.parse_args()
    if a.cmd == "package":
        print(json.dumps(package(Path(a.plan)), indent=1))
        return 0
    if a.cmd == "mix":
        import subprocess
        timing = json.loads(Path(a.timing).read_text(encoding="utf-8"))
        ad = Path(a.audio_dir)
        for lang, name in (("mr", "marathi"), ("hi", "hindi")):
            wav = ad / f"A1_full_{name}.wav"
            r = mix(lang, timing, ad, wav, target_dbfs=a.target_dbfs)
            subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", str(wav), "-codec:a", "libmp3lame", "-b:a", "96k", str(wav.with_suffix(".mp3"))], check=True)
            (ad / f"A1_full_{name}_index.json").write_text(json.dumps(r, ensure_ascii=False, indent=1), encoding="utf-8")
            print(f"{name}: {r['lines_placed']} lines, {r['seconds']} s -> {wav.with_suffix('.mp3')}")
        return 0
    res = ingest(Path(a.zip), KAGGLE / "a1_voice_work", ROOT / "canon" / "audio" / "A1_voice_measured.json", ROOT / "docs" / "pilot" / "A1_voice_listening_sheet.md", ROOT / "artifacts" / "audio" / "a1")
    print(json.dumps(res, indent=1))
    return 0 if not res["problems"] else 1


if __name__ == "__main__":
    sys.exit(main())
