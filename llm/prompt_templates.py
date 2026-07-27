"""Reusable prompt templates for LLM-assisted extraction."""

ENTITY_EXTRACTION_TEMPLATE = """
Extract architectural entities from the following prompt:

{prompt}
""".strip()

CONSTRAINT_EXTRACTION_TEMPLATE = """
Extract architectural constraints from the following prompt:

{prompt}
""".strip()
