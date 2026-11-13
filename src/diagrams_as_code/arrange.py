"""Line elements up and space them out.

These helpers add ordinary placement constraints, so they compose with
``at()``, ``right_of()`` and the rest, and are resolved when the diagram is
solved. The first element is the reference; position it yourself.
"""
from __future__ import annotations

from typing import Optional, Sequence

from diagrams_as_code.elements import AlignConstraint, Element, RelativeConstraint
from diagrams_as_code.geometry import to_px

_EDGES = {
    "left": ("left", "x"), "right": ("right", "x"), "center": ("center", "x"),
    "top": ("top", "y"), "bottom": ("bottom", "y"), "middle": ("center", "y"),
}


def align(elements: Sequence[Element], edge: str = "top") -> list[Element]:
    """Give every element the same ``edge`` as the first.

    ``edge`` is left, center or right (same x) or top, middle or bottom (same y).
    """
    if edge not in _EDGES:
        raise ValueError(f"edge must be one of {sorted(_EDGES)}, got {edge!r}")
    how, axis = _EDGES[edge]
    items = list(elements)
    for el in items[1:]:
        el.constraints.append(AlignConstraint(target=items[0], align=how, axis=axis))
    return items


def distribute(
    elements: Sequence[Element], direction: str = "right", gap: float = 40.0,
    align: Optional[str] = "center",
) -> list[Element]:
    """Place each element ``gap`` beyond the one before it, going ``direction``.

    ``direction`` is right, left, below or above. ``align`` is how each lines up
    with its predecessor across the direction of travel.
    """
    if direction not in ("right", "left", "below", "above"):
        raise ValueError(f"direction must be right, left, below or above, got {direction!r}")
    items = list(elements)
    for prev, el in zip(items, items[1:]):
        el.constraints.append(
            RelativeConstraint(target=prev, direction=direction, margin=to_px(gap), align=align or "center")
        )
    return items


def snap(value: float, grid: float) -> float:
    """``value`` moved to the nearest multiple of ``grid``."""
    return round(float(value) / grid) * grid if grid > 0.0 else float(value)
