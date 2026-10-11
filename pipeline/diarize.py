"""Speaker diarization with pyannote: who spoke when."""
import os

import numpy as np
import torch
from pyannote.audio import Pipeline
from pyannote.audio.core.task import Problem, Resolution, Specifications

from .audio import SAMPLE_RATE

# torch>=2.6 only unpickles allowlisted types; pyannote 3.x checkpoints need these
torch.serialization.add_safe_globals([torch.torch_version.TorchVersion, Problem, Resolution, Specifications])


def diarize(audio: np.ndarray, cfg: dict) -> list[tuple[float, float, str]]:
    pipeline = Pipeline.from_pretrained(cfg["model"], use_auth_token=os.getenv("HF_TOKEN"))
    pipeline.to(torch.device("cuda" if torch.cuda.is_available() else "cpu"))

    waveform = torch.from_numpy(audio).unsqueeze(0)
    result = pipeline(
        {"waveform": waveform, "sample_rate": SAMPLE_RATE},
        min_speakers=cfg.get("min_speakers"),
        max_speakers=cfg.get("max_speakers"),
    )
    turns = [(turn.start, turn.end, speaker) for turn, _, speaker in result.itertracks(yield_label=True)]

    # Free GPU memory before Whisper loads
    del pipeline
    torch.cuda.empty_cache()
    return turns
