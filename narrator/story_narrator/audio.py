"""Join synthesized chunks into one file without losing quality.

* PCM from the provider is joined sample-for-sample into a WAV master (lossless). The MP3
  is encoded once from that master at LAME's best VBR setting.
* If only MP3 is available, chunks are joined with ffmpeg stream copy: the provider's
  MP3 frames are kept as-is, never decoded or re-encoded.
"""
from __future__ import annotations

import json
import shutil
import subprocess
import tempfile
import wave
from pathlib import Path


class AudioError(RuntimeError):
    pass


def ffmpeg_available() -> bool:
    return bool(shutil.which("ffmpeg") and shutil.which("ffprobe"))


def _run(cmd: list[str]) -> str:
    p = subprocess.run(cmd, capture_output=True, text=True)
    if p.returncode != 0:
        raise AudioError(f"{cmd[0]} failed: {p.stderr.strip()[-600:]}")
    return p.stdout


def write_wav(pcm_chunks: list[bytes], path: Path, sample_rate: int, channels: int = 1) -> float:
    """Write 16-bit PCM chunks to a WAV file; returns the duration in seconds."""
    frame = 2 * channels
    frames = 0
    with wave.open(str(path), "wb") as w:
        w.setnchannels(channels)
        w.setsampwidth(2)
        w.setframerate(sample_rate)
        for chunk in pcm_chunks:
            usable = len(chunk) - len(chunk) % frame  # never write a torn sample
            w.writeframesraw(chunk[:usable])
            frames += usable // frame
    return frames / sample_rate


def encode_mp3(wav_path: Path, mp3_path: Path, vbr_quality: int = 0) -> None:
    _run(["ffmpeg", "-nostdin", "-loglevel", "error", "-y", "-i", str(wav_path),
          "-codec:a", "libmp3lame", "-q:a", str(vbr_quality), "-write_xing", "1", str(mp3_path)])


def concat_mp3(chunks: list[bytes], mp3_path: Path) -> None:
    if len(chunks) == 1:
        mp3_path.write_bytes(chunks[0])  # the provider's file, byte for byte
        return
    with tempfile.TemporaryDirectory(dir=mp3_path.parent) as tmp:
        lst = Path(tmp) / "list.txt"
        names = []
        for i, data in enumerate(chunks):
            p = Path(tmp) / f"{i:05d}.mp3"
            p.write_bytes(data)
            names.append(f"file '{p.name}'")
        lst.write_text("\n".join(names) + "\n")
        _run(["ffmpeg", "-nostdin", "-loglevel", "error", "-y", "-f", "concat", "-safe", "0",
              "-i", str(lst), "-c", "copy", "-map_metadata", "-1", str(mp3_path)])


def probe_duration(path: Path) -> float | None:
    try:
        out = _run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "json", str(path)])
        return float(json.loads(out)["format"]["duration"])
    except (AudioError, KeyError, ValueError, FileNotFoundError):
        return None
