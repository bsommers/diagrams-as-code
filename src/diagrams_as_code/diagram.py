"""Diagram context manager and fluent syntax engine."""
from __future__ import annotations

import copy
import dataclasses
from pathlib import Path
from typing import Any, Literal, Optional, Sequence, Union

from diagrams_as_code import context, rasterize
from diagrams_as_code.bom import BOMGenerator
from diagrams_as_code.connections import Edge, Port, Routing, _coerce_enum
from diagrams_as_code.constraints import ConstraintSolver
from diagrams_as_code import solids as _solids
from diagrams_as_code.elements import AnchorRef, Element, Junction, Shape
from diagrams_as_code.geometry import Anchor, Point, RoutedPath, Size, UnitBasis, to_px
from diagrams_as_code.groups import Group
from diagrams_as_code.primitives import (
    Band,
    Bracket,
    Caption,
    Path as PathShape,
    Polygon,
    Polyline,
    SolidShape,
    Text,
)
from diagrams_as_code.layout.layered import DIRECTIONS
from diagrams_as_code.layout.pipeline import run_layout
from diagrams_as_code.renderer_svg import SVGRenderer
from diagrams_as_code.style import Style
from diagrams_as_code.theme import Theme, get_theme

#: Nominal canvas used while laying out an axis that is fitted to content afterwards.
DEFAULT_WIDTH = 1200.0
DEFAULT_HEIGHT = 800.0


#: ``Edge`` options that ``edge()`` and ``connect()`` pass straight through.
EDGE_OPTIONS = frozenset(
    {"width", "head", "tail", "arrow_size", "two_way", "via", "trunk", "ellipsis", "z"}
)


