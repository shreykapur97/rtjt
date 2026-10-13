"""Copy the finished transcripts into the reviews folder that Claude Cowork works in.

Usage: python -m pipeline.export

    dev/outputs/students/<Name>/<date>_transcript.md  ->  <REVIEWS_DIR>/transcripts/<date>/<Name>.md

REVIEWS_DIR is set in .env (a path relative to dev/, or absolute) and must be outside dev/.
One-way copy of the readable transcripts only: no JSON, voiceprints, audio or speaker scores
leave dev. A file is only rewritten when its content changed, and nothing in the reviews folder
is ever deleted or read back.
"""
import os
from pathlib import Path

from .config import ROOT, load_config


def reviews_dir() -> Path:
    value = os.getenv("REVIEWS_DIR")
    if not value:
        raise SystemExit("Set REVIEWS_DIR in .env, e.g. REVIEWS_DIR=../reviews")
    path = Path(value)
    path = (path if path.is_absolute() else ROOT / path).resolve()
    if not path.is_dir():
        raise SystemExit(f"Reviews folder not found: {path}")
    if path == ROOT or ROOT in path.parents:
        raise SystemExit("REVIEWS_DIR must be outside the dev folder.")
    return path


def main() -> None:
    cfg = load_config()  # also loads .env
    reviews = reviews_dir()
    counts = {"new": 0, "updated": 0, "unchanged": 0}
    for md in sorted((cfg["paths"]["outputs"] / "students").glob("*/*_transcript.md")):
        student, date = md.parent.name, md.stem.removesuffix("_transcript")
        dest = reviews / "transcripts" / date / f"{student}.md"
        content = md.read_bytes()
        if dest.exists() and dest.read_bytes() == content:
            counts["unchanged"] += 1
            continue
        status = "updated" if dest.exists() else "new"
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(content)
        counts[status] += 1
        print(f"{status:8s} transcripts/{date}/{student}.md")
    print(f"\n{reviews}: {counts['new']} new, {counts['updated']} updated, {counts['unchanged']} unchanged")


if __name__ == "__main__":
    main()
