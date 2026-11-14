from __future__ import annotations

from collections.abc import Mapping, MutableMapping
from dataclasses import dataclass, fields, is_dataclass
from typing import Any, Literal, Optional, Union
from diagrams_as_code.geometry import Anchor, Point, Rect, to_px
from diagrams_as_code import context
from diagrams_as_code.drawing import DrawItem, PathItem, ellipse
from diagrams_as_code.style import Style


class Constraint(MutableMapping):
    """Base class for element positioning constraints with dictionary duck-typing."""

    type: str = ""
    _layout_source: Optional[str] = None
    _auto_layout: bool = False

    def __init__(
        self,
        type: str = "",
        _layout_source: Optional[str] = None,
        _auto_layout: bool = False,
        **kwargs: Any,
    ) -> None:
        self.type = type
        self._layout_source = _layout_source
        self._auto_layout = _auto_layout
        for k, v in kwargs.items():
            setattr(self, k, v)

    @property
    def _source(self) -> Optional[str]:
        return self._layout_source

    @_source.setter
    def _source(self, val: Optional[str]) -> None:
        self._layout_source = val

    def _present_fields(self) -> set[str]:
        res = set()
        if is_dataclass(self):
            for f in fields(self):
                if f.name in ("_layout_source", "_auto_layout"):
                    continue
                val = getattr(self, f.name, None)
                if val is not None:
                    res.add(f.name)
        for k, v in self.__dict__.items():
            if k in ("_layout_source", "_auto_layout"):
                continue
            if v is not None:
                res.add(k)
        if self._layout_source is not None:
            res.add("_layout_source")
            res.add("_source")
        if self._auto_layout:
            res.add("_auto_layout")
        return res

    def __getitem__(self, key: str) -> Any:
        if key not in self._present_fields():
            raise KeyError(key)
        return getattr(self, key)

    def __setitem__(self, key: str, value: Any) -> None:
        if key in ("_source", "_layout_source"):
            self._layout_source = value
        elif key == "_auto_layout":
            self._auto_layout = bool(value)
        else:
            setattr(self, key, value)

    def __delitem__(self, key: str) -> None:
        if key in self._present_fields():
            if key in ("_source", "_layout_source"):
                self._layout_source = None
            elif key == "_auto_layout":
                self._auto_layout = False
            else:
                setattr(self, key, None)
        else:
            raise KeyError(key)

    def __contains__(self, key: object) -> bool:
        return key in self._present_fields()

    def get(self, key: str, default: Any = None) -> Any:
        if key not in self._present_fields():
            return default
        return getattr(self, key)

    def __iter__(self):
        return iter(sorted(self._present_fields()))

    def __len__(self) -> int:
        return len(self._present_fields())

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Mapping):
            d_other = dict(other)
            d_self = {
                k: self[k]
                for k in self
                if k != "_source" or "_layout_source" not in d_other
            }
            return d_self == d_other
        return False

    def copy(self) -> Constraint:
        import copy

        return copy.copy(self)

    def to_dict(self) -> dict[str, Any]:
        return {k: self[k] for k in self}

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Constraint:
        ctype = data.get("type")
        source = data.get("_layout_source") or data.get("_source")
        auto = bool(data.get("_auto_layout", False))
        if ctype == "absolute":
            return AbsoluteConstraint(
                x=float(data["x"]),
                y=float(data["y"]),
                anchor=data.get("anchor", Anchor.TOP_LEFT),
                type="absolute",
                _layout_source=source,
                _auto_layout=auto,
            )
        elif ctype == "relative_dir":
            return RelativeConstraint(
                target=data["target"],
                direction=data["direction"],
                margin=float(data.get("margin", 20.0)),
                align=data.get("align", "center"),
                type="relative_dir",
                _layout_source=source,
                _auto_layout=auto,
            )
        elif ctype == "align":
            return AlignConstraint(
                target=data["target"],
                align=data.get("align", "center"),
                axis=data.get("axis", "horizontal"),
                type="align",
                _layout_source=source,
                _auto_layout=auto,
            )
        elif ctype == "inside":
            return InsideConstraint(
                target=data["target"],
                anchor=data.get("anchor", Anchor.CENTER),
                dx=float(data.get("dx", 0.0)),
                dy=float(data.get("dy", 0.0)),
                type="inside",
                _layout_source=source,
                _auto_layout=auto,
            )
        elif ctype == "span":
            return SpanConstraint(
                target=data["target"],
                other=data.get("other"),
                side=data.get("side", "right"),
                gap=float(data.get("gap", 8.0)),
                type="span",
                _layout_source=source,
                _auto_layout=auto,
            )
        c = Constraint(type=ctype or "unknown", _layout_source=source, _auto_layout=auto)
        for k, v in data.items():
            if k not in ("type", "_layout_source", "_source", "_auto_layout"):
                setattr(c, k, v)
        return c


