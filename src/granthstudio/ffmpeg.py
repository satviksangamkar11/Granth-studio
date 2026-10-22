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
from fractions import Fraction
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
    audio_duration_s: float | None = None
    audio_sample_rate: int | None = None


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


def _stream_duration(stream: dict | None) -> float | None:
    if stream is None:
        return None
    try:
        if stream.get("duration_ts") is not None and stream.get("time_base"):
            return float(int(stream["duration_ts"]) * Fraction(stream["time_base"]))
        return float(stream["duration"]) if stream.get("duration") else None
    except (TypeError, ValueError, ZeroDivisionError):
        return None


def audio_video_tolerance(audio: Probe, videos: list[Probe] = ()) -> float:
    """Two audio samples; allow 1 ms metadata quantization only when stream timing is absent."""
    sample = 1 / audio.audio_sample_rate if audio.audio_sample_rate else 0.001
    metadata = 0.001 if audio.audio_duration_s is None or any(v.video_duration_s is None for v in videos) else 1e-6
    return 2 * max(sample, metadata)


def probe(path: Path) -> Probe:
    output = _run(
        [_tool("ffprobe"), "-v", "error", "-print_format", "json", "-show_format", "-show_streams", str(path)]
    ).stdout
    data = json.loads(output)
    streams = data.get("streams", [])
    video = next((s for s in streams if s.get("codec_type") == "video"), None)
    audio = next((s for s in streams if s.get("codec_type") == "audio"), None)
    return Probe(
        duration_s=float(data.get("format", {}).get("duration", 0.0)),
        video_codec=video.get("codec_name") if video else None,
        width=video.get("width") if video else None,
        height=video.get("height") if video else None,
        has_audio=any(s.get("codec_type") == "audio" for s in streams),
        video_duration_s=_stream_duration(video),
        audio_duration_s=_stream_duration(audio),
        audio_sample_rate=int(audio["sample_rate"]) if audio and audio.get("sample_rate") else None,
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
    video_duration = info.video_duration_s if info.video_duration_s is not None else info.duration_s
    if not math.isfinite(video_duration) or abs(video_duration - expected_duration_s) > tolerance_s:
        problems.append(f"{path.name}: duration {video_duration:.3f}s != {expected_duration_s:.3f}s")
    if require_audio and info.has_audio:
        audio_duration = info.audio_duration_s if info.audio_duration_s is not None else info.duration_s
        if not math.isfinite(audio_duration) or abs(audio_duration - video_duration) > audio_video_tolerance(info, [info]):
            problems.append(f"{path.name}: measured audio/video stream durations differ")
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
        videos = [probe(clip) for clip in clips]
        duration = sum(v.video_duration_s if v.video_duration_s is not None else v.duration_s for v in videos)
        audio_duration = validate_audio(audio)
        if abs(duration - audio_duration) > audio_video_tolerance(probe(audio), videos):
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
    duration = info.audio_duration_s if info.audio_duration_s is not None else info.duration_s
    if not info.has_audio or info.video_codec is not None or not math.isfinite(duration) or duration <= 0:
        raise TaskFailed(f"{path.name}: expected finite, positive audio-only media")
    decode(path)
    return duration


def hold_clip(clip: Path, out: Path, duration_s: float) -> None:
    info = probe(clip)
    original = info.video_duration_s if info.video_duration_s is not None else info.duration_s
    if duration_s + 1e-6 < original:
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
