"""Group flow layout engines decoupling layout algorithms from container elements."""
from __future__ import annotations

from typing import Any, Literal, Protocol
from diagrams_as_code.elements import RelativeConstraint
from diagrams_as_code.groups import Group, register_group_layout


class GroupFlowLayout(Protocol):
    """Protocol implemented by group flow layout engines."""

    def apply(self, group: Group) -> None:
        """Apply placement constraints to group children."""
        ...


class VerticalFlowLayout:
    """Arranges group children top-to-bottom with specified margin and alignment."""

    def __init__(
        self,
        margin: float = 20.0,
        align: Literal["center", "left", "right"] = "left",
    ) -> None:
        self.margin = float(margin)
        self.align = align
        self.mode = "vertical_flow"

    def apply(self, group: Group) -> None:
        children = group.children
        if not children:
            return
        for ch in children:
            ch.constraints = [c for c in ch.constraints if not c.get("_auto_layout")]
        for i in range(1, len(children)):
            prev = children[i - 1]
            curr = children[i]
            curr.constraints.append(
                RelativeConstraint(
                    target=prev,
                    direction="below",
                    margin=self.margin,
                    align=self.align,
                    _auto_layout=True,
                )
            )


class HorizontalFlowLayout:
    """Arranges group children left-to-right with specified margin and alignment."""

    def __init__(
        self,
        margin: float = 20.0,
        align: Literal["center", "top", "bottom"] = "top",
    ) -> None:
        self.margin = float(margin)
        self.align = align
        self.mode = "horizontal_flow"

    def apply(self, group: Group) -> None:
        children = group.children
        if not children:
            return
        for ch in children:
            ch.constraints = [c for c in ch.constraints if not c.get("_auto_layout")]
        for i in range(1, len(children)):
            prev = children[i - 1]
            curr = children[i]
            curr.constraints.append(
                RelativeConstraint(
                    target=prev,
                    direction="right",
                    margin=self.margin,
                    align=self.align,
                    _auto_layout=True,
                )
            )


class GridLayout:
    """Arranges group children in a 2D grid of rows and columns."""

    def __init__(
        self,
        columns: int = 2,
        margin_x: float = 20.0,
        margin_y: float = 20.0,
    ) -> None:
        self.columns = max(1, int(columns))
        self.margin_x = float(margin_x)
        self.margin_y = float(margin_y)
        self.mode = "grid"

    def apply(self, group: Group) -> None:
        children = group.children
        if not children:
            return
        for ch in children:
            ch.constraints = [c for c in ch.constraints if not c.get("_auto_layout")]
        cols = self.columns
        for idx, ch in enumerate(children):
            row = idx // cols
            col = idx % cols
            if col > 0:
                left_sibling = children[idx - 1]
                ch.constraints.append(
                    RelativeConstraint(
                        target=left_sibling,
                        direction="right",
                        margin=self.margin_x,
                        align="top",
                        _auto_layout=True,
                    )
                )
            if row > 0:
                above_sibling = children[idx - cols]
                if col == 0:
                    ch.constraints.append(
                        RelativeConstraint(
                            target=above_sibling,
                            direction="below",
                            margin=self.margin_y,
                            align="left",
                            _auto_layout=True,
                        )
                    )


register_group_layout("vertical_flow", VerticalFlowLayout)
register_group_layout("vertical", VerticalFlowLayout)
register_group_layout("horizontal_flow", HorizontalFlowLayout)
register_group_layout("horizontal", HorizontalFlowLayout)
register_group_layout("grid", GridLayout)