@dataclass(eq=False)
class AbsoluteConstraint(Constraint):
    """Position element absolutely with an anchor point."""

    x: float = 0.0
    y: float = 0.0
    anchor: Union[Anchor, str] = Anchor.TOP_LEFT
    type: str = "absolute"
    _layout_source: Optional[str] = None
    _auto_layout: bool = False


@dataclass(eq=False)
class RelativeConstraint(Constraint):
    """Position element relative to a target element in a specified direction."""

    target: Any = None
    direction: str = "right"
    margin: float = 20.0
    align: str = "center"
    type: str = "relative_dir"
    _layout_source: Optional[str] = None
    _auto_layout: bool = False


@dataclass(eq=False)
class AlignConstraint(Constraint):
    """Align element relative to a target element along an axis."""

    target: Any = None
    align: str = "center"
    axis: str = "horizontal"
    type: str = "align"
    _layout_source: Optional[str] = None
    _auto_layout: bool = False


@dataclass(eq=False)
class InsideConstraint(Constraint):
    """Pin an anchor of the element to the same anchor of ``target``, plus an offset."""

    target: Any = None
    anchor: Union[Anchor, str] = Anchor.CENTER
    dx: float = 0.0
    dy: float = 0.0
    type: str = "inside"
    _layout_source: Optional[str] = None
    _auto_layout: bool = False


@dataclass(eq=False)
class SpanConstraint(Constraint):
    """Sit beside ``target`` .. ``other`` on ``side``, as long as the pair is."""

    target: Any = None
    other: Any = None
    side: str = "right"
    gap: float = 8.0
    type: str = "span"
    _layout_source: Optional[str] = None
    _auto_layout: bool = False


#: Constraint types that place an element from the position of others.
DEPENDENT_TYPES = ("relative_dir", "align", "inside", "span")


def constraint_targets(c: Any) -> list[Any]:
    """The elements a dependent constraint reads its position from."""
    out = [c["target"]]
    if c["type"] == "span" and c.get("other") is not None:
        out.append(c["other"])
    return out


_SIDES = {
    "right": "east", "left": "west", "top": "north", "bottom": "south",
    "east": "east", "west": "west", "north": "north", "south": "south",
    "e": "east", "w": "west", "n": "north", "s": "south",
}


def side_name(side: Any) -> str:
    """'north' | 'south' | 'east' | 'west' for a side given by any of its names."""
    key = str(getattr(side, "value", side)).lower()
    if key not in _SIDES:
        raise ValueError(f"side must be one of left, right, top, bottom, got {side!r}")
    return _SIDES[key]


