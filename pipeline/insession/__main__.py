# Copyright (C) 2026 Shrey Kapur
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Split the guides' in-session notes into one file per student per review.

Usage: python -m pipeline.insession

    <paths.insession>/In Session Notes.md  ->  outputs/students/<Name>/<date>_insession.md

The source is a Markdown copy of the guides' shared Google Doc, written next to it by an Apps
Script in the doc (Drive for Desktop syncs it). Layout: `# <full name>`, then `### YYMMDD`
per review, then one `####` heading per guide. A student is matched by the first word of their
name to a folder in outputs/students; anything else (e.g. a template) is skipped.
Copy the results to the reviews folder with `python -m pipeline.export --insession`.
"""
import re

from ..config import load_config

SOURCE = "In Session Notes.md"
DATE = re.compile(r"^###\s+[*_]*(\d{2})(\d{2})(\d{2})[*_]*\s*$")
GUIDE = re.compile(r"^####\s+[*_]*(.+?)[*_]*\s*$")


def split(text: str) -> dict:
    """{(student heading, YYYY-MM-DD): [lines]} from the exported doc."""
    sections, student, key = {}, None, None
    for line in text.splitlines():
        if line.startswith("# "):
            student, key = line[2:].strip(), None
        elif m := DATE.match(line):
            key = (student, f"20{m[1]}-{m[2]}-{m[3]}")
            sections[key] = []
        elif key:
            m = GUIDE.match(line)
            sections[key].append(f"## {m[1]}" if m else line)
    return sections


def main() -> None:
    cfg = load_config()
    src, students = cfg["paths"]["insession"] / SOURCE, cfg["paths"]["outputs"] / "students"
    if not src.is_file():
        raise SystemExit(f"Not found: {src}\nSet paths.insession in config.local.yaml and run "
                         "the export in the doc (RTJT > Export Markdown).")
    known = {p.name for p in students.iterdir() if p.is_dir()}
    counts = {"new": 0, "updated": 0, "unchanged": 0, "skipped": 0}
    for (heading, date), lines in split(src.read_text(encoding="utf-8")).items():
        name = heading.split()[0] if heading else ""
        if name not in known:
            print(f"skipped   {heading or '(no name)'} {date}: no outputs/students/<Name> for it")
            counts["skipped"] += 1
            continue
        content = f"# {name}: in-session notes {date}\n\n" + "\n".join(lines).strip() + "\n"
        dest = students / name / f"{date}_insession.md"
        if dest.exists() and dest.read_text(encoding="utf-8") == content:
            counts["unchanged"] += 1
            continue
        status = "updated" if dest.exists() else "new"
        dest.write_text(content, encoding="utf-8")
        counts[status] += 1
        print(f"{status:9s} {dest.relative_to(students.parent.parent)}")
    print("\n" + ", ".join(f"{v} {k}" for k, v in counts.items()))


if __name__ == "__main__":
    main()
