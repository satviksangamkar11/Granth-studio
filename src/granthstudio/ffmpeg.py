"""FFmpeg and ffprobe adapter: probing, duration validation, Tier 0 motion clips and language assembly.

Commands are argument lists (no shell). FFmpeg is available on this machine; the tests exercise it
with synthetic one-second clips only.
"""

from __future__ import annotations

import json
import math
import shutil
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path

from .errors import IntegrationUnavailable, TaskFailed


@dataclass(frozen=True)
class Probe:
    duration_s: float
    video_codec: str | None
    width: int | None
    height: int | None
    has_audio: bool
    video_duration_s: float | None = None


def _tool(name: str) -> str:
    found = shutil.which(name)
    if not found:
        raise IntegrationUnavailable(f"{name} not found on PATH")
    return found


MEDIA_TIMEOUT_S = 300


def _run(command: list[str]) -> subprocess.CompletedProcess[str]:
    try:
        result = subprocess.run(command, capture_output=True, text=True, check=False, timeout=MEDIA_TIMEOUT_S)
    except subprocess.TimeoutExpired as exc:
        raise TaskFailed(f"{Path(command[0]).name} exceeded {MEDIA_TIMEOUT_S} s and was stopped") from exc
    if result.returncode != 0:
        raise TaskFailed(f"{Path(command[0]).name} failed: {result.stderr.strip()[-500:]}")
    return result


def probe(path: Path) -> Probe:
    output = _run(
        [_tool("ffprobe"), "-v", "error", "-print_format", "json", "-show_format", "-show_streams", str(path)]
    ).stdout
    data = json.loads(output)
    streams = data.get("streams", [])
    video = next((s for s in streams if s.get("codec_type") == "video"), None)
    return Probe(
        duration_s=float(data.get("format", {}).get("duration", 0.0)),
        video_codec=video.get("codec_name") if video else None,
        width=video.get("width") if video else None,
        height=video.get("height") if video else None,
        has_audio=any(s.get("codec_type") == "audio" for s in streams),
        video_duration_s=float(video["duration"]) if video and video.get("duration") else None,
    )


def validate_video(path: Path, expected_duration_s: float, tolerance_s: float = 0.05, expected_codec: str = "h264", require_audio: bool = False) -> list[str]:
    if not path.is_file():
        return [f"{path.name}: missing"]
    info = probe(path)
    problems: list[str] = []
    if info.video_codec is None:
        problems.append(f"{path.name}: no video stream")
    elif info.video_codec != expected_codec:
        problems.append(f"{path.name}: codec {info.video_codec} != {expected_codec}")
    if require_audio and not info.has_audio:
        problems.append(f"{path.name}: no audio stream")
    if not math.isfinite(info.duration_s) or abs(info.duration_s - expected_duration_s) > tolerance_s:
        problems.append(f"{path.name}: duration {info.duration_s:.3f}s != {expected_duration_s:.3f}s")
    if not problems:
        decode(path)
    return problems


def still_motion_clip(image: Path, out: Path, duration_s: float, fps: int = 24, size: tuple[int, int] = (1280, 720)) -> None:
    if duration_s <= 0:
        raise ValueError("duration must be positive")
    frames = round(duration_s * fps)
    width, height = size
    video_filter = (
        f"zoompan=z='min(zoom+0.0008,1.1)':d={frames}"
        f":x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s={width}x{height}:fps={fps},format=yuv420p"
    )
    _run(
        [
            _tool("ffmpeg"), "-y", "-loglevel", "error", "-loop", "1", "-i", str(image),
            "-vf", video_filter, "-frames:v", str(frames), "-t", f"{duration_s:.3f}",
            "-c:v", "libx264", "-threads", "1", "-pix_fmt", "yuv420p", str(out),
        ]
    )


def assemble(clips: list[Path], out: Path, audio: Path | None = None) -> None:
    if not clips:
        raise TaskFailed("no clips to assemble")
    if audio is not None:
        duration = sum(probe(clip).duration_s for clip in clips)
        audio_duration = validate_audio(audio)
        if abs(duration - audio_duration) > 1 / 24:
            raise TaskFailed("audio and editorial video durations differ; refusing speech truncation")
    with tempfile.TemporaryDirectory() as scratch:
        listing = Path(scratch) / "clips.txt"
        escaped = [clip.resolve().as_posix().replace("'", "'\\''") for clip in clips]
        listing.write_text("".join(f"file '{name}'\n" for name in escaped), encoding="utf-8")
        command = [_tool("ffmpeg"), "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", str(listing)]
        if audio is not None:
            command += ["-i", str(audio), "-map", "0:v:0", "-map", "1:a:0", "-c:a", "aac"]
        command += ["-c:v", "libx264", "-threads", "1", "-pix_fmt", "yuv420p", str(out)]
        _run(command)


def decode(path: Path) -> None:
    _run([_tool("ffmpeg"), "-v", "error", "-xerror", "-i", str(path), "-map", "0:v?", "-map", "0:a?", "-f", "null", "-"])


def validate_audio(path: Path) -> float:
    info = probe(path)
    if not info.has_audio or info.video_codec is not None or not math.isfinite(info.duration_s) or info.duration_s <= 0:
        raise TaskFailed(f"{path.name}: expected finite, positive audio-only media")
    decode(path)
    return info.duration_s


def hold_clip(clip: Path, out: Path, duration_s: float) -> None:
    original = probe(clip).duration_s
    if duration_s + 1 / 24 < original:
        raise TaskFailed("editorial coverage must not cut the primary action")
    _run([_tool("ffmpeg"), "-y", "-v", "error", "-i", str(clip), "-vf",
          f"tpad=stop_mode=clone:stop_duration={max(0, duration_s-original):.6f}",
          "-t", f"{duration_s:.6f}", "-an", "-c:v", "libx264", "-threads", "1", "-pix_fmt", "yuv420p", str(out)])


def assemble_audio(segments: list[tuple[Path | None, float]], out: Path) -> None:
    if not segments:
        raise TaskFailed("no audio segments")
    command = [_tool("ffmpeg"), "-y", "-v", "error"]
    filters = []
    for i, (path, duration) in enumerate(segments):
        if duration <= 0:
            raise TaskFailed("audio segment duration must be positive")
        if path is None:
            command += ["-f", "lavfi", "-t", f"{duration:.6f}", "-i", "anullsrc=r=24000:cl=mono"]
        else:
            measured = validate_audio(path)
            if abs(measured-duration) > 0.001:
                raise TaskFailed("speech segment duration differs from measured audio")
            command += ["-i", str(path)]
        filters.append(f"[{i}:a]aresample=24000,aformat=channel_layouts=mono[a{i}]")
    filters.append("".join(f"[a{i}]" for i in range(len(segments))) + f"concat=n={len(segments)}:v=0:a=1[out]")
    command += ["-filter_complex", ";".join(filters), "-map", "[out]", "-c:a", "pcm_s16le", str(out)]
    _run(command)
