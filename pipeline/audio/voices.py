"""Voiceprints: recognise known people (the guides) by their voice.

    python -m pipeline.audio.voices enroll     build voiceprints from the names in speakers.yaml files
    python -m pipeline.audio.voices test       leave-one-out accuracy check against those names
    python -m pipeline.audio.voices identify   label existing transcripts and re-render them

A voiceprint is the average of pyannote's speaker embeddings (a vector describing a voice) over
many stretches of that person's speech. To identify, each SPEAKER_xx in a recording gets its own
average embedding, which is compared with every voiceprint by cosine similarity (1 = same voice).
Voiceprints are biometric data: they live in data/voiceprints/ (gitignored).
"""
import argparse
import json
import os
import warnings
from collections import defaultdict
from pathlib import Path

warnings.filterwarnings("ignore")

import numpy as np  # noqa: E402

from .decode import SAMPLE_RATE, load_audio  # noqa: E402
from ..config import load_config  # noqa: E402
from .names import manual_names  # noqa: E402

_EMBEDDER = None


def _embedder(cfg: dict):
    """pyannote's speaker-embedding model, taken from the diarization pipeline (loaded once)."""
    global _EMBEDDER
    if _EMBEDDER is None:
        import torch
        from pyannote.audio import Pipeline

        pipeline = Pipeline.from_pretrained(cfg["diarization"]["model"], token=os.getenv("HF_TOKEN"))
        pipeline.to(torch.device("cuda" if torch.cuda.is_available() else "cpu"))
        _EMBEDDER = pipeline._embedding
    return _EMBEDDER


def _unit(v: np.ndarray) -> np.ndarray:
    return v / (np.linalg.norm(v) or 1.0)


def speaker_embeddings(audio: np.ndarray, utterances: list[dict], cfg: dict) -> dict[str, list[float]]:
    """One averaged embedding per SPEAKER_xx, from that speaker's longer turns."""
    import torch

    v = cfg["voices"]
    embed = _embedder(cfg)
    spans = defaultdict(list)
    for u in utterances:
        if u["end"] - u["start"] >= v["min_segment"]:
            spans[u["speaker"]].append((u["start"], min(u["end"], u["start"] + v["max_segment"])))
    result = {}
    for spk, segs in spans.items():
        segs = sorted(segs, key=lambda s: s[0] - s[1])[: v["max_segments"]]  # longest first
        vecs = []
        for start, end in segs:
            chunk = audio[int(start * SAMPLE_RATE):int(end * SAMPLE_RATE)]
            e = embed(torch.from_numpy(chunk)[None, None, :])[0]
            if np.all(np.isfinite(e)):
                vecs.append(_unit(e))
        if vecs:
            result[spk] = _unit(np.mean(vecs, axis=0)).round(5).tolist()
    return result


def load_profiles(cfg: dict) -> dict[str, np.ndarray]:
    folder = cfg["paths"]["voiceprints"]
    return {p.stem: np.load(p) for p in sorted(folder.glob("*.npy"))} if folder.exists() else {}


def match(embeddings: dict[str, list[float]], profiles: dict[str, np.ndarray], threshold: float):
    """Give each known person to at most one speaker: best similarities first, above threshold."""
    scores = {spk: {name: float(np.dot(e, prof)) for name, prof in profiles.items()}
              for spk, e in embeddings.items()}
    names, used = {}, set()
    for spk, name, s in sorted(((spk, n, s) for spk, d in scores.items() for n, s in d.items()),
                               key=lambda t: -t[2]):
        if s >= threshold and spk not in names and name not in used:
            names[spk] = name
            used.add(name)
    return names, {spk: {n: round(s, 3) for n, s in d.items()} for spk, d in scores.items()}


def recordings(cfg: dict) -> list[tuple[Path, dict]]:
    out = []
    for p in sorted((cfg["paths"]["outputs"] / "_work").glob("*/*.json")):
        data = json.loads(p.read_text(encoding="utf-8"))
        if "words" in data["utterances"][0]:
            out.append((p, data))
    return out


def ensure_embeddings(path: Path, data: dict, cfg: dict) -> dict[str, list[float]]:
    """Speaker embeddings for a saved recording, computed once and cached in its JSON."""
    if "speaker_embeddings" not in data["meta"]:
        print(f"  embedding voices: {data['meta']['student']} {data['meta']['date']}")
        audio = load_audio(cfg["paths"]["recordings"] / data["meta"]["source"])
        data["meta"]["speaker_embeddings"] = speaker_embeddings(audio, data["utterances"], cfg)
        path.write_text(json.dumps(data, indent=1, ensure_ascii=False), encoding="utf-8")
    return data["meta"]["speaker_embeddings"]


