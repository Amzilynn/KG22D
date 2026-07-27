"""
Mistral-based extraction of building entities from a raw prompt.

The function in this module keeps the same contract as prompt_parser:
it returns a validated dict containing building, floors, style, bedrooms,
and rooms. If Mistral is unavailable or returns invalid JSON, callers can
fall back to the rule-based extractor.
"""

import json
import os
import re
from typing import Any

from ontology import RoomCategory, BuildingType, BuildingStyle
from prompt_templates import build_extraction_system_prompt, EXTRACTION_USER_TEMPLATE


MODEL = os.getenv("MISTRAL_MODEL", "mistral-large-latest")


class LLMExtractionError(Exception):
    """Raised when the LLM response cannot be parsed or validated."""


def _client() -> Any:
    api_key = os.getenv("MISTRAL_API_KEY")
    if not api_key:
        raise LLMExtractionError("Missing MISTRAL_API_KEY environment variable")

    try:
        from mistralai import Mistral
    except ImportError as exc:
        raise LLMExtractionError(
            "Missing mistralai package. Install it with: pip install mistralai"
        ) from exc

    return Mistral(api_key=api_key)


def _strip_markdown_fences(text: str) -> str:
    text = text.strip()
    text = re.sub(r"^```(?:json)?\s*", "", text)
    text = re.sub(r"\s*```$", "", text)
    return text.strip()


def _validate_and_normalize(raw: dict) -> dict:
    required_keys = {"building", "floors", "style", "bedrooms", "rooms"}
    missing = required_keys - raw.keys()
    if missing:
        raise LLMExtractionError(f"Missing keys in LLM response: {missing}")

    try:
        building = BuildingType(raw["building"]).value
    except ValueError as exc:
        raise LLMExtractionError(f"Invalid building type: {raw['building']!r}") from exc

    try:
        style = BuildingStyle(raw["style"]).value
    except ValueError as exc:
        raise LLMExtractionError(f"Invalid style: {raw['style']!r}") from exc

    floors = raw["floors"]
    if not isinstance(floors, int) or floors < 1:
        raise LLMExtractionError(f"Invalid floors value: {floors!r}")

    bedrooms = raw["bedrooms"]
    if not isinstance(bedrooms, int) or bedrooms < 0:
        raise LLMExtractionError(f"Invalid bedrooms value: {bedrooms!r}")

    rooms = raw["rooms"]
    if not isinstance(rooms, list):
        raise LLMExtractionError(f"'rooms' must be a list, got {type(rooms)}")

    validated_rooms = []
    for room in rooms:
        try:
            validated_rooms.append(RoomCategory(room).value)
        except ValueError:
            continue

    return {
        "building": building,
        "floors": floors,
        "style": style,
        "bedrooms": bedrooms,
        "rooms": validated_rooms,
    }


def _extract_response_text(response) -> str:
    content = response.choices[0].message.content
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return "".join(
            block.get("text", "") if isinstance(block, dict) else getattr(block, "text", "")
            for block in content
        )
    return str(content)


def extract_with_llm(text: str, max_retries: int = 1) -> dict:
    """
    Call Mistral to extract structured building entities from a raw prompt.

    Requires MISTRAL_API_KEY in the environment. Optionally set
    MISTRAL_MODEL to override the default model.
    """
    system_prompt = build_extraction_system_prompt()
    user_message = EXTRACTION_USER_TEMPLATE.format(text=text)

    last_error: Exception | None = None
    client = _client()

    for _ in range(max_retries + 1):
        response = client.chat.complete(
            model=MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ],
            response_format={"type": "json_object"},
        )

        cleaned = _strip_markdown_fences(_extract_response_text(response))

        try:
            parsed = json.loads(cleaned)
            return _validate_and_normalize(parsed)
        except (json.JSONDecodeError, LLMExtractionError) as exc:
            last_error = exc

    raise LLMExtractionError(
        f"Failed to get valid extraction after {max_retries + 1} attempt(s): {last_error}"
    )


if __name__ == "__main__":
    test_prompt = """
    Je veux une villa S+2 moderne avec :
    - 4 chambres
    - une cuisine ouverte
    - un salon
    - une salle a manger
    - un garage
    - une piscine
    - un bureau
    """
    print(json.dumps(extract_with_llm(test_prompt), indent=2, ensure_ascii=False))
