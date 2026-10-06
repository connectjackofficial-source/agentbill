"""agentbill config: load pricing overrides from a JSON file."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Optional


def load_config(path: Optional[Path] = None) -> dict:
    if path and Path(path).exists():
        try:
            return json.loads(Path(path).read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return {}
    return {}


def default_path() -> Path:
    return Path.home() / ".agentbill.json"
