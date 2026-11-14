from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import math
from typing import Any, Optional, Sequence, Type, TypeVar, Union

from diagrams_as_code.drawing import ARROW_STYLES
from diagrams_as_code.elements import AnchorRef, Element, Junction
from diagrams_as_code.geometry import Anchor, PathKind, Point, RoutedPath, to_px

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
    #: A smooth curve through the edge's ``via`` points.
    SPLINE = "spline"


@dataclass(frozen=True)
class EdgeStyle:
    routing: Routing
    corner_radius: float
    clearance: float


def _as_point(value: Any) -> Optional[Point]:
    if isinstance(value, Point):
        return value
    if (
        isinstance(value, (tuple, list))
        and len(value) == 2
        and all(isinstance(v, (int, float, str)) and not isinstance(v, bool) for v in value)
    ):
        return Point(to_px(value[0]), to_px(value[1]))
    return None


def _endpoint(value: Any, name: str) -> tuple[Element, Optional[Port], Optional[float]]:
    """An edge end as (element, port, fraction along that side).

    An end may be an element, a point on its side (``box.anchor("right", 0.25)``)
    or a bare point, which becomes an invisible ``Junction``.
    """
    if isinstance(value, AnchorRef):
        if not isinstance(value.element, Element):
            raise TypeError(f"{name} anchor must be on an Element")
        return value.element, Port(value.side), float(value.fraction)
    point = _as_point(value)
    if point is not None:
        return Junction("point", point.x, point.y), None, None
    if not isinstance(value, Element):
        raise TypeError(f"{name} must be an Element instance, got {type(value).__name__}")
    return value, None, None


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
        width: Optional[float] = None,
        head: str = "triangle",
        tail: str = "triangle",
        arrow_size: float = 1.0,
        two_way: bool = False,
        via: Optional[Sequence[Any]] = None,
        trunk: Optional[float] = None,
        ellipsis: bool = False,
        z: float = 0.0,
    ) -> None:
        source, anchor_port, source_anchor = _endpoint(source, "source")
        if anchor_port is not None:
            source_port = anchor_port
        target, anchor_port, target_anchor = _endpoint(target, "target")
        if anchor_port is not None:
            target_port = anchor_port

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
        #: Where along its side each end attaches, 0 to 1; ``None`` is the layout's choice.
        self.source_anchor: Optional[float] = source_anchor
        self.target_anchor: Optional[float] = target_anchor
        if width is not None and not (float(width) > 0.0 and math.isfinite(float(width))):
            raise ValueError(f"width must be a positive finite number, got {width!r}")
        #: Stroke weight in pixels; ``None`` uses the theme's.
        self.width: Optional[float] = None if width is None else to_px(width)
        for name, value in (("head", head), ("tail", tail)):
            if value not in ARROW_STYLES:
                raise ValueError(f"{name} must be one of {ARROW_STYLES}, got {value!r}")
        #: Arrowhead shape at the target end and at the source end.
        self.head = head
        self.tail = tail
        if not (float(arrow_size) > 0.0 and math.isfinite(float(arrow_size))):
            raise ValueError(f"arrow_size must be a positive finite number, got {arrow_size!r}")
        #: Arrowhead size as a multiple of the default for the stroke weight.
        self.arrow_size = float(arrow_size)
        #: Points the line passes through between its ends.
        self.via: Optional[list[Point]] = None
        if via:
            self.via = []
            for item in via:
                point = _as_point(item)
                if point is None:
                    raise TypeError(f"via must be a sequence of points, got {item!r}")
                self.via.append(point)
        #: Distance from the source port (negative: from the target port) at which
        #: the line turns, so edges from one source share a trunk up to there.
        self.trunk: Optional[float] = None if trunk is None else to_px(trunk)
        #: Draw the middle of the line as three dots, for "and so on".
        self.ellipsis = bool(ellipsis)
        #: Above zero the edge is painted over the nodes instead of under them.
        self.z = float(z)

        self._routing: Optional[Routing] = _coerce_enum(
            routing, Routing, "routing", allow_none=True
        )

        effective_r = corner_radius if corner_radius is not None else arc_radius
        self._corner_radius: Optional[float] = self._validate_corner_radius(effective_r)
        self._clearance: Optional[float] = self._validate_clearance(clearance)

        self.arrow_head = bool(arrow_head)
        self.arrow_tail = bool(arrow_tail) or bool(two_way)
        self.metadata: dict[str, Any] = dict(metadata) if metadata else {}
        self.manual_waypoints: Optional[list[Point]] = (
            list(manual_waypoints) if manual_waypoints else None
        )
        self._resolved_path: Optional[RoutedPath] = None
        self._resolved_style: Optional[EdgeStyle] = None
        #: Centre of the label badge, chosen by the layout; ``None`` means the path midpoint.
        self._label_anchor: Optional[Point] = None
        #: Text width the badge is wrapped at, when it would not fit unwrapped.
        self._label_wrap: Optional[float] = None
        #: Another edge whose identical badge, on a shared trunk, labels this edge too.
        self._label_owner: Optional[Edge] = None

    @property
    def custom_arrows(self) -> bool:
        """True when the line or its arrowheads differ from the theme's default."""
        return (
            self.width is not None
            or self.arrow_size != 1.0
            or self.ellipsis
            or (self.arrow_head and self.head != "triangle")
            or (self.arrow_tail and self.tail != "triangle")
        )

    @property
    def fixed_route(self) -> bool:
        """True when the author laid the line out, so the layout must not move it."""
        return bool(self.manual_waypoints or self.via or self.trunk is not None)

    @property
    def routing(self) -> Routing:
        """Routing strategy for edges."""
        if self._routing is not None:
            return self._routing
        if self._resolved_style is not None:
            return self._resolved_style.routing
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
        return self.corner_radius

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


def may_share_a_line(e1: Any, e2: Any, links: set[tuple[int, int]]) -> bool:
    """True if drawing ``e1`` and ``e2`` along one line misleads nobody.

    That holds for a fan-out from one source, a fan-in to one target, and a bus
    on which every source feeds every target, so that the merged line implies
    only connections that exist. ``links`` is the set of
    ``(id(source), id(target))`` pairs of every edge in the diagram.
    """
    if e1.source is e2.source or e1.target is e2.target:
        return True
    return (id(e1.source), id(e2.target)) in links and (id(e2.source), id(e1.target)) in links
