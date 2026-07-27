"""Polygon utility functions."""


def polygon_bounds(points: list[tuple[float, float]]) -> tuple[float, float, float, float]:
    """Return min_x, min_y, max_x, max_y for a polygon."""
    xs = [point[0] for point in points]
    ys = [point[1] for point in points]
    return min(xs), min(ys), max(xs), max(ys)
