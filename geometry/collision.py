"""Geometry collision checks."""


def rectangles_overlap(a: tuple[float, float, float, float], b: tuple[float, float, float, float]) -> bool:
    """Check whether two rectangles overlap."""
    ax1, ay1, ax2, ay2 = a
    bx1, by1, bx2, by2 = b
    return ax1 < bx2 and ax2 > bx1 and ay1 < by2 and ay2 > by1
