"""Re-run speaker detection on full recordings, reusing the saved Whisper words.

Usage: python -m pipeline.rediarize <label>

Writes outputs/_compare/<label>/<Name>/<date>_transcript.md (and .json) using the diarization
settings in config.yaml, so a different speaker model can be read side by side with the current
transcripts in outputs/students/. Prints, per student, speakers and turns for both, and how often
the two agree on who said each word.
"""
import argparse
import json
import warnings
from collections import Counter, defaultdict

warnings.filterwarnings("ignore")

from .audio import load_audio  # noqa: E402
from .config import load_config  # noqa: E402
from .merge import build_utterances, remove_ghosts  # noqa: E402
from .render import save  # noqa: E402


def agreement(a: list[str], b: list[str]) -> float:
    """Share of words given the same speaker, after matching up the two label sets
    (each model numbers its speakers independently)."""
    pairs = Counter(zip(a, b))
    mapping, used = {}, set()
    for (x, y), _ in pairs.most_common():
        if x not in mapping and y not in used:
            mapping[x] = y
            used.add(y)
    return sum(n for (x, y), n in pairs.items() if mapping.get(x) == y) / max(len(a), 1)


def stats(utterances: list[dict]) -> tuple[int, int]:
    return len({u["speaker"] for u in utterances}), len(utterances)


def main() -> None:
    parser = argparse.ArgumentParser(description="Re-run speaker detection on saved transcripts")
    parser.add_argument("label", help="name for this run, e.g. community-1")
    args = parser.parse_args()

    cfg = load_config()
    outputs = cfg["paths"]["outputs"]
    out_root = outputs / "_compare" / args.label
    ghost = cfg["render"]["ghost_max_words"]

    from .diarize import diarize

    print(f"diarization: {cfg['diarization']['model']} (exclusive: {cfg['diarization'].get('exclusive', False)})")
    rows = []
    for json_path in sorted((outputs / "_work").rglob("*.json")):
        data = json.loads(json_path.read_text(encoding="utf-8"))
        meta = data["meta"]
        if "words" not in data["utterances"][0]:
            continue
        print(f"  {meta['student']} {meta['date']}...")
        old = remove_ghosts(data["utterances"], ghost)
        words = [{k: v for k, v in w.items() if k not in ("speaker", "ghost")}
                 for u in data["utterances"] for w in u["words"]]

        turns = diarize(load_audio(cfg["paths"]["recordings"] / meta["source"]), cfg["diarization"])
        new_data = {"meta": {**meta, "diarization": cfg["diarization"]["model"]},
                    "utterances": build_utterances(words, turns)}
        new = remove_ghosts(new_data["utterances"], ghost)

        name = f"{meta['date']}_transcript"
        save(new_data, cfg["render"], out_root / meta["student"] / f"{name}.md",
             out_root / "_work" / meta["date"] / f"{meta['student']}.json", cfg["paths"]["presentations"])
        speakers = lambda us: [w["speaker"] for u in us for w in u["words"]]
        rows.append((meta["student"], *stats(old), *stats(new), agreement(speakers(old), speakers(new))))

    print(f"\n{'Student':10s} {'current: speakers/turns':>24s} {args.label + ': speakers/turns':>28s} {'agree':>7s}")
    for student, s0, t0, s1, t1, agree in rows:
        print(f"{student:10s} {s0:>15d} / {t0:<6d} {s1:>19d} / {t1:<6d} {agree:>7.0%}")
    print(f"\nside-by-side transcripts in {out_root.relative_to(outputs.parent)}")


if __name__ == "__main__":
    main()
