from __future__ import annotations

from typing import Any, Literal, Optional, Union
from iiot_diagrams.geometry import Anchor, Rect


class Element:
    """Base class for all diagram elements."""

    def __init__(
        self,
        id: str,
        label: str,
        width: float = 120.0,
        height: float = 60.0,
        metadata: Optional[dict[str, Any]] = None,
    ) -> None:
        self.id = id
        self.label = label
        self.width = float(width)
        self.height = float(height)
        self.bounds: Rect = Rect(0.0, 0.0, self.width, self.height)
        self.parent: Optional[Element] = None
        self.metadata: dict[str, Any] = dict(metadata) if metadata is not None else {}
        self.constraints: list[dict[str, Any]] = []


class Shape(Element):
    """Visual shape element with absolute or relative positioning constraints."""

    def __init__(
        self,
        id: str,
        label: str,
        width: float = 120.0,
        height: float = 60.0,
        kind: str = "box",
        icon: Optional[str] = None,
        metadata: Optional[dict[str, Any]] = None,
    ) -> None:
        super().__init__(id, label, width, height, metadata)
        self.kind = kind
        self.icon = icon

    def at(
        self, x: float, y: float, anchor: Union[Anchor, str] = Anchor.TOP_LEFT
    ) -> Shape:
        """Position element absolutely with an anchor point."""
        self.constraints.append(
            {"type": "absolute", "x": float(x), "y": float(y), "anchor": anchor}
        )
        return self

    def right_of(
        self,
        other: Element,
        margin: float = 20.0,
        align: Literal["center", "top", "bottom"] = "center",
    ) -> Shape:
        """Position element to the right of another element."""
        self.constraints.append(
            {
                "type": "relative_dir",
                "target": other,
                "direction": "right",
                "margin": float(margin),
                "align": align,
            }
        )
        return self

    def left_of(
        self,
        other: Element,
        margin: float = 20.0,
        align: Literal["center", "top", "bottom"] = "center",
    ) -> Shape:
        """Position element to the left of another element."""
        self.constraints.append(
            {
                "type": "relative_dir",
                "target": other,
                "direction": "left",
                "margin": float(margin),
                "align": align,
            }
        )
        return self

    def below(
        self,
        other: Element,
        margin: float = 20.0,
        align: Literal["center", "left", "right"] = "center",
    ) -> Shape:
        """Position element below another element."""
        self.constraints.append(
            {
                "type": "relative_dir",
                "target": other,
                "direction": "below",
                "margin": float(margin),
                "align": align,
            }
        )
        return self

    def above(
        self,
        other: Element,
        margin: float = 20.0,
        align: Literal["center", "left", "right"] = "center",
    ) -> Shape:
        """Position element above another element."""
        self.constraints.append(
            {
                "type": "relative_dir",
                "target": other,
                "direction": "above",
                "margin": float(margin),
                "align": align,
            }
        )
        return self