@dataclass(frozen=True)
class AnchorRef:
    """A point on one side of an element: ``box.anchor("right", 0.25)``.

    ``fraction`` runs from 0 to 1 along the side, top to bottom on the left and
    right sides and left to right on the top and bottom. Use it as either end
    of an edge.
    """

    element: Any
    side: str
    fraction: float = 0.5

    def __post_init__(self) -> None:
        object.__setattr__(self, "side", side_name(self.side))
        if not 0.0 <= float(self.fraction) <= 1.0:
            raise ValueError(f"anchor fraction must be between 0 and 1, got {self.fraction!r}")

    @property
    def point(self) -> Point:
        """Where the anchor is, for the element's current bounds."""
        b, f = self.element.bounds, float(self.fraction)
        if self.side == "east":
            return Point(b.right, b.top + f * b.height)
        if self.side == "west":
            return Point(b.left, b.top + f * b.height)
        if self.side == "north":
            return Point(b.left + f * b.width, b.top)
        return Point(b.left + f * b.width, b.bottom)

    def _connect(self, source: Any, target: Any) -> None:
        diag = self.element._find_diagram()
        if diag is not None:
            diag.connect(source, target)
        else:
            from diagrams_as_code.connections import Edge

            Edge(source, target)

    def __rshift__(self, other: Any) -> Any:
        if getattr(other, "_is_edge_builder", False):
            other.source = self
            return other
        for target in other if isinstance(other, (list, tuple)) else [other]:
            self._connect(self, target)
        return other

    def __rrshift__(self, other: Any) -> Any:
        for source in other if isinstance(other, (list, tuple)) else [other]:
            self._connect(source, self)
        return self


def to_constraint(c: Union[Constraint, dict[str, Any]]) -> Constraint:
    """Coerce a constraint dict or object into a typed Constraint."""
    if isinstance(c, Constraint):
        return c
    if isinstance(c, dict):
        return Constraint.from_dict(c)
    raise TypeError(f"Expected Constraint or dict, got {type(c).__name__}")


