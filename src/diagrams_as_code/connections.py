from __future__ import annotations

from enum import Enum
from typing import Any, Optional, Type, TypeVar, Union

from diagrams_as_code.elements import Element
from diagrams_as_code.geometry import Anchor, Point

E = TypeVar("E", bound=Enum)


def _coerce_enum(
    val: Union[E, str, None],
    enum_cls: Type[E],
    name: str,
    allow_none: bool = False,
) -> Optional[E]:
    """Coerce string or enum instance to expected enum type."""
    if val is None:
        if allow_none:
            return None
        raise TypeError(f"{name} cannot be None")
    if isinstance(val, enum_cls):
        return val
    if isinstance(val, str):
        try:
            return enum_cls(val)
        except ValueError:
            return enum_cls(val.lower())
    raise TypeError(
        f"{name} must be {enum_cls.__name__} or str, got {type(val).__name__}"
    )


class Port(Enum):
    """Connection port locations on element bounding box."""

    NORTH = "north"
    SOUTH = "south"
    EAST = "east"
    WEST = "west"

    def to_anchor(self) -> Anchor:
        """Map port location to geometry Anchor."""
        mapping = {
            Port.NORTH: Anchor.TOP_CENTER,
            Port.SOUTH: Anchor.BOTTOM_CENTER,
            Port.EAST: Anchor.RIGHT_CENTER,
            Port.WEST: Anchor.LEFT_CENTER,
        }
        return mapping[self]


class Routing(Enum):
    """Routing strategy for edges."""

    DIRECT = "direct"
    ORTHOGONAL = "orthogonal"
    CURVE = "curve"


class Edge:
    """Connection between source and target elements with port anchors and routing style."""

    def __init__(
        self,
        source: Element,
        target: Element,
        label: str = "",
        color: Optional[str] = None,
        style: str = "solid",
        source_port: Optional[Union[Port, str]] = None,
        target_port: Optional[Union[Port, str]] = None,
        arrow_head: bool = True,
        arrow_tail: bool = False,
        routing: Union[Routing, str] = Routing.ORTHOGONAL,
        metadata: Optional[dict[str, Any]] = None,
    ) -> None:
        if not isinstance(source, Element):
            raise TypeError(
                f"source must be an Element instance, got {type(source).__name__}"
            )
        if not isinstance(target, Element):
            raise TypeError(
                f"target must be an Element instance, got {type(target).__name__}"
            )

        self.source = source
        self.target = target
        self.label = label
        self.color = color
        self.style = style

        self.source_port = _coerce_enum(
            source_port, Port, "source_port", allow_none=True
        )
        self.target_port = _coerce_enum(
            target_port, Port, "target_port", allow_none=True
        )

        coerced_routing = _coerce_enum(routing, Routing, "routing", allow_none=False)
        assert coerced_routing is not None
        self.routing: Routing = coerced_routing

        self.arrow_head = bool(arrow_head)
        self.arrow_tail = bool(arrow_tail)
        self.metadata: dict[str, Any] = dict(metadata) if metadata else {}
        self.waypoints: Optional[list[Point]] = None
