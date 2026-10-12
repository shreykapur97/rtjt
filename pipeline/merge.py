"""Assign a speaker to each word and group words into utterances."""


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


def build_utterances(words: list[dict], turns: list[tuple[float, float, str]]) -> list[dict]:
    """Consecutive words by the same speaker form one utterance. Words are kept for re-rendering."""
    utterances = []
    for w in words:
        w = {**w, "speaker": _speaker_for(w, turns) if turns else "SPEAKER"}
        if utterances and utterances[-1]["speaker"] == w["speaker"]:
            utterances[-1]["end"] = w["end"]
            utterances[-1]["words"].append(w)
        else:
            utterances.append({"speaker": w["speaker"], "start": w["start"], "end": w["end"], "words": [w]})
    return utterances
