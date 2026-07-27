"""General parsing helpers."""

import json
from pathlib import Path


def load_json(path: str | Path) -> dict:
    """Load a JSON file."""
    return json.loads(Path(path).read_text(encoding="utf-8"))
