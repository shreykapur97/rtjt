"""Decode any audio file to 16 kHz mono float32 using ffmpeg (no temp files)."""
import subprocess
from pathlib import Path

import numpy as np

SAMPLE_RATE = 16000
AUDIO_EXTS = {".wav", ".mp3", ".m4a", ".flac", ".ogg", ".opus", ".aac", ".wma", ".webm", ".mp4", ".mov", ".mkv"}


def read_markers(path: Path) -> list[float]:
    """Markers set with Ctrl+M in Windows Sound Recorder, stored as "s1;s2;" in the comment tag."""
    cmd = ["ffprobe", "-v", "error", "-show_entries", "format_tags=comment", "-of", "default=nw=1:nk=1", str(path)]
    comment = subprocess.run(cmd, capture_output=True, text=True).stdout.strip()
    markers = []
    for part in comment.split(";"):
        try:
            markers.append(float(part))
        except ValueError:
            pass
    return sorted(markers)


def load_audio(path: Path) -> np.ndarray:
    cmd = [
        "ffmpeg", "-nostdin", "-v", "error", "-i", str(path),
        "-f", "f32le", "-ac", "1", "-ar", str(SAMPLE_RATE), "-",
    ]
    proc = subprocess.run(cmd, capture_output=True)
    if proc.returncode != 0:
        raise RuntimeError(f"ffmpeg failed on {path}: {proc.stderr.decode(errors='replace').strip()}")
    return np.frombuffer(proc.stdout, dtype=np.float32).copy()
