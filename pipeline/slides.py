"""Flatten student presentations and copy them to the reviews folder that Claude Cowork works in.

Usage: python -m pipeline.slides [--force]

    data/raw_presentations/<date>/<Name>.pdf  ->  <REVIEWS_DIR>/presentations/<date>/<Name>.pdf

Each page is rendered to an image and rebuilt as an image-only PDF, so hidden text, links,
metadata and scripts never reach the reviews folder: Cowork sees exactly what a person sees.
PDF only: export PowerPoint, Google Slides, Keynote etc. to PDF first.
"""
import argparse
import io

import pymupdf

from .config import load_config
from .export import reviews_dir

DPI = 150


def flatten(src, dest) -> None:
    with pymupdf.open(src) as doc, pymupdf.open() as out:
        for page in doc:
            image = page.get_pixmap(dpi=DPI, alpha=False).tobytes("jpeg", jpg_quality=85)
            new = out.new_page(width=page.rect.width, height=page.rect.height)
            new.insert_image(new.rect, stream=io.BytesIO(image))
        dest.parent.mkdir(parents=True, exist_ok=True)
        out.save(dest, garbage=4, deflate=True)


def main() -> None:
    parser = argparse.ArgumentParser(description="Flatten presentations into the reviews folder")
    parser.add_argument("--force", action="store_true", help="redo presentations already copied")
    args = parser.parse_args()

    cfg = load_config()  # also loads .env
    reviews = reviews_dir()
    counts = {"copied": 0, "unchanged": 0, "skipped": 0}
    for src in sorted(p for p in cfg["paths"]["presentations"].glob("*/*") if p.is_file()):
        rel = f"{src.parent.name}/{src.name}"
        if src.suffix.lower() != ".pdf":
            if src.name.lower() not in {"desktop.ini", "thumbs.db"}:
                print(f"skipped   {rel}: not a PDF, export it as PDF first")
                counts["skipped"] += 1
            continue
        dest = reviews / "presentations" / src.parent.name / f"{src.stem}.pdf"
        if dest.exists() and dest.stat().st_mtime >= src.stat().st_mtime and not args.force:
            counts["unchanged"] += 1
            continue
        flatten(src, dest)
        counts["copied"] += 1
        print(f"copied    presentations/{rel}")
    print(f"\n{reviews}: " + ", ".join(f"{v} {k}" for k, v in counts.items()))


if __name__ == "__main__":
    main()
