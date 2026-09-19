from __future__ import annotations

from enum import Enum
from typing import Optional, Union

from iiot_diagrams.elements import Element
from iiot_diagrams.geometry import Anchor


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

        if isinstance(source_port, str):
            try:
                self.source_port: Optional[Port] = Port(source_port)
            except ValueError:
                self.source_port = Port(source_port.lower())
        elif isinstance(source_port, Port) or source_port is None:
            self.source_port = source_port
        else:
            raise TypeError(
                f"source_port must be Port or str, got {type(source_port).__name__}"
            )

        if isinstance(target_port, str):
            try:
                self.target_port: Optional[Port] = Port(target_port)
            except ValueError:
                self.target_port = Port(target_port.lower())
        elif isinstance(target_port, Port) or target_port is None:
            self.target_port = target_port
        else:
            raise TypeError(
                f"target_port must be Port or str, got {type(target_port).__name__}"
            )

        if isinstance(routing, str):
            try:
                self.routing: Routing = Routing(routing)
            except ValueError:
                self.routing = Routing(routing.lower())
        elif isinstance(routing, Routing):
            self.routing = routing
        else:
            raise TypeError(f"routing must be Routing or str, got {type(routing).__name__}")

        self.arrow_head = bool(arrow_head)
        self.arrow_tail = bool(arrow_tail)
