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
        **kwargs: Any,
    ) -> None:
        self.id = id
        self.label = label
        self.width = float(width)
        self.height = float(height)
        self.bounds: Rect = Rect(0.0, 0.0, self.width, self.height)
        self.parent: Optional[Element] = None
        self.metadata: dict[str, Any] = dict(metadata) if metadata is not None else {}
        self.metadata.update(kwargs)
        self.constraints: list[dict[str, Any]] = []
        self._diagram: Optional[Any] = None

    def translate(self, dx: float, dy: float) -> None:
        """Translate element bounds by delta (dx, dy)."""
        self.bounds = Rect(
            self.bounds.x + float(dx),
            self.bounds.y + float(dy),
            self.bounds.width,
            self.bounds.height,
        )

    def clear_constraints(self) -> Element:
        """Clear all positioning constraints from this element."""
        self.constraints.clear()
        return self

    def _find_diagram(self, other: Any = None) -> Optional[Any]:
        """Find the active Diagram instance for this element."""
        if self._diagram is not None:
            return self._diagram
        if other is not None and getattr(other, "_diagram", None) is not None:
            return other._diagram
        from iiot_diagrams.diagram import Diagram

        return Diagram.get_current()

    def __rshift__(self, other: Any) -> Any:
        """Connect this element to target using >> operator."""
        if hasattr(other, "_is_edge_builder") and other._is_edge_builder:
            other.source = self
            return other

        diag = self._find_diagram(other)
        if isinstance(other, Element):
            if diag is not None:
                diag.connect(self, other)
            else:
                from iiot_diagrams.connections import Edge

                Edge(self, other)
            return other
        elif isinstance(other, (list, tuple)):
            # Atomically validate all targets before initiating connections
            for target in other:
                if not isinstance(target, Element):
                    raise TypeError(
                        f"Target must be Element, got {type(target).__name__}"
                    )
            for target in other:
                if diag is not None:
                    diag.connect(self, target)
                else:
                    from iiot_diagrams.connections import Edge

                    Edge(self, target)
            return other
        return NotImplemented

    def __rrshift__(self, other: Any) -> Any:
        """Support list fan-in: [s1, s2] >> self."""
        if isinstance(other, (list, tuple)):
            # Atomically validate all sources before initiating connections
            for source in other:
                if not isinstance(source, Element):
                    raise TypeError(
                        f"Source must be Element, got {type(source).__name__}"
                    )
            for source in other:
                diag = self._find_diagram(source)
                if diag is not None:
                    diag.connect(source, self)
                else:
                    from iiot_diagrams.connections import Edge

                    Edge(source, self)
            return self
        elif isinstance(other, Element):
            diag = self._find_diagram(other)
            if diag is not None:
                diag.connect(other, self)
            else:
                from iiot_diagrams.connections import Edge

                Edge(other, self)
            return self
        return NotImplemented


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
        **kwargs: Any,
    ) -> None:
        super().__init__(
            id,
            label,
            width=width,
            height=height,
            metadata=metadata,
            **kwargs,
        )
        self.kind = kind
        self.icon = icon

    def at(
        self, x: float, y: float, anchor: Union[Anchor, str] = Anchor.TOP_LEFT
    ) -> Shape:
        """Position element absolutely with an anchor point."""
        self.constraints.append(
            {"type": "absolute", "x": float(x), "y": float(y), "anchor": anchor}
        )
        if isinstance(anchor, str):
            try:
                anchor_enum = Anchor(anchor)
            except ValueError:
                anchor_enum = Anchor(anchor.lower())
        else:
            anchor_enum = anchor
        offset = Rect(0.0, 0.0, self.bounds.width, self.bounds.height).get_anchor(
            anchor_enum
        )
        self.bounds = Rect(
            float(x) - offset.x,
            float(y) - offset.y,
            self.bounds.width,
            self.bounds.height,
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

    def move_to(
        self, x: float, y: float, anchor: Union[Anchor, str] = Anchor.TOP_LEFT
    ) -> Shape:
        """Clear existing constraints and relocate element absolutely."""
        self.clear_constraints()
        return self.at(x, y, anchor=anchor)

    def clone(self, new_id: Optional[str] = None, **overrides: Any) -> Shape:
        """Stamp out an independent copy of this shape from a template."""
        clone_id = new_id or overrides.pop("id", None) or f"{self.id}_clone"
        label = overrides.pop("label", self.label)
        width = overrides.pop("width", self.width)
        height = overrides.pop("height", self.height)
        kind = overrides.pop("kind", self.kind)
        icon = overrides.pop("icon", self.icon)
        metadata = dict(self.metadata)
        if "metadata" in overrides:
            metadata.update(overrides.pop("metadata"))
        cloned = Shape(
            id=clone_id,
            label=label,
            width=width,
            height=height,
            kind=kind,
            icon=icon,
            metadata=metadata,
            **overrides,
        )
        return cloned
