# Copyright (C) 2026 Shrey Kapur
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Speech-to-text with faster-whisper, word-level timestamps."""
import numpy as np
import torch  # noqa: F401  (loads CUDA/cuDNN DLLs that ctranslate2 needs on Windows)
from faster_whisper import BatchedInferencePipeline, WhisperModel


def load_model(cfg: dict) -> WhisperModel:
    return WhisperModel(cfg["model"], device=cfg["device"], compute_type=cfg["compute_type"])


def _vocab(cfg: dict) -> list[str]:
    if not cfg.get("use_vocabulary", False):
        return []
    keys = ("names", "terms", "languages", "vocabulary")
    return [w for k in keys for w in (cfg.get(k) or [])]


def _prompt(cfg: dict) -> str | None:
    parts = []
    if cfg.get("style_prompt", False):
        parts.append("Hello, welcome to the architecture thesis review.")
    if vocab := _vocab(cfg):
        parts.append("Glossary: " + ", ".join(vocab) + ".")
    return " ".join(parts) or None


def transcribe(model: WhisperModel, audio: np.ndarray, cfg: dict, quiet: bool = False) -> tuple[list[dict], str]:
    common = dict(
        language=cfg.get("language"),
        initial_prompt=_prompt(cfg),
        hotwords=", ".join(_vocab(cfg)) or None,
        word_timestamps=True,
    )
    if cfg.get("batched", True):
        # Splits audio at pauses and decodes chunks independently, so one bad window can't
        # make Whisper skip the next. Scored best and is deterministic (see pipeline/evaluate.py).
        segments, info = BatchedInferencePipeline(model=model).transcribe(
            audio, batch_size=cfg.get("batch_size", 8), **common
        )
    else:
        segments, info = model.transcribe(
            audio,
            condition_on_previous_text=cfg.get("condition_on_previous_text", True),
            vad_filter=True,
            **common,
        )
    words = []
    for seg in segments:
        for w in seg.words:
            words.append({"start": w.start, "end": w.end, "text": w.word, "prob": round(w.probability, 3)})
        if not quiet:
            print(f"\r  transcribed {seg.end / 60:5.1f} min", end="", flush=True)
    if not quiet:
        print()
    return words, info.language
