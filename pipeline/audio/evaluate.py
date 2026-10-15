"""Score transcription settings against hand-corrected clips.

Usage: python -m pipeline.audio.evaluate [--presets a b ...] [--repeats N]

data/eval/<clip>.m4a + <clip>.txt  (reference: exact words; a line starting with "-" = speaker change)
Reports word error rate (WER, lower is better) and how many reference speaker changes the
pipeline also switches speaker at. Results are saved to outputs/_eval/<timestamp>.md.
"""
import argparse
import difflib
import re
import statistics
import time
import warnings
from datetime import datetime
from pathlib import Path

warnings.filterwarnings("ignore")

from .decode import load_audio  # noqa: E402
from ..config import load_config  # noqa: E402

FILLERS = {"um", "uh", "umm", "uhm", "mm", "mhm", "hmm", "erm", "ah", "eh"}


def normalise(text: str) -> list[str]:
    """Lowercase, drop punctuation and fillers; hyphenated words count as separate words."""
    tokens = re.sub(r"[^\w\s']", " ", text.lower().replace("-", " ")).split()
    return [t.strip("'") for t in tokens if t.strip("'") and t not in FILLERS]


def read_reference(path: Path) -> tuple[list[str], list[int]]:
    """Reference words, plus the word index where each speaker change ("-" line) starts."""
    words, changes = [], []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.lstrip().startswith("-") and words:
            changes.append(len(words))
        words += normalise(line)
    return words, changes


def wer(ref: list[str], hyp: list[str]) -> float:
    """Word error rate: (substitutions + deletions + insertions) / reference length."""
    prev = list(range(len(hyp) + 1))
    for i, r in enumerate(ref, 1):
        cur = [i] + [0] * len(hyp)
        for j, h in enumerate(hyp, 1):
            cur[j] = min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (r != h))
        prev = cur
    return prev[-1] / max(len(ref), 1)


def change_counts(ref: list[str], changes: list[int], hyp_words: list[dict], tolerance: int) -> dict:
    """Compare speaker changes. Recall: reference changes the pipeline also switches at.
    Precision: pipeline switches that sit at a real change (penalises switching too often)."""
    hyp = [(t, w["speaker"]) for w in hyp_words for t in normalise(w["text"])]
    hyp_tokens = [t for t, _ in hyp]
    hyp_changes = [j for j in range(1, len(hyp)) if hyp[j][1] != hyp[j - 1][1]]
    ref_to_hyp = {}
    for a, b, size in difflib.SequenceMatcher(None, ref, hyp_tokens, autojunk=False).get_matching_blocks():
        for k in range(size):
            ref_to_hyp[a + k] = b + k
    # each reference change, located in the pipeline's word sequence (nearest aligned word at or after it)
    located = [j for c in changes
               if (j := next((ref_to_hyp[i] for i in range(c, min(c + tolerance + 1, len(ref))) if i in ref_to_hyp),
                             None)) is not None]
    return {
        "ref": len(changes),
        "ref_hit": sum(any(abs(j - h) <= tolerance for h in hyp_changes) for j in located),
        "hyp": len(hyp_changes),
        "hyp_hit": sum(any(abs(j - h) <= tolerance for j in located) for h in hyp_changes),
    }


def change_scores(counts: list[dict]) -> tuple[float, float, float]:
    """Recall, precision and F1 pooled over all clips and runs."""
    recall = sum(c["ref_hit"] for c in counts) / max(sum(c["ref"] for c in counts), 1)
    precision = sum(c["hyp_hit"] for c in counts) / max(sum(c["hyp"] for c in counts), 1)
    f1 = 2 * recall * precision / (recall + precision) if recall + precision else 0.0
    return recall, precision, f1


def preset_cfg(base: dict, preset: dict) -> dict:
    """Whisper config for a preset: `vocabulary` maps to use_vocabulary, other keys override directly."""
    cfg = {**base, **{k: v for k, v in preset.items() if k != "vocabulary"}}
    if "vocabulary" in preset:
        cfg["use_vocabulary"] = preset["vocabulary"]
    return cfg