class _EdgeBuilder:
    """Intermediate builder for fluent edge syntax (e.g. s1 >> diag.edge(...) >> s2)."""

    _is_edge_builder: bool = True

    def __init__(
        self,
        diagram: Optional[Diagram] = None,
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
        metadata: Optional[dict[str, Any]] = None,
        **options: Any,
    ) -> None:
        self.diagram = diagram
        #: Further ``Edge`` options: width, head, tail, arrow_size, two_way, via, trunk, ellipsis, z.
        for name in options:
            if name not in EDGE_OPTIONS:
                raise TypeError(f"edge() got an unexpected keyword argument {name!r}")
        self.options = dict(options)
        self.label = label
        self.color = color
        self.style = style
        self.source_port = source_port
        self.target_port = target_port
        self.arrow_head = arrow_head
        self.arrow_tail = arrow_tail
        self.routing = _coerce_enum(routing, Routing, "routing", allow_none=True)
        effective_r = corner_radius if corner_radius is not None else arc_radius
        self._corner_radius: Optional[float] = Edge._validate_corner_radius(effective_r)
        self._clearance: Optional[float] = (
            Edge._validate_clearance(clearance) if clearance is not None else None
        )
        self.metadata = dict(metadata) if metadata else {}
        self.source: Any = None

    @property
    def corner_radius(self) -> Optional[float]:
        return self._corner_radius

    @corner_radius.setter
    def corner_radius(self, val: Optional[Union[int, float]]) -> None:
        self._corner_radius = Edge._validate_corner_radius(val)

    @property
    def arc_radius(self) -> Optional[float]:
        return self._corner_radius

    @arc_radius.setter
    def arc_radius(self, val: Optional[Union[int, float]]) -> None:
        self._corner_radius = Edge._validate_corner_radius(val)

    @property
    def clearance(self) -> Optional[float]:
        return self._clearance

    @clearance.setter
    def clearance(self, val: Optional[Union[int, float]]) -> None:
        self._clearance = Edge._validate_clearance(val) if val is not None else None

    def __call__(
        self,
        source: Optional[Any] = None,
        target: Optional[Any] = None,
        clearance: Optional[float] = None,
        **kwargs: Any,
    ) -> Any:
        allowed_kwargs = {
            "source",
            "target",
            "clearance",
            "corner_radius",
            "arc_radius",
            "routing",
        }
        for k in kwargs:
            if k not in allowed_kwargs:
                raise TypeError(f"_EdgeBuilder got unexpected keyword argument {k!r}")

        clone = copy.copy(self)
        call_source = kwargs.get("source", source)
        call_target = kwargs.get("target", target)

        if "clearance" in kwargs:
            clone.clearance = kwargs["clearance"]
        elif clearance is not None:
            clone.clearance = clearance

        effective_r = kwargs.get("corner_radius", kwargs.get("arc_radius"))
        if effective_r is not None or "corner_radius" in kwargs or "arc_radius" in kwargs:
            clone.corner_radius = effective_r

        if "routing" in kwargs:
            clone.routing = _coerce_enum(
                kwargs["routing"], Routing, "routing", allow_none=True
            )

        if call_source is not None:
            clone.source = call_source
        if clone.source is not None and call_target is not None:
            return clone >> call_target
        return clone

    def __rrshift__(self, source: Any) -> _EdgeBuilder:
        """Support fan-in operator when left operand is a list/tuple or element."""
        self.source = source
        return self

    def __rshift__(self, target: Any) -> Any:
        """Finalize edge creation with target element(s)."""
        if self.source is None:
            raise ValueError(
                "EdgeBuilder requires a source before connecting to a target"
            )

        ends = (Element, AnchorRef)
        sources: list[Any]
        if isinstance(self.source, (list, tuple)):
            for s in self.source:
                if not isinstance(s, ends):
                    raise TypeError(
                        f"Expected Element in sources, got {type(s).__name__}"
                    )
            sources = list(self.source)
        elif isinstance(self.source, ends):
            sources = [self.source]
        else:
            raise TypeError(
                f"Expected Element or sequence of Elements as source, got {type(self.source).__name__}"
            )

        targets: list[Any]
        if isinstance(target, (list, tuple)):
            for t in target:
                if not isinstance(t, ends):
                    raise TypeError(
                        f"Expected Element in targets, got {type(t).__name__}"
                    )
            targets = list(target)
        elif isinstance(target, ends):
            targets = [target]
        else:
            raise TypeError(
                f"Expected Element or sequence of Elements as target, got {type(target).__name__}"
            )

        diag = self.diagram
        def owner(end: Any) -> Any:
            return getattr(getattr(end, "element", end), "_diagram", None)

        if diag is None:
            diag = next((owner(s) for s in sources if owner(s) is not None), None)
        if diag is None:
            diag = next((owner(t) for t in targets if owner(t) is not None), None)
        if diag is None:
            diag = Diagram.get_current()

        for s in sources:
            for t in targets:
                if diag is not None:
                    diag.connect(
                        source=s,
                        target=t,
                        label=self.label,
                        color=self.color,
                        style=self.style,
                        source_port=self.source_port,
                        target_port=self.target_port,
                        arrow_head=self.arrow_head,
                        arrow_tail=self.arrow_tail,
                        routing=self.routing,
                        corner_radius=self.corner_radius,
                        clearance=self.clearance,
                        metadata=self.metadata,
                        **self.options,
                    )
                else:
                    Edge(
                        source=s,
                        target=t,
                        label=self.label,
                        color=self.color,
                        style=self.style,
                        source_port=self.source_port,
                        target_port=self.target_port,
                        arrow_head=self.arrow_head,
                        arrow_tail=self.arrow_tail,
                        routing=self.routing,
                        corner_radius=self.corner_radius,
                        clearance=self.clearance,
                        metadata=self.metadata,
                        **self.options,
                    )

        self.source = None
        return target


