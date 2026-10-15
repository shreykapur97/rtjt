"""Flatten student presentations into image-only PDFs.

Usage: python -m pipeline.slides [--force]

    data/raw_presentations/<date>/<Name>.pdf  ->  outputs/students/<Name>/<date>_slides.pdf

Each page is rendered to an image and rebuilt as an image-only PDF, so hidden text, links,
metadata and scripts never reach the reviews folder: Cowork sees exactly what a person sees.
PDF only: export PowerPoint, Google Slides, Keynote etc. to PDF first.
Copy the results to the reviews folder with `python -m pipeline.export --slides`.
"""
import argparse
import io

import pymupdf

from ..config import load_config

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
    parser = argparse.ArgumentParser(description="Flatten presentations into outputs/students")
    parser.add_argument("--force", action="store_true", help="redo presentations already flattened")
    args = parser.parse_args()

    cfg = load_config()
    presentations, outputs = cfg["paths"]["presentations"], cfg["paths"]["outputs"]
    if not presentations.is_dir():
        raise SystemExit(f"Presentations folder not found: {presentations}\n"
                         "Set paths.presentations in config.local.yaml (Windows .lnk shortcuts don't work).")
    counts = {"flattened": 0, "unchanged": 0, "skipped": 0}
    for src in sorted(p for p in presentations.glob("*/*") if p.is_file()):
        rel = f"{src.parent.name}/{src.name}"
        if src.suffix.lower() != ".pdf":
            if src.name.lower() not in {"desktop.ini", "thumbs.db"}:
                how = "in Drive: File > Download > PDF" if src.suffix.lower() == ".gslides" else "export it as PDF"
                print(f"skipped   {rel}: not a PDF, {how} into the same folder")
                counts["skipped"] += 1
            continue
        dest = outputs / "students" / src.stem / f"{src.parent.name}_slides.pdf"
        if dest.exists() and dest.stat().st_mtime >= src.stat().st_mtime and not args.force:
            counts["unchanged"] += 1
            continue
        flatten(src, dest)
        counts["flattened"] += 1
        print(f"flattened {rel} -> {dest.relative_to(outputs.parent)}")
    print("\n" + ", ".join(f"{v} {k}" for k, v in counts.items()))


if __name__ == "__main__":
    main()
