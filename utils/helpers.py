"""General project helpers."""


def clamp(value: float, minimum: float, maximum: float) -> float:
    """Clamp a numeric value between a minimum and maximum."""
    return max(minimum, min(value, maximum))