class _GroupContext:
    """Context manager for hierarchical groups with fluent configuration."""

    def __init__(self, diag: Diagram, group: Group) -> None:
        self.diag = diag
        self.group = group
        self._prev_group: Optional[Group] = None

    def __enter__(self) -> Group:
        self._prev_group = self.diag._active_group
        if self._prev_group is not None:
            self._prev_group.add(self.group)
        self.diag._active_group = self.group
        return self.group

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        self.diag._active_group = self._prev_group
        if self.group.is_auto_sized and self.group.children:
            self.group.calculate_bounds()

    def at(
        self, x: float, y: float, anchor: Union[Anchor, str] = Anchor.TOP_LEFT
    ) -> _GroupContext:
        self.group.at(x, y, anchor=anchor)
        return self

    def right_of(
        self,
        other: Element,
        margin: float = 50.0,
        align: Literal["center", "top", "bottom"] = "top",
    ) -> _GroupContext:
        self.group.right_of(other, margin=margin, align=align)
        return self

    def left_of(
        self,
        other: Element,
        margin: float = 50.0,
        align: Literal["center", "top", "bottom"] = "top",
    ) -> _GroupContext:
        self.group.left_of(other, margin=margin, align=align)
        return self

    def below(
        self,
        other: Element,
        margin: float = 50.0,
        align: Literal["center", "left", "right"] = "left",
    ) -> _GroupContext:
        self.group.below(other, margin=margin, align=align)
        return self

    def above(
        self,
        other: Element,
        margin: float = 50.0,
        align: Literal["center", "left", "right"] = "left",
    ) -> _GroupContext:
        self.group.above(other, margin=margin, align=align)
        return self

    def move_to(
        self, x: float, y: float, anchor: Union[Anchor, str] = Anchor.TOP_LEFT
    ) -> _GroupContext:
        self.group.move_to(x, y, anchor=anchor)
        return self

    def align_with(
        self,
        other: Element,
        align: Literal["center", "left", "right", "top", "bottom"] = "center",
        axis: Literal["horizontal", "vertical", "both", "x", "y"] = "horizontal",
    ) -> _GroupContext:
        self.group.align_with(other, align=align, axis=axis)
        return self

    def flow(self, engine: Any = "vertical", **kwargs: Any) -> _GroupContext:
        self.group.flow(engine, **kwargs)
        return self

    def clear_constraints(self) -> _GroupContext:
        self.group.clear_constraints()
        return self

    def __getattr__(self, name: str) -> Any:
        attr = getattr(self.group, name)
        if callable(attr):

            def wrapper(*args: Any, **kwargs: Any) -> Any:
                res = attr(*args, **kwargs)
                if res is self.group:
                    return self
                return res

            return wrapper
        return attr


