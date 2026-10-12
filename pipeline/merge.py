"""Assign a speaker to each word, group words into utterances, tidy up speakers."""
from collections import defaultdict


def _speaker_for(word: dict, turns: list[tuple[float, float, str]]) -> str:
    best, best_overlap = None, 0.0
    for start, end, speaker in turns:
        overlap = min(end, word["end"]) - max(start, word["start"])
        if overlap > best_overlap:
            best, best_overlap = speaker, overlap
    if best is None and turns:
        # No overlap: take the nearest turn
        mid = (word["start"] + word["end"]) / 2
        best = min(turns, key=lambda t: min(abs(t[0] - mid), abs(t[1] - mid)))[2]
    return best or "UNKNOWN"


def group_words(words: list[dict]) -> list[dict]:
    """Consecutive words by the same speaker form one utterance."""
    utterances = []
    for w in words:
        if utterances and utterances[-1]["speaker"] == w["speaker"]:
            utterances[-1]["end"] = w["end"]
            utterances[-1]["words"].append(w)
        else:
            utterances.append({"speaker": w["speaker"], "start": w["start"], "end": w["end"], "words": [w]})
    return utterances


def build_utterances(words: list[dict], turns: list[tuple[float, float, str]]) -> list[dict]:
    """Words are kept in each utterance so outputs can be re-rendered without re-transcribing."""
    return group_words([{**w, "speaker": _speaker_for(w, turns) if turns else "SPEAKER"} for w in words])


def remove_ghosts(utterances: list[dict], max_seconds: float, max_share: float) -> list[dict]:
    """Speakers with very little speech (under `max_seconds` AND under `max_share` of all speech)
    are usually noise or a mis-split voice: give their words to the nearest real speaker in time."""
    words = [w for u in utterances for w in u["words"]]
    talk = defaultdict(float)
    for w in words:
        talk[w["speaker"]] += w["end"] - w["start"]
    total = sum(talk.values()) or 1
    ghosts = {s for s, secs in talk.items() if secs < max_seconds and secs / total < max_share}
    if not ghosts or len(ghosts) == len(talk):
        return utterances

    real = [i for i, w in enumerate(words) if w["speaker"] not in ghosts]
    cleaned, k = [], 0
    for i, w in enumerate(words):
        if w["speaker"] in ghosts:
            while k + 1 < len(real) and real[k + 1] < i:
                k += 1
            candidates = [real[k]] + ([real[k + 1]] if k + 1 < len(real) else [])
            nearest = min(candidates, key=lambda j: abs(words[j]["start"] - w["start"]))
            w = {**w, "speaker": words[nearest]["speaker"], "ghost": w["speaker"]}
        cleaned.append(w)
    return group_words(cleaned)
