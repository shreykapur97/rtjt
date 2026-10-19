# Copyright (C) 2026 Shrey Kapur
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Speaker diarization with pyannote: who spoke when."""
import os

import numpy as np
import torch
from pyannote.audio import Pipeline

from .decode import SAMPLE_RATE

try:
    # torch>=2.6 only unpickles allowlisted types; older pyannote checkpoints need these
    from pyannote.audio.core.task import Problem, Resolution, Specifications

    torch.serialization.add_safe_globals([torch.torch_version.TorchVersion, Problem, Resolution, Specifications])
except ImportError:
    pass


def diarize(audio: np.ndarray, cfg: dict) -> list[tuple[float, float, str]]:
    pipeline = Pipeline.from_pretrained(cfg["model"], token=os.getenv("HF_TOKEN"))
    pipeline.to(torch.device("cuda" if torch.cuda.is_available() else "cpu"))

    waveform = torch.from_numpy(audio).unsqueeze(0)
    result = pipeline(
        {"waveform": waveform, "sample_rate": SAMPLE_RATE},
        min_speakers=cfg.get("min_speakers"),
        max_speakers=cfg.get("max_speakers"),
    )
    # pyannote 4 returns both a regular and an "exclusive" (one speaker at a time) diarization;
    # exclusive is designed for lining up with transcript words
    if hasattr(result, "speaker_diarization"):
        result = result.exclusive_speaker_diarization if cfg.get("exclusive") else result.speaker_diarization
    turns = [(turn.start, turn.end, speaker) for turn, _, speaker in result.itertracks(yield_label=True)]

    # Free GPU memory before Whisper loads
    del pipeline
    torch.cuda.empty_cache()
    return turns