class Element:
    """Base class for all diagram elements."""

    #: Edges route around it, and the audit counts lines and badges over it.
    obstacle: bool = True
    #: Drawing aid rather than a component: left out of the bill of materials.
    annotation: bool = False
    #: Placed by the layout after everything else (a caption), not by auto-layout.
    floating: bool = False

    def anchor(self, side: Any, fraction: float = 0.5) -> AnchorRef:
        """A point ``fraction`` of the way along ``side``, to attach an edge to."""
        return AnchorRef(self, side, fraction)

    def prepare(self) -> None:
        """Recompute any size the element derives from its own content."""

    def draw(self, style: Style, theme: Any) -> Optional[list[DrawItem]]:
        """Drawing items for an element that draws itself; ``None`` for ordinary shapes."""
        return None

    def __init__(
        self,
        id: str,
        label: str,
        width: float = 120.0,
        height: float = 60.0,
        metadata: Optional[dict[str, Any]] = None,
        style: Optional[Style] = None,
        z: float = 0.0,
        obstacle: Optional[bool] = None,
        **kwargs: Any,
    ) -> None:
        self.id = id
        self.label = label
        #: How this element is drawn, over the theme and enclosing groups.
        self.style: Optional[Style] = style
        #: Paint order. Below zero is drawn under the edges; otherwise higher is on top.
        self.z = float(z)
        if obstacle is not None:
            self.obstacle = bool(obstacle)
        self.width = to_px(width)
        self.height = to_px(height)
        self.bounds: Rect = Rect(0.0, 0.0, self.width, self.height)
        self.parent: Optional[Element] = None
        self.metadata: dict[str, Any] = dict(metadata) if metadata is not None else {}
        self.metadata.update(kwargs)
        self.constraints: list[Any] = []
        self._diagram: Optional[Any] = None
        self.explicit_id: bool = True

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
        return context.current()

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
                from diagrams_as_code.connections import Edge

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
                    from diagrams_as_code.connections import Edge

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
                    from diagrams_as_code.connections import Edge

                    Edge(source, self)
            return self
        elif isinstance(other, Element):
            diag = self._find_diagram(other)
            if diag is not None:
                diag.connect(other, self)
            else:
                from diagrams_as_code.connections import Edge

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
        label_position: str = "auto",
        metadata: Optional[dict[str, Any]] = None,
        fit_label: Optional[bool] = None,
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
        self.label_position = label_position
        #: Grow the shape when its inside label cannot fit. ``None`` follows the
        #: diagram's ``fit_labels`` setting; ``False`` keeps the size as given.
        self.fit_label = fit_label
        #: Shapes placed inside this one with ``inside()``; they move with it.
        self.children: list[Shape] = []

    def translate(self, dx: float, dy: float) -> None:
        super().translate(dx, dy)
        for child in self.children:
            child.translate(dx, dy)

    def inside(
        self,
        container: Shape,
        anchor: Union[Anchor, str] = Anchor.CENTER,
        dx: float = 0.0,
        dy: float = 0.0,
    ) -> Shape:
        """Nest this shape in ``container``, pinning ``anchor`` of both together.

        ``inside(box)`` centres it; ``inside(box, "top_left", 10, 10)`` puts it
        10 px in from the corner. The shape then moves with its container and
        edges to it may cross the container's outline.
        """
        if container is self or self in _ancestry(container):
            raise ValueError(f"cannot nest '{self.id}' inside itself")
        if not isinstance(container, Shape):
            raise TypeError(f"container must be a Shape, got {type(container).__name__}")
        if self.parent is not None and self in getattr(self.parent, "children", []):
            self.parent.children.remove(self)
        self.parent = container
        container.children.append(self)
        self.constraints.append(
            InsideConstraint(target=container, anchor=anchor, dx=to_px(dx), dy=to_px(dy))
        )
        return self

    def at(
        self, x: float, y: float, anchor: Union[Anchor, str] = Anchor.TOP_LEFT
    ) -> Shape:
        """Position element absolutely with an anchor point."""
        x, y = to_px(x), to_px(y)
        self.constraints.append(
            AbsoluteConstraint(x=float(x), y=float(y), anchor=anchor)
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
        self.translate(float(x) - offset.x - self.bounds.x, float(y) - offset.y - self.bounds.y)
        return self

    def right_of(
        self,
        other: Element,
        margin: float = 20.0,
        align: Literal["center", "top", "bottom"] = "center",
    ) -> Shape:
        """Position element to the right of another element."""
        self.constraints.append(
            RelativeConstraint(
                target=other,
                direction="right",
                margin=float(margin),
                align=align,
            )
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
            RelativeConstraint(
                target=other,
                direction="left",
                margin=float(margin),
                align=align,
            )
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
            RelativeConstraint(
                target=other,
                direction="below",
                margin=float(margin),
                align=align,
            )
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
            RelativeConstraint(
                target=other,
                direction="above",
                margin=float(margin),
                align=align,
            )
        )
        return self

    def align_with(
        self,
        other: Element,
        align: Literal["center", "left", "right", "top", "bottom"] = "center",
        axis: Literal["horizontal", "vertical", "both", "x", "y"] = "horizontal",
    ) -> Shape:
        """Align element relative to another element."""
        self.constraints.append(
            AlignConstraint(
                target=other,
                align=align,
                axis=axis,
            )
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
            label_position=overrides.pop("label_position", self.label_position),
            fit_label=overrides.pop("fit_label", self.fit_label),
            style=overrides.pop("style", self.style),
            **overrides,
        )
        return cloned


def _ancestry(element: Any) -> list[Any]:
    chain: list[Any] = []
    cur = getattr(element, "parent", None)
    while cur is not None and cur not in chain:
        chain.append(cur)
        cur = getattr(cur, "parent", None)
    return chain


class Junction(Shape):
    """A point edges can start, end or meet at; optionally drawn as a dot."""

    obstacle = False
    annotation = True
    self_placed = True

    def __init__(
        self, id: str = "point", x: float = 0.0, y: float = 0.0, dot: bool = False,
        radius: float = 2.5, **kwargs: Any,
    ) -> None:
        super().__init__(id, "", width=0.0, height=0.0, kind="point", fit_label=False, **kwargs)
        self.dot = bool(dot)
        self.radius = float(radius)
        self.bounds = Rect(to_px(x), to_px(y), 0.0, 0.0)

    def draw(self, style: Style, theme: Any) -> list[DrawItem]:
        if not self.dot:
            return []
        color = (self.style.fill if self.style and self.style.fill else None) or theme.edge_color
        return [PathItem(ellipse(self.bounds.x, self.bounds.y, self.radius), fill=color)]
