from __future__ import annotations

from enum import Enum
import math
from typing import Any, Optional, Sequence, Type, TypeVar, Union

from diagrams_as_code.elements import Element
from diagrams_as_code.geometry import Anchor, PathKind, Point, RoutedPath

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
        routing: Optional[Union[Routing, str]] = None,
        corner_radius: Optional[float] = None,
        arc_radius: Optional[float] = None,
        clearance: Optional[float] = None,
        manual_waypoints: Optional[Sequence[Point]] = None,
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

        self._routing: Optional[Routing] = _coerce_enum(
            routing, Routing, "routing", allow_none=True
        )

        effective_r = corner_radius if corner_radius is not None else arc_radius
        self._corner_radius: Optional[float] = self._validate_corner_radius(effective_r)
        self._clearance: Optional[float] = self._validate_clearance(clearance)

        self.arrow_head = bool(arrow_head)
        self.arrow_tail = bool(arrow_tail)
        self.metadata: dict[str, Any] = dict(metadata) if metadata else {}
        self.manual_waypoints: Optional[list[Point]] = (
            list(manual_waypoints) if manual_waypoints else None
        )
        self._resolved_path: Optional[RoutedPath] = None

    @property
    def routing(self) -> Routing:
        """Routing strategy for edges."""
        if self._routing is not None:
            return self._routing
        if self._resolved_path is not None:
            return (
                Routing.CURVE
                if self._resolved_path.kind == PathKind.BEZIER_CHAIN
                else Routing.ORTHOGONAL
            )
        return Routing.ORTHOGONAL

    @routing.setter
    def routing(self, val: Optional[Union[Routing, str]]) -> None:
        self._routing = _coerce_enum(val, Routing, "routing", allow_none=True)

    @property
    def waypoints(self) -> Optional[list[Point]]:
        """Path waypoints, either from resolved path or manual waypoints."""
        if self._resolved_path is not None:
            return list(self._resolved_path.points)
        if self.manual_waypoints is not None:
            return list(self.manual_waypoints)
        return None

    @waypoints.setter
    def waypoints(self, val: Optional[Union[Sequence[Point], list[Point]]]) -> None:
        self.manual_waypoints = list(val) if val is not None else None
        self._resolved_path = None

    @staticmethod
    def _validate_corner_radius(val: Optional[Union[int, float]]) -> Optional[float]:
        """Validate and coerce corner radius to non-negative finite float."""
        if val is None:
            return None
        if isinstance(val, (bool, str)):
            raise ValueError(
                f"corner_radius must be a non-negative finite float, got {val!r}"
            )
        try:
            r = float(val)
        except (TypeError, ValueError) as exc:
            raise ValueError(
                f"corner_radius must be a non-negative finite float, got {val!r}"
            ) from exc
        if r < 0.0 or math.isnan(r) or math.isinf(r):
            raise ValueError(
                f"corner_radius must be a non-negative finite float, got {r}"
            )
        return r

    @property
    def corner_radius(self) -> Optional[float]:
        """Corner radius for rounded orthogonal fillet bends."""
        if self._corner_radius is not None:
            return self._corner_radius
        if self._resolved_path is not None:
            return self._resolved_path.corner_radius
        return None

    @corner_radius.setter
    def corner_radius(self, val: Optional[Union[int, float]]) -> None:
        self._corner_radius = self._validate_corner_radius(val)

    @property
    def arc_radius(self) -> Optional[float]:
        """Backward-compatible alias for corner_radius."""
        return self._corner_radius

    @arc_radius.setter
    def arc_radius(self, val: Optional[Union[int, float]]) -> None:
        self._corner_radius = self._validate_corner_radius(val)

    @staticmethod
    def _validate_clearance(val: Optional[Union[int, float]]) -> Optional[float]:
        """Validate and coerce clearance buffer to non-negative finite float."""
        if val is None:
            return None
        if isinstance(val, (bool, str)):
            raise ValueError(
                f"clearance must be a non-negative finite float, got {val!r}"
            )
        try:
            c = float(val)
        except (TypeError, ValueError) as exc:
            raise ValueError(
                f"clearance must be a non-negative finite float, got {val!r}"
            ) from exc
        if c < 0.0 or math.isnan(c) or math.isinf(c):
            raise ValueError(
                f"clearance must be a non-negative finite float, got {c}"
            )
        return c

    @property
    def clearance(self) -> float:
        """Clearance buffer distance (in pixels) maintained from obstacles."""
        return self._clearance if self._clearance is not None else 15.0

    @clearance.setter
    def clearance(self, val: Optional[Union[int, float]]) -> None:
        self._clearance = self._validate_clearance(val)

