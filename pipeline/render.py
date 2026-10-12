"""Turn the JSON working data into a readable Markdown transcript."""
import json
import os
from collections import defaultdict
from pathlib import Path

from .merge import group_words, remove_ghosts

SENTENCE_END = (".", "?", "!")


def _ts(seconds: float) -> str:
    s = int(seconds)
    return f"{s // 3600:02d}:{s % 3600 // 60:02d}:{s % 60:02d}"


def _text(words: list[dict]) -> str:
    return "".join(w["text"] for w in words).strip()


def _speaking_time(utterances: list[dict]) -> dict[str, float]:
    totals = defaultdict(float)
    for u in utterances:
        for w in u["words"]:
            totals[w["speaker"]] += w["end"] - w["start"]
    return dict(sorted(totals.items(), key=lambda kv: -kv[1]))


def _fold_interjections(utterances: list[dict], cfg: dict) -> list[dict]:
    """A short reply ("yeah", "mm-hm") between two turns of the same other speaker
    becomes an inline note in that speaker's turn instead of its own line."""
    out = []
    i = 0
    while i < len(utterances):
        u = utterances[i]
        prev = out[-1] if out else None
        nxt = utterances[i + 1] if i + 1 < len(utterances) else None
        short = (
            len(u["words"]) <= cfg["interjection_max_words"]
            and u["end"] - u["start"] <= cfg["interjection_max_seconds"]
        )
        if short and prev and nxt and prev["speaker"] == nxt["speaker"] != u["speaker"]:
            note = {"start": u["start"], "end": u["end"], "text": f" *({u['speaker']}: {_text(u['words'])})*",
                    "speaker": u["speaker"], "inline": True}
            prev["words"] = prev["words"] + [note] + nxt["words"]
            prev["end"] = nxt["end"]
            i += 2
            continue
        out.append({**u, "words": list(u["words"])})
        i += 1
    return out


def _paragraphs(words: list[dict], cfg: dict) -> list[list[dict]]:
    """Split one speaker's turn at long pauses, or at a sentence end once it gets long."""
    paras, current = [], []
    for w in words:
        if current:
            pause = w["start"] - current[-1]["end"]
            long_and_ended = len(current) >= cfg["paragraph_max_words"] and current[-1]["text"].strip().endswith(SENTENCE_END)
            if pause >= cfg["paragraph_pause"] or long_and_ended:
                paras.append(current)
                current = []
        current.append(w)
    if current:
        paras.append(current)
    return paras


def apply_names(utterances: list[dict], names: dict[str, str], student: str | None) -> list[dict]:
    """Replace SPEAKER_xx with names. If `student` is given, not yet identified, and exactly one
    speaker is left unnamed, that speaker is the student. Same name on two labels = one speaker."""
    names = dict(names)
    unnamed = {u["speaker"] for u in utterances} - names.keys()
    if student and names and student not in names.values() and len(unnamed) == 1:
        names[unnamed.pop()] = student
    if not names:
        return utterances
    return group_words([{**w, "speaker": names.get(w["speaker"], w["speaker"])}
                        for u in utterances for w in u["words"]])


def render_markdown(data: dict, cfg: dict, presentation: Path | None, md_path: Path,
                    names: dict[str, str] | None = None, label_student: bool = False) -> str:
    meta = data["meta"]
    utterances = remove_ghosts(data["utterances"], cfg["ghost_max_words"])
    utterances = apply_names(utterances, names or {}, meta["student"] if label_student else None)
    speaking = _speaking_time(utterances)
    total = sum(speaking.values()) or 1

    lines = [f"# {meta['student']} — review {meta['date']}", ""]
    info = [f"**Duration:** {_ts(meta['duration'])}", f"**Language:** {meta['language']}"]
    if presentation:
        link = Path(os.path.relpath(presentation, md_path.parent)).as_posix()
        info.append(f"**Presentation:** [{presentation.name}]({link})")
    lines += [" · ".join(info), ""]

    markers = meta.get("markers", [])
    if markers:
        links = [f"[{k + 1} · {_ts(m)}](#marker-{k + 1})" for k, m in enumerate(markers)]
        lines += ["**Marked moments:** " + " · ".join(links), ""]

    lines += ["| Speaker | Speaking time | Share |", "|---|---|---|"]
    for speaker, secs in speaking.items():
        lines.append(f"| {speaker} | {_ts(secs)} | {secs / total:.0%} |")
    lines += ["", "---", ""]

    windows = [(m - cfg["marker_before"], m + cfg["marker_after"]) for m in markers]
    labelled, prev_hit = set(), False
    for u in _fold_interjections(utterances, cfg):
        for n, p in enumerate(_paragraphs(u["words"], cfg)):
            block = [f"**{u['speaker']}** `{_ts(u['start'])}`", _text(p)] if n == 0 else [f"`{_ts(p[0]['start'])}` {_text(p)}"]
            hits = [k for k, (a, b) in enumerate(windows) if p[0]["start"] < b and p[-1]["end"] > a]
            if hits:
                label = []
                for k in hits:
                    if k not in labelled:
                        labelled.add(k)
                        label += [f'<a id="marker-{k + 1}"></a>**Marked moment {k + 1}** · `{_ts(markers[k])}`', ""]
                block = ["> " + line if line else ">" for line in label + block]
                if prev_hit:
                    lines[-1] = ">"  # keep consecutive highlighted paragraphs in one quote box
            lines += block + [""]
            prev_hit = bool(hits)
    return "\n".join(lines)


def save(data: dict, cfg: dict, md_path: Path, json_path: Path, presentations_dir: Path,
         names: dict[str, str] | None = None, label_student: bool = False) -> None:
    json_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(data, indent=1, ensure_ascii=False), encoding="utf-8")
    write_markdown(data, cfg, md_path, presentations_dir, names, label_student)


def write_markdown(data: dict, cfg: dict, md_path: Path, presentations_dir: Path,
                   names: dict[str, str] | None = None, label_student: bool = False) -> None:
    meta = data["meta"]
    pdf = presentations_dir / meta["date"] / f"{meta['student']}.pdf"
    md_path.parent.mkdir(parents=True, exist_ok=True)
    md = render_markdown(data, cfg, pdf if pdf.exists() else None, md_path, names, label_student)
    md_path.write_text(md, encoding="utf-8")
