"""Spatial graph generation from a knowledge graph."""


def create_floor_graph(knowledge_graph: dict) -> dict:
    """Convert a knowledge graph into a spatial planning graph."""
    return {"nodes": knowledge_graph.get("entities", []), "edges": []}