def labelled(cfg: dict, people_only: bool = False) -> list[tuple[Path, dict, dict[str, str]]]:
    """Recordings with names in speakers.yaml (only `voices.people` if people_only)."""
    people = set(cfg["voices"]["people"])
    out = []
    for path, data in recordings(cfg):
        names = manual_names(cfg["paths"]["outputs"], data["meta"]["date"], data["meta"]["student"])
        names = {spk: n for spk, n in names.items() if n in people or not people_only}
        if names:
            out.append((path, data, names))
    return out


def candidates(profiles: dict[str, np.ndarray], cfg: dict, student: str) -> dict[str, np.ndarray]:
    """Voiceprints to look for in one recording: the people in every recording + its own student."""
    wanted = set(cfg["voices"]["people"]) | {student}
    return {name: prof for name, prof in profiles.items() if name in wanted}


def build_profiles(items, cfg: dict) -> dict[str, np.ndarray]:
    sums = defaultdict(list)
    for path, data, names in items:
        embs = ensure_embeddings(path, data, cfg)
        for spk, name in names.items():
            if spk in embs:
                sums[name].append(np.array(embs[spk]))
    return {name: _unit(np.mean(vs, axis=0)) for name, vs in sums.items()}


def cmd_enroll(cfg: dict) -> None:
    items = labelled(cfg)
    if not items:
        print("No names found. Fill in outputs/_work/<date>/speakers.yaml first "
              f"(people to recognise: {cfg['voices']['people']}).")
        return
    profiles = build_profiles(items, cfg)
    folder = cfg["paths"]["voiceprints"]
    folder.mkdir(parents=True, exist_ok=True)
    for name, vec in profiles.items():
        np.save(folder / f"{name}.npy", vec)
        n = sum(name in names.values() for _, _, names in items)
        print(f"saved voiceprint {name} (from {n} recordings)")


def cmd_test(cfg: dict) -> None:
    """For each named recording: build voiceprints from all the OTHER recordings, identify, compare.
    Only `voices.people` can be tested this way: a student needs at least two named recordings."""
    items = labelled(cfg, people_only=True)
    if len(items) < 2:
        print("Need names in at least 2 recordings to test.")
        return
    threshold = cfg["voices"]["threshold"]
    right = wrong = missed = 0
    same, other = [], []
    print(f"{'recording':22s} {'speaker':11s} {'true':9s} {'guess':9s} similarities")
    for i, (path, data, truth) in enumerate(items):
        profiles = build_profiles(items[:i] + items[i + 1:], cfg)
        embs = ensure_embeddings(path, data, cfg)
        guess, scores = match(embs, profiles, threshold)
        for spk in sorted(embs):
            t, g = truth.get(spk, "-"), guess.get(spk, "-")
            for name, s in scores[spk].items():
                (same if name == t else other).append(s)
            if t != "-" and g == t:
                right += 1
            elif g != "-" and g != t:
                wrong += 1
            elif t != "-":
                missed += 1
            sims = "  ".join(f"{n} {s:.2f}" for n, s in scores[spk].items())
            label = f"{data['meta']['student']} {data['meta']['date']}"
            print(f"{label:22s} {spk:11s} {t:9s} {g:9s} {sims}")
    print(f"\nthreshold {threshold}: {right} right, {wrong} wrong name, {missed} missed")
    if same and other:
        print(f"similarity to own voiceprint:   min {min(same):.2f}  mean {np.mean(same):.2f}")
        print(f"similarity to other voiceprint: max {max(other):.2f}  mean {np.mean(other):.2f}")
        print("A good threshold sits between those two numbers.")


def cmd_identify(cfg: dict) -> None:
    from .__main__ import render_all

    profiles = load_profiles(cfg)
    if not profiles:
        print("No voiceprints yet: run `python -m pipeline.audio.voices enroll` first.")
        return
    for path, data in recordings(cfg):
        embs = ensure_embeddings(path, data, cfg)
        names, scores = match(embs, candidates(profiles, cfg, data["meta"]["student"]), cfg["voices"]["threshold"])
        data["meta"]["speaker_names"], data["meta"]["speaker_scores"] = names, scores
        path.write_text(json.dumps(data, indent=1, ensure_ascii=False), encoding="utf-8")
        found = ", ".join(f"{spk}={n}" for spk, n in sorted(names.items())) or "nobody recognised"
        print(f"{data['meta']['student']:10s} {data['meta']['date']}: {found}")
    render_all(cfg)


def main() -> None:
    parser = argparse.ArgumentParser(description="Voiceprints for recognising known speakers")
    parser.add_argument("command", choices=["enroll", "test", "identify"])
    args = parser.parse_args()
    cfg = load_config()
    {"enroll": cmd_enroll, "test": cmd_test, "identify": cmd_identify}[args.command](cfg)


if __name__ == "__main__":
    main()
