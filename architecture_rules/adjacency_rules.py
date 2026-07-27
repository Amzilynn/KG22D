"""Adjacency rules for room placement."""

PREFERRED_ADJACENCIES = {
    "kitchen": {"dining_room", "living_room"},
    "bedroom": {"bathroom"},
}

AVOID_ADJACENCIES = {
    "bedroom": {"garage", "technical_room"},
}
