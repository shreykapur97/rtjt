# Copyright (C) 2026 Shrey Kapur
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Copy finished outputs into the reviews folder that Claude Cowork works in.

Usage: python -m pipeline.export [--audio] [--slides]     (no flag = both)

    dev/outputs/students/<Name>/<date>_transcript.md  ->  <REVIEWS_DIR>/transcripts/<date>/<Name>.md
    dev/outputs/students/<Name>/<date>_slides.pdf     ->  <REVIEWS_DIR>/presentations/<date>/<Name>.pdf

REVIEWS_DIR is set in .env (a path relative to dev/, or absolute) and must be outside dev/.
One-way copy of these two file types only: no JSON, voiceprints, audio or speaker scores
leave dev. A file is only rewritten when its content changed, and nothing in the reviews folder
is ever deleted or read back.
"""
import argparse
import os
from pathlib import Path

from .config import ROOT, load_config

# kind: (file suffix in outputs/students/<Name>/, folder in reviews, extension there)
KINDS = {
    "audio": ("_transcript.md", "transcripts", ".md"),
    "slides": ("_slides.pdf", "presentations", ".pdf"),
}


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


def export(students: Path, reviews: Path, kind: str) -> dict:
    suffix, folder, ext = KINDS[kind]
    counts = {"new": 0, "updated": 0, "unchanged": 0}
    for src in sorted(students.glob(f"*/*{suffix}")):
        student, date = src.parent.name, src.name.removesuffix(suffix)
        dest = reviews / folder / date / f"{student}{ext}"
        content = src.read_bytes()
        if dest.exists() and dest.read_bytes() == content:
            counts["unchanged"] += 1
            continue
        status = "updated" if dest.exists() else "new"
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(content)
        counts[status] += 1
        print(f"{status:8s} {folder}/{date}/{student}{ext}")
    return counts


def main() -> None:
    parser = argparse.ArgumentParser(description="Copy transcripts and/or slides to the reviews folder")
    parser.add_argument("--audio", action="store_true", help="transcripts only")
    parser.add_argument("--slides", action="store_true", help="flattened slides only")
    args = parser.parse_args()
    kinds = [k for k in KINDS if getattr(args, k)] or list(KINDS)

    cfg = load_config()  # also loads .env
    reviews = reviews_dir()
    for kind in kinds:
        c = export(cfg["paths"]["outputs"] / "students", reviews, kind)
        print(f"{KINDS[kind][1]}: {c['new']} new, {c['updated']} updated, {c['unchanged']} unchanged")
    print(f"-> {reviews}")


if __name__ == "__main__":
    main()
