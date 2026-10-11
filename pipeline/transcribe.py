"""Speech-to-text with faster-whisper, word-level timestamps."""
import numpy as np
import torch  # noqa: F401  (loads CUDA/cuDNN DLLs that ctranslate2 needs on Windows)
from faster_whisper import WhisperModel


def load_model(cfg: dict) -> WhisperModel:
    return WhisperModel(cfg["model"], device=cfg["device"], compute_type=cfg["compute_type"])


def transcribe(model: WhisperModel, audio: np.ndarray, cfg: dict) -> tuple[list[dict], str]:
    segments, info = model.transcribe(
        audio,
        language=cfg.get("language"),
        word_timestamps=True,
        vad_filter=True,
    )
    words = []
    for seg in segments:
        for w in seg.words:
            words.append({"start": w.start, "end": w.end, "text": w.word})
        print(f"\r  transcribed {seg.end / 60:5.1f} min", end="", flush=True)
    print()
    return words, info.language
