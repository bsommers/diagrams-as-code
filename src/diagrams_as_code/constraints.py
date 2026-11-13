from __future__ import annotations

from typing import Any, Sequence, Union
from diagrams_as_code.elements import (
    AbsoluteConstraint,
    AlignConstraint,
    Constraint,
    DEPENDENT_TYPES,
    Element,
    RelativeConstraint,
    constraint_targets,
    to_constraint,
)
from diagrams_as_code.geometry import Anchor, Rect
from diagrams_as_code.groups import Group

__all__ = [
    "AbsoluteConstraint",
    "AlignConstraint",
    "Constraint",
    "ConstraintSolver",
    "RelativeConstraint",
    "to_constraint",
]


class ConstraintSolver:
    """Solves absolute and relative placement constraints for diagram elements."""

    def __init__(self) -> None:
        self.elements: list[Element] = []

    def add(self, *elements: Union[Element, Sequence[Element]]) -> None:
        """Add elements to the solver."""
        for item in elements:
            if isinstance(item, (list, tuple)):
                for el in item:
                    self._add_single(el)
            elif isinstance(item, Element):
                self._add_single(item)
            else:
                raise TypeError(
                    f"Expected Element or sequence of Elements, got {type(item).__name__}"
                )

    def _add_single(self, el: Element) -> None:
        if not isinstance(el, Element):
            raise TypeError(f"Expected Element, got {type(el).__name__}")
        if any(existing.id == el.id for existing in self.elements):
            raise ValueError(f"Duplicate element id '{el.id}' detected in solver")
        self.elements.append(el)

    def all_elements(self) -> list[Element]:
        """Return every element, groups before their children, in declaration order."""
        result: list[Element] = []
        seen: dict[str, Element] = {}

        def visit(el: Element) -> None:
            if not isinstance(el, Element):
                raise TypeError(f"Expected Element, got {type(el).__name__}")
            if el.id in seen:
                if seen[el.id] is not el:
                    raise ValueError(f"Duplicate element id '{el.id}' detected in solver")
                return
            seen[el.id] = el
            result.append(el)
            if isinstance(el, Group):
                for child in el.children:
                    visit(child)

        for root in self.elements:
            visit(root)
        return result

    _collect_all_elements = all_elements

    def solve(self, strict: bool = True) -> None:
        """Resolve all element constraints iteratively with hierarchical group support."""
        all_elements = self.all_elements()
        solved: set[Element] = set()

        # Step 1: Resolve absolute constraints for non-group elements or empty groups
        for el in all_elements:
            has_children = isinstance(el, Group) and bool(el.children)
            if has_children:
                continue
            has_rel = any(
                c["type"] in DEPENDENT_TYPES for c in el.constraints
            )
            for c in el.constraints:
                if c["type"] == "absolute":
                    self._apply_absolute(el, c)
                    if not has_rel:
                        solved.add(el)
                    break

        # Step 2: Unconstrained elements retain initial bounds without error
        for el in all_elements:
            if el in solved:
                continue
            has_children = isinstance(el, Group) and bool(el.children)
            if not el.constraints and not has_children:
                solved.add(el)

        # Step 3: Multi-pass iterative resolution for relative constraints and group auto-bounds
        max_iters = len(all_elements) * 4 + 20
        for _ in range(max_iters):
            progress = False

            # 3a: Auto-bound any group whose children are all solved
            for el in all_elements:
                if not isinstance(el, Group) or not el.children:
                    continue
                if all(ch in solved for ch in el.children):
                    if el not in solved:
                        el.calculate_bounds()
                        abs_constraints = [
                            c for c in el.constraints if c["type"] == "absolute"
                        ]
                        rel_constraints = [
                            c
                            for c in el.constraints
                            if c["type"] in DEPENDENT_TYPES
                        ]
                        if abs_constraints:
                            self._apply_absolute(el, abs_constraints[0])
                            solved.add(el)
                            progress = True
                        elif not rel_constraints:
                            solved.add(el)
                            progress = True

            # 3b: Resolve relative directional and alignment constraints
            for el in all_elements:
                if el in solved:
                    continue
                if isinstance(el, Group) and el.children:
                    if not all(ch in solved for ch in el.children):
                        continue
                rel_list = [
                    c
                    for c in el.constraints
                    if c["type"] in DEPENDENT_TYPES
                ]
                if not rel_list:
                    continue
                if all(t in solved for c in rel_list for t in constraint_targets(c)):
                    for c in rel_list:
                        if c["type"] == "relative_dir":
                            self._apply_relative(
                                el,
                                c["target"],
                                c["direction"],
                                c["margin"],
                                c["align"],
                            )
                        elif c["type"] == "align":
                            self._apply_align(
                                el,
                                c["target"],
                                c.get("align", "center"),
                                c.get("axis", "horizontal"),
                            )
                        elif c["type"] == "inside":
                            self._apply_inside(el, c)
                        elif c["type"] == "span":
                            self._apply_span(el, c)
                    solved.add(el)
                    progress = True

            if not progress:
                break

        unsolved = [e.id for e in all_elements if e not in solved]
        if unsolved and strict:
            raise RuntimeError(f"Unresolved constraints for elements: {unsolved}")

    def _apply_absolute(self, el: Element, c: dict[str, Any]) -> None:
        """Apply absolute positioning constraint with anchor offset."""
        x = float(c["x"])
        y = float(c["y"])
        anchor = c.get("anchor", Anchor.TOP_LEFT)
        if isinstance(anchor, str):
            try:
                anchor = Anchor(anchor)
            except ValueError:
                anchor = Anchor(anchor.lower())
        offset = Rect(0.0, 0.0, el.bounds.width, el.bounds.height).get_anchor(anchor)
        target_x = x - offset.x
        target_y = y - offset.y
        dx = target_x - el.bounds.x
        dy = target_y - el.bounds.y
        el.translate(dx, dy)

    @staticmethod
    def _anchor(value: Any) -> Anchor:
        if isinstance(value, Anchor):
            return value
        try:
            return Anchor(value)
        except ValueError:
            return Anchor(str(value).lower())

    def _apply_inside(self, el: Element, c: Any) -> None:
        """Pin an anchor of ``el`` to the same anchor of its container, plus an offset."""
        anchor = self._anchor(c.get("anchor", Anchor.CENTER))
        want = c["target"].bounds.get_anchor(anchor)
        have = el.bounds.get_anchor(anchor)
        el.translate(
            want.x + float(c.get("dx", 0.0)) - have.x, want.y + float(c.get("dy", 0.0)) - have.y
        )

    def _apply_span(self, el: Element, c: Any) -> None:
        """Stretch ``el`` along one side of the box around its two targets."""
        box = c["target"].bounds
        if c.get("other") is not None:
            box = box.union(c["other"].bounds)
        side, gap = c.get("side", "right"), float(c.get("gap", 8.0))
        resize = getattr(el, "set_length", None)
        if side in ("left", "right"):
            if resize is not None:
                resize(box.height)
            x = box.right + gap if side == "right" else box.left - gap - el.bounds.width
            y = box.top + (box.height - el.bounds.height) / 2.0
        else:
            if resize is not None:
                resize(box.width)
            x = box.left + (box.width - el.bounds.width) / 2.0
            y = box.bottom + gap if side == "bottom" else box.top - gap - el.bounds.height
        el.translate(x - el.bounds.x, y - el.bounds.y)

    def _apply_relative(
        self,
        el: Element,
        target: Element,
        direction: str,
        margin: float,
        align: str,
    ) -> None:
        """Calculate element bounds relative to a target element and translate."""
        tb = target.bounds
        w, h = el.bounds.width, el.bounds.height

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

        dx = x - el.bounds.x
        dy = y - el.bounds.y
        el.translate(dx, dy)

    def _apply_align(
        self,
        el: Element,
        target: Element,
        align: str,
        axis: str = "horizontal",
    ) -> None:
        """Align element bounds relative to a target element along specified axis."""
        tb = target.bounds
        w, h = el.bounds.width, el.bounds.height
        dx, dy = 0.0, 0.0

        if align == "center":
            if axis in ("horizontal", "x", "both"):
                dx = (tb.left + (tb.width - w) / 2.0) - el.bounds.x
            if axis in ("vertical", "y", "both"):
                dy = (tb.top + (tb.height - h) / 2.0) - el.bounds.y
        elif align == "left":
            dx = tb.left - el.bounds.x
        elif align == "right":
            dx = tb.right - w - el.bounds.x
        elif align == "top":
            dy = tb.top - el.bounds.y
        elif align == "bottom":
            dy = tb.bottom - h - el.bounds.y
        else:
            raise ValueError(f"Unknown align: {align}")

        el.translate(dx, dy)

