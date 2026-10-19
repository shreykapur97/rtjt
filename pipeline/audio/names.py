# Copyright (C) 2026 Shrey Kapur
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Speaker names: automatic guesses from voiceprints, overridden by the manual map.

Manual map: outputs/_work/<date>/speakers.yaml
    Ayush:
      SPEAKER_00: Rodrigo
      SPEAKER_02: Shrey
Values left empty are ignored. A name written here always wins over a voiceprint guess.
"""
from pathlib import Path

import yaml


def manual_names(outputs: Path, date: str, student: str) -> dict[str, str]:
    path = outputs / "_work" / date / "speakers.yaml"
    if not path.exists():
        return {}
    block = (yaml.safe_load(path.read_text(encoding="utf-8")) or {}).get(student) or {}
    return {spk: str(name).strip() for spk, name in block.items() if name}


def names_for(data: dict, outputs: Path) -> dict[str, str]:
    """Voiceprint guesses (stored in the JSON), with manual names on top."""
    meta = data["meta"]
    manual = manual_names(outputs, meta["date"], meta["student"])
    auto = {spk: n for spk, n in meta.get("speaker_names", {}).items() if n not in manual.values()}
    return {**auto, **manual}
