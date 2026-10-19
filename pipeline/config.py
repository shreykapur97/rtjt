# Copyright (C) 2026 Shrey Kapur
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Load config.yaml, overlaid with config.local.yaml if present."""
from pathlib import Path

import yaml
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent


def _merge(base: dict, override: dict) -> dict:
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(base.get(key), dict):
            _merge(base[key], value)
        else:
            base[key] = value
    return base


def load_config() -> dict:
    load_dotenv(ROOT / ".env")
    cfg = yaml.safe_load((ROOT / "config.yaml").read_text(encoding="utf-8"))
    local = ROOT / "config.local.yaml"
    if local.exists():
        _merge(cfg, yaml.safe_load(local.read_text(encoding="utf-8")) or {})
    for key, value in cfg["paths"].items():
        cfg["paths"][key] = ROOT / value
    return cfg