def main() -> None:
    parser = argparse.ArgumentParser(description="Score transcription settings on data/eval clips")
    parser.add_argument("--presets", nargs="*", help="only these presets (default: all in config.yaml)")
    parser.add_argument("--repeats", type=int, help="runs per preset (default from config.yaml)")
    args = parser.parse_args()

    cfg = load_config()
    ev = cfg["eval"]
    presets = {k: v for k, v in ev["presets"].items() if not args.presets or k in args.presets}
    repeats = args.repeats or ev["repeats"]
    clips = sorted(p for p in cfg["paths"]["eval"].glob("*.m4a") if p.with_suffix(".txt").exists())
    if not clips:
        print(f"No clips with a matching .txt in {cfg['paths']['eval']}")
        return

    from .diarize import diarize
    from .merge import build_utterances, remove_ghosts
    from .transcribe import load_model, transcribe

    print(f"{len(clips)} clips · {len(presets)} presets · {repeats} repeats")
    data = {}
    for clip in clips:
        audio = load_audio(clip)
        print(f"  diarizing {clip.stem}...")
        data[clip.stem] = (audio, diarize(audio, cfg["diarization"]), *read_reference(clip.with_suffix(".txt")))

    model = load_model(cfg["whisper"])
    results = {}  # preset -> clip -> list of (wer, change counts)
    t0 = time.time()
    for name, preset in presets.items():
        wcfg = preset_cfg(cfg["whisper"], preset)
        for clip, (audio, turns, ref, changes) in data.items():
            for r in range(repeats):
                words, _ = transcribe(model, audio, wcfg, quiet=True)
                utterances = remove_ghosts(build_utterances(words, turns), cfg["render"]["ghost_max_words"])
                labelled = [w for u in utterances for w in u["words"]]
                hyp = [t for w in words for t in normalise(w["text"])]
                score = (wer(ref, hyp), change_counts(ref, changes, labelled, ev["change_tolerance"]))
                results.setdefault(name, {}).setdefault(clip, []).append(score)
                print(f"  {name:14s} {clip:24s} run {r + 1}: WER {score[0]:.1%}")

    report = render_report(results, list(data), repeats, cfg["diarization"])
    print("\n" + report)
    out = cfg["paths"]["outputs"] / "_eval" / f"{datetime.now():%Y-%m-%d_%H%M}.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(report, encoding="utf-8")
    print(f"\nsaved {out.relative_to(cfg['paths']['outputs'].parent)} · {(time.time() - t0) / 60:.1f} min")


def render_report(results: dict, clips: list[str], repeats: int, diarization: dict) -> str:
    pct = lambda x: f"{x:.1%}"
    lines = [f"# Evaluation {datetime.now():%Y-%m-%d %H:%M}", "",
             f"Diarization: {diarization['model']} (exclusive: {diarization.get('exclusive', False)})", "",
             f"WER = share of words wrong (lower is better). Range = best–worst over {repeats} runs.",
             "Speaker changes: recall = real changes caught, precision = pipeline switches that were real,",
             "F1 = both combined (higher is better).", "",
             "| Preset | Avg WER | Range | Change recall | Change precision | Change F1 |", "|---|---|---|---|---|---|"]
    ranked = sorted(results, key=lambda n: statistics.mean(s[0] for c in results[n].values() for s in c))
    for name in ranked:
        per_run = [statistics.mean(results[name][c][r][0] for c in clips) for r in range(repeats)]
        recall, precision, f1 = change_scores([s[1] for c in results[name].values() for s in c])
        lines.append(f"| {name} | {pct(statistics.mean(per_run))} | {pct(min(per_run))}–{pct(max(per_run))} | "
                     f"{pct(recall)} | {pct(precision)} | {pct(f1)} |")
    lines += ["", "## WER per clip", "", "| Preset | " + " | ".join(clips) + " |", "|---" * (len(clips) + 1) + "|"]
    for name in ranked:
        cells = [pct(statistics.mean(s[0] for s in results[name][c])) for c in clips]
        lines.append(f"| {name} | " + " | ".join(cells) + " |")
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    main()