class Diagram:
    """Fluent context manager and container for directed diagrams."""

    _active_stack: list[Diagram] = context._ACTIVE
    LAYOUT_MODES = ("manual", "auto")

    @classmethod
    def get_current(cls) -> Optional[Diagram]:
        """Get the innermost active Diagram from the context stack."""
        return context.current()

    def __init__(
        self,
        title: str = "IIoT Architecture",
        width: Optional[float] = None,
        height: Optional[float] = None,
        theme: Union[Theme, str] = "iiot_dark_gold",
        theme_overrides: Optional[dict[str, str]] = None,
        label_position: str = "inside",
        layout: str = "manual",
        direction: str = "LR",
        layout_file: Optional[Union[str, Path]] = None,
        rank_gap: float = 80.0,
        node_gap: float = 40.0,
        interactive: bool = False,
        corner_radius: Optional[float] = None,
        arc_radius: Optional[float] = None,
        clearance: Optional[float] = None,
        routing: Optional[Union[Routing, str]] = None,
        fit_labels: bool = True,
        precision: int = 2,
        pixel_snap: bool = False,
        grid: float = 0.0,
    ) -> None:
        self.title = title
        #: Snap every shape's top-left corner to multiples of this many pixels; 0 is off.
        self.grid = to_px(grid)
        #: Grow shapes whose inside label would otherwise spill out of them.
        self.fit_labels = bool(fit_labels)
        #: Decimal places kept in SVG coordinates.
        self.precision = int(precision)
        #: Round every position and size to whole pixels and draw odd-width
        #: strokes on pixel centres, so hairlines are one crisp pixel wide.
        self.pixel_snap = bool(pixel_snap)
        #: An axis left as ``None`` is fitted to the content after layout; a
        #: given size is a minimum that still grows if content would be clipped.
        self._fit_width = width is None
        self._fit_height = height is None
        self.width = DEFAULT_WIDTH if width is None else float(width)
        self.height = DEFAULT_HEIGHT if height is None else float(height)
        base_t = get_theme(theme)
        if theme_overrides:
            self.theme = dataclasses.replace(
                base_t, name=f"{base_t.name}_custom", **theme_overrides
            )
        else:
            self.theme = base_t
        self.label_position = label_position
        self.interactive = bool(interactive)
        effective_r = corner_radius if corner_radius is not None else arc_radius
        self._corner_radius: Optional[float] = Edge._validate_corner_radius(effective_r)
        self._clearance: Optional[float] = (
            Edge._validate_clearance(clearance) if clearance is not None else None
        )
        self._routing: Optional[Routing] = _coerce_enum(
            routing, Routing, "routing", allow_none=True
        )
        self.shapes: list[Shape] = []
        self.groups: list[Group] = []
        self.edges: list[Edge] = []
        self.routes: dict[Any, RoutedPath] = {}
        self.solver = ConstraintSolver()
        self._active_group: Optional[Group] = None
        self._counter: int = 0
        self._is_solved: bool = False
        self.layout = "manual"
        self.direction = "LR"
        self.layout_file: Optional[Path] = None
        self.rank_gap = 80.0
        self.node_gap = 40.0
        self.configure(
            layout=layout,
            direction=direction,
            layout_file=layout_file,
            rank_gap=rank_gap,
            node_gap=node_gap,
            interactive=interactive,
            clearance=clearance,
            routing=routing,
        )

    @property
    def corner_radius(self) -> Optional[float]:
        """Default corner radius for orthogonal edge fillets in this diagram."""
        return self._corner_radius

    @corner_radius.setter
    def corner_radius(self, val: Optional[Union[int, float]]) -> None:
        self._corner_radius = Edge._validate_corner_radius(val)

    @property
    def arc_radius(self) -> Optional[float]:
        """Backward-compatible alias for corner_radius."""
        return self._corner_radius

    @arc_radius.setter
    def arc_radius(self, val: Optional[Union[int, float]]) -> None:
        self._corner_radius = Edge._validate_corner_radius(val)

    @property
    def clearance(self) -> Optional[float]:
        """Default obstacle clearance buffer for edges in this diagram."""
        return self._clearance

    @clearance.setter
    def clearance(self, val: Optional[Union[int, float]]) -> None:
        self._clearance = Edge._validate_clearance(val) if val is not None else None

    @property
    def routing(self) -> Optional[Routing]:
        """Default routing strategy for edges in this diagram."""
        return self._routing

    @routing.setter
    def routing(self, val: Optional[Union[Routing, str]]) -> None:
        self._routing = _coerce_enum(val, Routing, "routing", allow_none=True)

    def configure(
        self,
        *,
        layout: Optional[str] = None,
        direction: Optional[str] = None,
        theme: Optional[Union[Theme, str]] = None,
        layout_file: Optional[Union[str, Path]] = None,
        rank_gap: Optional[float] = None,
        node_gap: Optional[float] = None,
        interactive: Optional[bool] = None,
        corner_radius: Optional[float] = None,
        arc_radius: Optional[float] = None,
        clearance: Optional[float] = None,
        routing: Optional[Union[Routing, str]] = None,
    ) -> Diagram:
        """Change layout or theme settings; layout changes re-solve on next render."""
        if interactive is not None:
            self.interactive = bool(interactive)
        if layout is not None and layout not in self.LAYOUT_MODES:
            raise ValueError(f"layout must be one of {self.LAYOUT_MODES}, got {layout!r}")
        if direction is not None and direction not in DIRECTIONS:
            raise ValueError(f"direction must be one of {DIRECTIONS}, got {direction!r}")
        for name, gap in (("rank_gap", rank_gap), ("node_gap", node_gap)):
            if gap is not None and gap < 0:
                raise ValueError(f"{name} must be non-negative, got {gap}")
        if theme is not None:
            self.theme = get_theme(theme)
        effective_r = corner_radius if corner_radius is not None else arc_radius
        if effective_r is not None:
            self.corner_radius = Edge._validate_corner_radius(effective_r)
            self._is_solved = False
        if clearance is not None:
            self.clearance = clearance
            self._is_solved = False
        if routing is not None:
            self.routing = routing
            self._is_solved = False
        changes = {
            "layout": layout,
            "direction": direction,
            "layout_file": Path(layout_file) if layout_file is not None else None,
            "rank_gap": float(rank_gap) if rank_gap is not None else None,
            "node_gap": float(node_gap) if node_gap is not None else None,
        }
        for name, value in changes.items():
            if value is not None:
                setattr(self, name, value)
                self._is_solved = False
        return self

    def all_elements(self) -> list[Element]:
        """Every shape and group, groups before their children, in declaration order."""
        return self.solver.all_elements()

    @property
    def unit_basis(self) -> UnitBasis:
        """UnitBasis coordinate converter for this diagram canvas."""
        return UnitBasis(Size(self.width, self.height))

    def __enter__(self) -> Diagram:
        context.push(self)
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        context.pop(self)
        if exc_type is None:
            self.solve()

    def shape(
        self,
        label: str,
        width: float = 130.0,
        height: float = 60.0,
        kind: str = "box",
        icon: Optional[str] = None,
        id: Optional[str] = None,
        metadata: Optional[dict[str, Any]] = None,
        **kwargs: Any,
    ) -> Shape:
        """Create, track, and return a visual Shape node."""
        self._counter += 1
        shape_id = id or f"shape_{self._counter}"
        while any(s.id == shape_id for s in self.shapes):
            self._counter += 1
            shape_id = f"shape_{self._counter}"

        s = Shape(
            id=shape_id,
            label=label,
            width=width,
            height=height,
            kind=kind,
            icon=icon,
            metadata=metadata,
            **kwargs,
        )
        s._diagram = self
        s.explicit_id = id is not None
        self.shapes.append(s)
        self.solver.add(s)
        if self._active_group is not None:
            self._active_group.add(s)
        return s

    def group(
        self,
        label: str,
        padding: float = 25.0,
        header_height: float = 35.0,
        id: Optional[str] = None,
        metadata: Optional[dict[str, Any]] = None,
        style: Optional[Style] = None,
        child_style: Optional[Style] = None,
    ) -> _GroupContext:
        """Create, track, and enter a hierarchical Group context."""
        self._counter += 1
        group_id = id or f"group_{self._counter}"
        while any(g.id == group_id for g in self.groups):
            self._counter += 1
            group_id = f"group_{self._counter}"

        g = Group(
            id=group_id,
            label=label,
            padding=padding,
            header_height=header_height,
            metadata=metadata,
            style=style,
            child_style=child_style,
        )
        g._diagram = self
        g.explicit_id = id is not None
        self.groups.append(g)
        self.solver.add(g)
        return _GroupContext(self, g)

    def edge(
        self,
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
        metadata: Optional[dict[str, Any]] = None,
        **options: Any,
    ) -> _EdgeBuilder:
        """Return an edge builder for fluent >> chaining.

        Further keyword options are those of ``Edge``: ``width``, ``head``,
        ``tail``, ``arrow_size``, ``two_way``, ``via``, ``trunk``, ``ellipsis``, ``z``.
        """
        return _EdgeBuilder(
            diagram=self,
            label=label,
            color=color,
            style=style,
            source_port=source_port,
            target_port=target_port,
            arrow_head=arrow_head,
            arrow_tail=arrow_tail,
            routing=routing,
            corner_radius=corner_radius,
            arc_radius=arc_radius,
            clearance=clearance,
            metadata=metadata,
            **options,
        )

    def connect(
        self,
        source: Any,
        target: Any,
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
        metadata: Optional[dict[str, Any]] = None,
        **options: Any,
    ) -> Edge:
        """Connect two ends with an Edge and record it.

        An end is an element, a point on one (``box.anchor("right", 0.25)``) or
        a bare ``(x, y)``. Further options are those of ``Edge``.
        """
        effective_r = corner_radius if corner_radius is not None else arc_radius
        e = Edge(
            source=source,
            target=target,
            label=label,
            color=color,
            style=style,
            source_port=source_port,
            target_port=target_port,
            arrow_head=arrow_head,
            arrow_tail=arrow_tail,
            routing=routing,
            corner_radius=effective_r,
            clearance=clearance,
            metadata=metadata,
            **options,
        )
        for end in (e.source, e.target):
            if isinstance(end, Junction) and end._diagram is None:
                self._adopt(end, None, "point")
        self.edges.append(e)
        return e

    # ------------------------------------------------------- drawing primitives

    def _adopt(self, element: Shape, id: Optional[str], prefix: str, group: bool = False) -> Any:
        """Give ``element`` an id unique in this diagram and register it."""
        self._counter += 1
        new_id = id or f"{prefix}_{self._counter}"
        while any(s.id == new_id for s in self.shapes):
            self._counter += 1
            new_id = f"{prefix}_{self._counter}"
        element.id = new_id
        element._diagram = self
        element.explicit_id = id is not None
        self.shapes.append(element)
        self.solver.add(element)
        if group and self._active_group is not None:
            self._active_group.add(element)
        return element

    def text(self, text: str, id: Optional[str] = None, **kwargs: Any) -> Text:
        """Free text with no box: a note, a heading, a formula."""
        return self._adopt(Text("_", text, **kwargs), id, "text", group=True)

    def caption(self, text: str, id: Optional[str] = None, **kwargs: Any) -> Caption:
        """A figure caption, centred under the drawing unless you position it."""
        return self._adopt(Caption("_", text, **kwargs), id, "caption")

    def bracket(self, label: str = "", id: Optional[str] = None, **kwargs: Any) -> Bracket:
        """A brace or bracket; ``.spanning(a, b)`` runs it along two elements."""
        return self._adopt(Bracket("_", label, **kwargs), id, "bracket", group=True)

    def polygon(self, points: Sequence[Any], label: str = "", id: Optional[str] = None, **kwargs: Any) -> Polygon:
        """A closed, filled outline through ``points``."""
        return self._adopt(Polygon("_", points, label, **kwargs), id, "polygon", group=True)

    def polyline(self, points: Sequence[Any], id: Optional[str] = None, **kwargs: Any) -> Polyline:
        """An open line through ``points``."""
        return self._adopt(Polyline("_", points, **kwargs), id, "polyline", group=True)

    def path(self, d: str, label: str = "", id: Optional[str] = None, **kwargs: Any) -> PathShape:
        """A free shape from SVG path data."""
        return self._adopt(PathShape("_", d, label, **kwargs), id, "path", group=True)

    def point(self, x: float, y: float, dot: bool = False, id: Optional[str] = None, **kwargs: Any) -> Junction:
        """A point for edges to meet at, drawn as a dot if ``dot``."""
        return self._adopt(Junction("_", x, y, dot=dot, **kwargs), id, "point")

    def solid(self, solid: _solids.Solid, label: str = "", id: Optional[str] = None, **kwargs: Any) -> SolidShape:
        """A convex solid in parallel projection, hidden edges dashed."""
        return self._adopt(SolidShape("_", solid, label, **kwargs), id, "solid", group=True)

    def cuboid(
        self, label: str = "", width: float = 80.0, height: float = 60.0, depth: float = 40.0,
        id: Optional[str] = None, **kwargs: Any,
    ) -> SolidShape:
        """A box drawn in three dimensions; sizes are in pixels."""
        return self.solid(_solids.Solid.box(width, height, depth), label, id=id, **kwargs)

    def band(
        self, label: str, id: Optional[str] = None, **kwargs: Any
    ) -> _GroupContext:
        """A layer band: a dashed frame with a bold title and optional side notes."""
        self._counter += 1
        band_id = id or f"band_{self._counter}"
        while any(g.id == band_id for g in self.groups):
            self._counter += 1
            band_id = f"band_{self._counter}"
        b = Band(band_id, label, **kwargs)
        b._diagram = self
        b.explicit_id = id is not None
        self.groups.append(b)
        self.solver.add(b)
        return _GroupContext(self, b)

    def leader(
        self, text: str, target: Any, at: Sequence[float], *, anchor: Union[Anchor, str] = Anchor.TOP_LEFT,
        head: str = "none", width: float = 0.75, id: Optional[str] = None,
        edge: Optional[dict[str, Any]] = None, **text_options: Any,
    ) -> Text:
        """A note at ``at`` with a thin straight line to ``target``.

        ``target`` is an element, an anchor on one, or a point. ``head`` puts an
        arrowhead or a dot (``"circle"``) on the target end.
        """
        text_options.setdefault("size", 11.0)
        text_options.setdefault("padding", 3.0)
        note = self.text(text, id=id, **text_options).at(at[0], at[1], anchor=anchor)
        options = {"routing": Routing.DIRECT, "width": width, "head": head, "arrow_head": head != "none"}
        options.update(edge or {})
        self.connect(note, target, **options)
        return note

    def fan_out(
        self, source: Any, targets: Sequence[Any], trunk: float = 30.0, **options: Any
    ) -> list[Edge]:
        """Connect ``source`` to each target along one shared trunk that then splits.

        ``trunk`` is how far from the source the line runs before it splits.
        """
        return [self.connect(source, t, trunk=trunk, **options) for t in targets]

    def fan_in(
        self, sources: Sequence[Any], target: Any, trunk: float = 30.0, **options: Any
    ) -> list[Edge]:
        """Connect each source to ``target``, merging ``trunk`` px before it."""
        return [self.connect(s, target, trunk=-abs(float(trunk)), **options) for s in sources]

    def add(
        self, *elements: Union[Element, Edge, Sequence[Union[Element, Edge]]]
    ) -> Any:
        """Add pre-instantiated Shape(s), Group(s), or Edge(s) to diagram."""
        flat: list[Union[Element, Edge]] = []
        for item in elements:
            if isinstance(item, (list, tuple)):
                flat.extend(item)
            elif isinstance(item, (Element, Edge)):
                flat.append(item)
            else:
                raise TypeError(
                    f"Expected Element, Edge, or sequence, got {type(item).__name__}"
                )

        def _register_element(el: Element) -> None:
            el._diagram = self
            if not any(existing.id == el.id for existing in self.solver.elements):
                self.solver.add(el)
            if isinstance(el, Group):
                if el not in self.groups:
                    self.groups.append(el)
                for child in el.children:
                    _register_element(child)
            elif isinstance(el, Shape):
                if el not in self.shapes:
                    self.shapes.append(el)
                if self._active_group is not None and el.parent is None:
                    self._active_group.add(el)

        for item in flat:
            if isinstance(item, Edge):
                if item not in self.edges:
                    self.edges.append(item)
            elif isinstance(item, Element):
                _register_element(item)

        if len(flat) == 1:
            return flat[0]
        return flat

    def solve(self) -> None:
        """Place every element: auto-layout, layout file, constraints, framing."""
        run_layout(self)
        self._is_solved = True
        self._solved_signature = self._signature()

    def _signature(self) -> tuple[Any, ...]:
        """Everything a solve depends on, so a stale solve can be detected."""
        elements = tuple(
            (id(el), el.width, el.height, len(el.constraints), id(el.parent))
            for el in self.solver.all_elements()
        )
        edges = tuple(
            (
                id(e), id(e.source), id(e.target), e.source_port, e.target_port,
                e._routing, e._corner_radius, e._clearance, bool(e.label),
                tuple(e.manual_waypoints) if e.manual_waypoints else None,
                e.source_anchor, e.target_anchor, e.trunk,
                tuple(e.via) if e.via else None,
            )
            for e in self.edges
        )
        return (elements, edges, self.width, self.height, self.grid)

    def _ensure_solved(self) -> None:
        """Solve if never solved, or if the model changed since the last solve."""
        if not self._is_solved or getattr(self, "_solved_signature", None) != self._signature():
            self.solve()

    def render_svg(self, path: Optional[Union[str, Path]] = None) -> str:
        """Render diagram to SVG string and optionally write to file."""
        self._ensure_solved()
        renderer = SVGRenderer(self.theme, precision=self.precision, crisp=self.pixel_snap)
        svg = renderer.render(
            elements=self.shapes,
            groups=self.groups,
            edges=self.edges,
            width=self.width,
            height=self.height,
            routes=self.routes,
            interactive=self.interactive,
        )
        if path is not None:
            p = Path(path)
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(svg, encoding="utf-8")
        return svg

    def render_png(self, path: Union[str, Path]) -> bytes:
        """Render diagram to PNG file using resvg-py, cairosvg, or system converters."""
        svg_content = self.render_svg()
        p = Path(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        return rasterize.svg_to_png(svg_content, p)

    @property
    def bom(self) -> BOMGenerator:
        """Bill of Materials generator for this diagram."""
        return BOMGenerator(self)

    def generate_readme(
        self,
        image_file: str,
        output_path: Union[str, Path] = "README.md",
        include_connections: bool = True,
    ) -> str:
        """Generate living documentation README with diagram graphic link and BOM table."""
        self._ensure_solved()
        return self.bom.generate_readme(
            image_file=image_file,
            diagram_name=self.title,
            output_path=output_path,
            include_connections=include_connections,
        )
