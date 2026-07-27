"""Rule-based extraction of architectural entities from user prompts."""

import re

from ontology import BuildingType, BuildingStyle, RoomCategory, ROOM_SYNONYMS


def _normalized(text: str) -> str:
    return text.lower()


def extract_building_type(prompt: str) -> BuildingType:
    """Extract the building type, defaulting to villa."""
    text = _normalized(prompt)
    for building_type in BuildingType:
        if building_type.value in text:
            return building_type
    return BuildingType.VILLA


def extract_style(prompt: str) -> BuildingStyle | None:
    """Extract a known architectural style if present."""
    text = _normalized(prompt)
    for style in BuildingStyle:
        if style.value in text:
            return style
    return None


def extract_floors(prompt: str) -> int:
    """Extract floor count from S+N notation or explicit floor words."""
    text = _normalized(prompt)

    s_plus_match = re.search(r"\bs\s*\+\s*(\d+)\b", text)
    if s_plus_match:
        return int(s_plus_match.group(1)) + 1

    floor_match = re.search(r"(\d+)\s*(?:floors?|etages?|etages|niveaux)", text)
    if floor_match:
        return max(1, int(floor_match.group(1)))

    return 1


def extract_bedroom_count(prompt: str) -> int:
    """Extract the requested number of bedrooms."""
    text = _normalized(prompt)
    match = re.search(r"(\d+)\s*(?:chambres?|bedrooms?)", text)
    if match:
        return int(match.group(1))
    return 0


def extract_rooms(prompt: str, bedroom_count: int = 0) -> list[RoomCategory]:
    """Extract canonical room categories from the known synonym table."""
    text = _normalized(prompt)
    rooms: list[RoomCategory] = []

    for synonym, category in ROOM_SYNONYMS.items():
        if synonym in text and category not in rooms:
            rooms.append(category)

    if bedroom_count > 0 and RoomCategory.BEDROOM not in rooms:
        rooms.append(RoomCategory.BEDROOM)

    return rooms
