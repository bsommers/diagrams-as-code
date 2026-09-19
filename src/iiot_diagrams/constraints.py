from __future__ import annotations

from typing import Sequence, Union
from iiot_diagrams.elements import Element
from iiot_diagrams.geometry import Anchor, Rect


class ConstraintSolver:
    """Solves absolute and relative placement constraints for diagram elements."""

    def __init__(self) -> None:
        self.elements: list[Element] = []

    def add(self, *elements: Union[Element, Sequence[Element]]) -> None:
        """Add elements to the solver."""
        for item in elements:
            if isinstance(item, (list, tuple)):
                for el in item:
                    if el not in self.elements:
                        self.elements.append(el)
            elif isinstance(item, Element):
                if item not in self.elements:
                    self.elements.append(item)

    def solve(self) -> None:
        """Resolve all element constraints iteratively."""
        solved: set[Element] = set()

        # Resolve absolute constraints first
        for el in self.elements:
            for c in el.constraints:
                if c["type"] == "absolute":
                    x = float(c["x"])
                    y = float(c["y"])
                    anchor = c.get("anchor", Anchor.TOP_LEFT)
                    if isinstance(anchor, str):
                        anchor = Anchor(anchor)
                    offset = Rect(0.0, 0.0, el.width, el.height).get_anchor(anchor)
                    el.bounds = Rect(x - offset.x, y - offset.y, el.width, el.height)
                    solved.add(el)
                    break

        # Iteratively resolve relative constraints
        max_iters = len(self.elements) * 2 + 10
        for _ in range(max_iters):
            progress = False
            for el in self.elements:
                if el in solved:
                    continue
                for c in el.constraints:
                    if c["type"] == "relative_dir":
                        target = c["target"]
                        if target in solved:
                            self._apply_relative(
                                el,
                                target,
                                c["direction"],
                                c["margin"],
                                c["align"],
                            )
                            solved.add(el)
                            progress = True
                            break
            if not progress:
                break

        unsolved = [e.id for e in self.elements if e not in solved]
        if unsolved:
            raise RuntimeError(f"Unresolved constraints for elements: {unsolved}")

    def _apply_relative(
        self,
        el: Element,
        target: Element,
        direction: str,
        margin: float,
        align: str,
    ) -> None:
        """Calculate element bounds relative to a target element."""
        tb = target.bounds
        w, h = el.width, el.height

        if direction == "right":
            x = tb.right + margin
            if align == "center":
                y = tb.top + (tb.height - h) / 2.0
            elif align == "top":
                y = tb.top
            elif align == "bottom":
                y = tb.bottom - h
            else:
                raise ValueError(f"Unknown align for {direction}: {align}")
        elif direction == "left":
            x = tb.left - margin - w
            if align == "center":
                y = tb.top + (tb.height - h) / 2.0
            elif align == "top":
                y = tb.top
            elif align == "bottom":
                y = tb.bottom - h
            else:
                raise ValueError(f"Unknown align for {direction}: {align}")
        elif direction == "below":
            y = tb.bottom + margin
            if align == "center":
                x = tb.left + (tb.width - w) / 2.0
            elif align == "left":
                x = tb.left
            elif align == "right":
                x = tb.right - w
            else:
                raise ValueError(f"Unknown align for {direction}: {align}")
        elif direction == "above":
            y = tb.top - margin - h
            if align == "center":
                x = tb.left + (tb.width - w) / 2.0
            elif align == "left":
                x = tb.left
            elif align == "right":
                x = tb.right - w
            else:
                raise ValueError(f"Unknown align for {direction}: {align}")
        else:
            raise ValueError(f"Unknown direction: {direction}")

        el.bounds = Rect(x, y, w, h)
