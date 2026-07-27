"""Knowledge graph export utilities."""

import json
from pathlib import Path


def export_graph_json(graph: dict, output_path: str | Path) -> None:
    """Export a graph as JSON."""
    Path(output_path).write_text(json.dumps(graph, indent=2), encoding="utf-8")
