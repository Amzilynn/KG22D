"""Knowledge graph construction."""


def build_knowledge_graph(entities: list[dict], constraints: list[dict]) -> dict:
    """Build a knowledge graph from extracted entities and constraints."""
    return {"entities": entities, "constraints": constraints, "relationships": []}
