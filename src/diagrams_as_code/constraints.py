from __future__ import annotations

from typing import Any, Sequence, Union
from diagrams_as_code.elements import Element
from diagrams_as_code.geometry import Anchor, Rect
from diagrams_as_code.groups import Group


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
            for c in el.constraints:
                if c["type"] == "absolute":
                    self._apply_absolute(el, c)
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
                            c for c in el.constraints if c["type"] == "relative_dir"
                        ]
                        if abs_constraints:
                            self._apply_absolute(el, abs_constraints[0])
                            solved.add(el)
                            progress = True
                        elif not rel_constraints:
                            solved.add(el)
                            progress = True

            # 3b: Resolve relative directional constraints
            for el in all_elements:
                if el in solved:
                    continue
                if isinstance(el, Group) and el.children:
                    if not all(ch in solved for ch in el.children):
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
