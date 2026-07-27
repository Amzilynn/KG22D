"""
llm/prompt_parser.py

Entry point of the pipeline: raw user prompt (string) -> structured dict
matching the ontology's vocabulary. This is the contract kg_builder.py
consumes.

Two extraction strategies are available:
  - Rule-based (entity_extractor.py): fast, free, deterministic, but
    limited to the exact vocabulary in ROOM_SYNONYMS.
  - Mistral-based (llm_extractor.py): handles paraphrasing, implicit rooms,
    unusual phrasing -- at the cost of an API call and non-determinism.

Default strategy: try the LLM first (use_llm=True by default) since it
handles free-form prompts much better; fall back to rules automatically
if the API call fails or returns something that doesn't validate. This
guarantees parse_prompt() always returns *something* usable even if the
API is unreachable.
"""

from dataclasses import asdict

from ontology import BuildingSpec, RoomCategory
from entity_extractor import (
    extract_building_type,
    extract_style,
    extract_floors,
    extract_bedroom_count,
    extract_rooms,
)
from llm_extractor import extract_with_llm, LLMExtractionError


def _parse_prompt_rule_based(text: str) -> dict:
    building_type = extract_building_type(text)
    style = extract_style(text)
    floors = extract_floors(text)
    bedroom_count = extract_bedroom_count(text)
    rooms = extract_rooms(text, bedroom_count)

    spec = BuildingSpec(
        building_type=building_type,
        style=style if style is not None else BuildingSpec.__dataclass_fields__["style"].default,
        floors=floors,
        bedrooms=bedroom_count,
        rooms=rooms,
    )

    result = asdict(spec)
    result["building"] = spec.building_type.value
    result["style"] = spec.style.value
    result["rooms"] = [r.value for r in spec.rooms]
    del result["building_type"]
    return result


def parse_prompt(text: str, use_llm: bool = True) -> dict:
    """
    Parse a raw user prompt into a structured dict:

    {
        "building": "villa",
        "floors": 3,
        "style": "modern",
        "rooms": ["living_room", "kitchen", "office", "garage", "pool", ...],
        "bedrooms": 4
    }

    If use_llm=True (default), attempts intelligent Mistral-based extraction
    first and silently falls back to the rule-based extractor if the API
    call fails, times out, or returns an invalid/unparseable response.
    Set use_llm=False to force the deterministic rule-based path only
    (useful for tests, offline runs, or when you want zero API cost).
    """
    if use_llm:
        try:
            return extract_with_llm(text)
        except LLMExtractionError:
            pass  # fall through to rule-based
        except Exception:
            # Covers network errors, auth errors, etc. -- any failure
            # here should degrade gracefully, not crash the pipeline.
            pass

    return _parse_prompt_rule_based(text)


if __name__ == "__main__":
    import json

    villa_prompt = """
    Je veux une villa S+2 moderne avec :
    - 4 chambres
    - une cuisine ouverte
    - un salon
    - une salle à manger
    - un garage
    - une piscine
    - un bureau
    """

    parsed = parse_prompt(villa_prompt)
    print(json.dumps(parsed, indent=2, ensure_ascii=False))
