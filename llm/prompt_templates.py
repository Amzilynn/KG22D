"""Reusable prompt templates for LLM-assisted extraction."""


def build_extraction_system_prompt() -> str:
    return """
You extract structured architectural requirements from user prompts.
Return only valid JSON with exactly these keys:
- building: one of villa, apartment, house, studio
- floors: integer >= 1
- style: one of modern, traditional, minimalist, colonial
- bedrooms: integer >= 0
- rooms: array containing only canonical room names from:
  living_room, kitchen, open_kitchen, dining_room, bedroom, bathroom,
  garage, office, pool, entrance, corridor, stairwell, laundry, storage,
  terrace, garden

Normalize French and English room names to the canonical values.
Do not include markdown, explanations, or extra keys.
""".strip()


EXTRACTION_USER_TEMPLATE = """
Extract the architectural requirements from this prompt:

{text}
""".strip()

ENTITY_EXTRACTION_TEMPLATE = """
Extract architectural entities from the following prompt:

{prompt}
""".strip()

CONSTRAINT_EXTRACTION_TEMPLATE = """
Extract architectural constraints from the following prompt:

{prompt}
""".strip()
