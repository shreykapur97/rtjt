"""Speech-to-text with faster-whisper, word-level timestamps."""
import numpy as np
import torch  # noqa: F401  (loads CUDA/cuDNN DLLs that ctranslate2 needs on Windows)
from faster_whisper import WhisperModel


def load_model(cfg: dict) -> WhisperModel:
    return WhisperModel(cfg["model"], device=cfg["device"], compute_type=cfg["compute_type"])


def _vocab(cfg: dict) -> list[str]:
    return (cfg.get("names") or []) + (cfg.get("vocabulary") or [])


def _prompt(cfg: dict) -> str:
    # Sets style (punctuation, casing) for the first window; later windows carry it over
    prompt = "Hello, welcome to the architecture thesis review."
    if vocab := _vocab(cfg):
        prompt += " Glossary: " + ", ".join(vocab) + "."
    return prompt


def transcribe(model: WhisperModel, audio: np.ndarray, cfg: dict) -> tuple[list[dict], str]:
    segments, info = model.transcribe(
        audio,
        language=cfg.get("language"),
        initial_prompt=_prompt(cfg),
        condition_on_previous_text=cfg.get("condition_on_previous_text", True),
        hotwords=", ".join(_vocab(cfg)) or None,  # applied to every window, unlike initial_prompt
        word_timestamps=True,
        vad_filter=True,
    )
    words = []
    for seg in segments:
        for w in seg.words:
            words.append({"start": w.start, "end": w.end, "text": w.word, "prob": round(w.probability, 3)})
        print(f"\r  transcribed {seg.end / 60:5.1f} min", end="", flush=True)
    print()
    return words, info.language
