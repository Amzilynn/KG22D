"""
knowledge_graph/ontology.py

Defines the vocabulary (entities, relations, attributes) used across the
whole pipeline: prompt_parser -> kg_builder -> graph_reasoner -> planner.

This file is the single source of truth for names. Every other module
should import from here rather than hardcoding strings like "kitchen"
or "adjacent_to".
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import Optional


# ---------------------------------------------------------------------------
# Entity types
# ---------------------------------------------------------------------------

class EntityType(str, Enum):
    BUILDING = "Building"
    FLOOR = "Floor"
    ROOM = "Room"


class BuildingType(str, Enum):
    VILLA = "villa"
    APARTMENT = "apartment"
    HOUSE = "house"
    STUDIO = "studio"


class BuildingStyle(str, Enum):
    MODERN = "modern"
    TRADITIONAL = "traditional"
    MINIMALIST = "minimalist"
    COLONIAL = "colonial"


class RoomCategory(str, Enum):
    """
    Canonical room vocabulary. The prompt_parser MUST normalize any
    language/synonym input (e.g. French "salon", "chambre") to these
    values before the KG builder ever sees them.
    """
    LIVING_ROOM = "living_room"
    KITCHEN = "kitchen"
    OPEN_KITCHEN = "open_kitchen"
    DINING_ROOM = "dining_room"
    BEDROOM = "bedroom"
    BATHROOM = "bathroom"
    GARAGE = "garage"
    OFFICE = "office"
    POOL = "pool"
    ENTRANCE = "entrance"
    CORRIDOR = "corridor"
    STAIRWELL = "stairwell"
    LAUNDRY = "laundry"
    STORAGE = "storage"
    TERRACE = "terrace"
    GARDEN = "garden"


# ---------------------------------------------------------------------------
# Relation types
# ---------------------------------------------------------------------------

class RelationType(str, Enum):
    HAS_FLOOR = "hasFloor"
    HAS_ROOM = "hasRoom"
    LOCATED_ON = "locatedOn"     # Room -> Floor
    ADJACENT_TO = "adjacentTo"   # Room <-> Room (reasoner-added)
    NEAR = "near"                # Room <-> Room, weaker than adjacent
    OUTSIDE = "outside"          # Room is exterior to the building footprint
    UPSTAIRS = "upstairs"        # Room preference: non-ground floor
    GROUND_FLOOR = "groundFloor" # Room preference: floor 0 only


# ---------------------------------------------------------------------------
# Attribute schemas (defaults / constraints per room category)
# ---------------------------------------------------------------------------

@dataclass
class RoomSpec:
    """
    Default constraints for a room category. Used by graph_validator
    and later by the optimizer/geometry modules. Areas in m^2.
    """
    category: RoomCategory
    area_min: float
    area_max: float
    requires_window: bool = True
    requires_exterior_access: bool = False
    default_floor_preference: Optional[RelationType] = None  # UPSTAIRS / GROUND_FLOOR / None


# Central registry: one RoomSpec per RoomCategory.
# Extend here as new room types are supported — nowhere else.
ROOM_SPECS: dict[RoomCategory, RoomSpec] = {
    RoomCategory.LIVING_ROOM: RoomSpec(RoomCategory.LIVING_ROOM, 20, 45,
                                        default_floor_preference=RelationType.GROUND_FLOOR),
    RoomCategory.KITCHEN: RoomSpec(RoomCategory.KITCHEN, 8, 20,
                                    default_floor_preference=RelationType.GROUND_FLOOR),
    RoomCategory.OPEN_KITCHEN: RoomSpec(RoomCategory.OPEN_KITCHEN, 10, 25,
                                         default_floor_preference=RelationType.GROUND_FLOOR),
    RoomCategory.DINING_ROOM: RoomSpec(RoomCategory.DINING_ROOM, 10, 20,
                                        default_floor_preference=RelationType.GROUND_FLOOR),
    RoomCategory.BEDROOM: RoomSpec(RoomCategory.BEDROOM, 9, 20,
                                    default_floor_preference=RelationType.UPSTAIRS),
    RoomCategory.BATHROOM: RoomSpec(RoomCategory.BATHROOM, 4, 10, requires_window=False),
    RoomCategory.GARAGE: RoomSpec(RoomCategory.GARAGE, 15, 40, requires_window=False,
                                   requires_exterior_access=True,
                                   default_floor_preference=RelationType.GROUND_FLOOR),
    RoomCategory.OFFICE: RoomSpec(RoomCategory.OFFICE, 8, 16),
    RoomCategory.POOL: RoomSpec(RoomCategory.POOL, 20, 80, requires_window=False,
                                 requires_exterior_access=True),
    RoomCategory.ENTRANCE: RoomSpec(RoomCategory.ENTRANCE, 4, 10, requires_window=False,
                                     requires_exterior_access=True,
                                     default_floor_preference=RelationType.GROUND_FLOOR),
    RoomCategory.CORRIDOR: RoomSpec(RoomCategory.CORRIDOR, 3, 15, requires_window=False),
    RoomCategory.STAIRWELL: RoomSpec(RoomCategory.STAIRWELL, 4, 12, requires_window=False),
    RoomCategory.LAUNDRY: RoomSpec(RoomCategory.LAUNDRY, 3, 8, requires_window=False),
    RoomCategory.STORAGE: RoomSpec(RoomCategory.STORAGE, 2, 8, requires_window=False),
    RoomCategory.TERRACE: RoomSpec(RoomCategory.TERRACE, 10, 40, requires_window=False,
                                    requires_exterior_access=True),
    RoomCategory.GARDEN: RoomSpec(RoomCategory.GARDEN, 20, 200, requires_window=False,
                                   requires_exterior_access=True),
}


# ---------------------------------------------------------------------------
# Synonym / normalization table (French + common variants -> RoomCategory)
# ---------------------------------------------------------------------------

ROOM_SYNONYMS: dict[str, RoomCategory] = {
    # French
    "salon": RoomCategory.LIVING_ROOM,
    "séjour": RoomCategory.LIVING_ROOM,
    "sejour": RoomCategory.LIVING_ROOM,
    "cuisine": RoomCategory.KITCHEN,
    "cuisine ouverte": RoomCategory.OPEN_KITCHEN,
    "cuisine américaine": RoomCategory.OPEN_KITCHEN,
    "salle à manger": RoomCategory.DINING_ROOM,
    "salle a manger": RoomCategory.DINING_ROOM,
    "chambre": RoomCategory.BEDROOM,
    "chambres": RoomCategory.BEDROOM,
    "salle de bain": RoomCategory.BATHROOM,
    "salle d'eau": RoomCategory.BATHROOM,
    "garage": RoomCategory.GARAGE,
    "bureau": RoomCategory.OFFICE,
    "piscine": RoomCategory.POOL,
    "entrée": RoomCategory.ENTRANCE,
    "entree": RoomCategory.ENTRANCE,
    "couloir": RoomCategory.CORRIDOR,
    "cage d'escalier": RoomCategory.STAIRWELL,
    "buanderie": RoomCategory.LAUNDRY,
    "cellier": RoomCategory.STORAGE,
    "terrasse": RoomCategory.TERRACE,
    "jardin": RoomCategory.GARDEN,
    # English variants
    "lounge": RoomCategory.LIVING_ROOM,
    "living room": RoomCategory.LIVING_ROOM,
    "open kitchen": RoomCategory.OPEN_KITCHEN,
    "dining room": RoomCategory.DINING_ROOM,
    "study": RoomCategory.OFFICE,
    "swimming pool": RoomCategory.POOL,
}


def normalize_room_name(raw_name: str) -> RoomCategory:
    """
    Map a raw string (French or English, any case) to a canonical
    RoomCategory. Raises ValueError if unknown -- callers should catch
    this and either log it or route it to a fallback/manual-review path.
    """
    key = raw_name.strip().lower()
    if key in ROOM_SYNONYMS:
        return ROOM_SYNONYMS[key]
    try:
        return RoomCategory(key)
    except ValueError:
        raise ValueError(f"Unknown room category: '{raw_name}'")


# ---------------------------------------------------------------------------
# Building-level defaults
# ---------------------------------------------------------------------------

@dataclass
class BuildingSpec:
    building_type: BuildingType = BuildingType.VILLA
    style: BuildingStyle = BuildingStyle.MODERN
    floors: int = 1
    bedrooms: int = 0
    rooms: list[RoomCategory] = field(default_factory=list)