"""Assign a speaker to each word, group into utterances, write outputs."""
import json
from pathlib import Path


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
    utterances = []
    for w in words:
        speaker = _speaker_for(w, turns) if turns else "SPEAKER"
        if utterances and utterances[-1]["speaker"] == speaker:
            utterances[-1]["end"] = w["end"]
            utterances[-1]["text"] += w["text"]
        else:
            utterances.append({"speaker": speaker, "start": w["start"], "end": w["end"], "text": w["text"]})
    for u in utterances:
        u["text"] = u["text"].strip()
    return utterances


def _ts(seconds: float) -> str:
    s = int(seconds)
    return f"{s // 3600:02d}:{s % 3600 // 60:02d}:{s % 60:02d}"


def write_outputs(utterances: list[dict], meta: dict, md_path: Path, json_path: Path) -> None:
    json_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(
        json.dumps({"meta": meta, "utterances": utterances}, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    lines = [
        f"# {meta['student']} — review {meta['date']}",
        "",
        f"Language: {meta['language']} · Duration: {_ts(meta['duration'])}",
        "",
    ]
    for u in utterances:
        lines.append(f"**[{_ts(u['start'])}] {u['speaker']}:** {u['text']}")
        lines.append("")
    md_path.parent.mkdir(parents=True, exist_ok=True)
    md_path.write_text("\n".join(lines), encoding="utf-8")
