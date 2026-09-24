"""Diagram context manager and fluent syntax engine."""
from __future__ import annotations

import dataclasses
from pathlib import Path
from typing import Any, Literal, Optional, Sequence, Union

from diagrams_as_code import context, rasterize
from diagrams_as_code.bom import BOMGenerator
from diagrams_as_code.connections import Edge, Port, Routing
from diagrams_as_code.constraints import ConstraintSolver
from diagrams_as_code.elements import Element, Shape
from diagrams_as_code.geometry import Anchor, Point, Size, UnitBasis
from diagrams_as_code.groups import Group
from diagrams_as_code.layout.layered import DIRECTIONS
from diagrams_as_code.layout.pipeline import run_layout
from diagrams_as_code.renderer_svg import SVGRenderer
from diagrams_as_code.theme import Theme, get_theme


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
        routing: Union[Routing, str] = Routing.ORTHOGONAL,
        metadata: Optional[dict[str, Any]] = None,
    ) -> None:
        self.diagram = diagram
        self.label = label
        self.color = color
        self.style = style
        self.source_port = source_port
        self.target_port = target_port
        self.arrow_head = arrow_head
        self.arrow_tail = arrow_tail
        self.routing = routing
        self.metadata = dict(metadata) if metadata else {}
        self.source: Any = None

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

        sources: list[Element]
        if isinstance(self.source, (list, tuple)):
            for s in self.source:
                if not isinstance(s, Element):
                    raise TypeError(
                        f"Expected Element in sources, got {type(s).__name__}"
                    )
            sources = list(self.source)
        elif isinstance(self.source, Element):
            sources = [self.source]
        else:
            raise TypeError(
                f"Expected Element or sequence of Elements as source, got {type(self.source).__name__}"
            )

        targets: list[Element]
        if isinstance(target, (list, tuple)):
            for t in target:
                if not isinstance(t, Element):
                    raise TypeError(
                        f"Expected Element in targets, got {type(t).__name__}"
                    )
            targets = list(target)
        elif isinstance(target, Element):
            targets = [target]
        else:
            raise TypeError(
                f"Expected Element or sequence of Elements as target, got {type(target).__name__}"
            )

        diag = self.diagram
        if diag is None:
            for s in sources:
                if getattr(s, "_diagram", None) is not None:
                    diag = s._diagram
                    break
        if diag is None:
            for t in targets:
                if getattr(t, "_diagram", None) is not None:
                    diag = t._diagram
                    break
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
                        metadata=self.metadata,
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
                        metadata=self.metadata,
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
        width: float = 1200.0,
        height: float = 800.0,
        theme: Union[Theme, str] = "iiot_dark_gold",
        theme_overrides: Optional[dict[str, str]] = None,
        label_position: str = "inside",
        layout: str = "manual",
        direction: str = "LR",
        layout_file: Optional[Union[str, Path]] = None,
        rank_gap: float = 80.0,
        node_gap: float = 40.0,
    ) -> None:
        self.title = title
        self.width = float(width)
        self.height = float(height)
        base_t = get_theme(theme)
        if theme_overrides:
            self.theme = dataclasses.replace(
                base_t, name=f"{base_t.name}_custom", **theme_overrides
            )
        else:
            self.theme = base_t
        self.label_position = label_position
        self.shapes: list[Shape] = []
        self.groups: list[Group] = []
        self.edges: list[Edge] = []
        self.routes: dict[int, list[Point]] = {}
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
        )

    def configure(
        self,
        *,
        layout: Optional[str] = None,
        direction: Optional[str] = None,
        theme: Optional[Union[Theme, str]] = None,
        layout_file: Optional[Union[str, Path]] = None,
        rank_gap: Optional[float] = None,
        node_gap: Optional[float] = None,
    ) -> Diagram:
        """Change layout or theme settings; layout changes re-solve on next render."""
        if layout is not None and layout not in self.LAYOUT_MODES:
            raise ValueError(f"layout must be one of {self.LAYOUT_MODES}, got {layout!r}")
        if direction is not None and direction not in DIRECTIONS:
            raise ValueError(f"direction must be one of {DIRECTIONS}, got {direction!r}")
        for name, gap in (("rank_gap", rank_gap), ("node_gap", node_gap)):
            if gap is not None and gap < 0:
                raise ValueError(f"{name} must be non-negative, got {gap}")
        if theme is not None:
            self.theme = get_theme(theme)
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
        routing: Union[Routing, str] = Routing.ORTHOGONAL,
        metadata: Optional[dict[str, Any]] = None,
    ) -> _EdgeBuilder:
        """Return an edge builder for fluent >> chaining."""
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
            metadata=metadata,
        )

    def connect(
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
    ) -> Edge:
        """Directly connect two elements with an Edge and record it."""
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
            metadata=metadata,
        )
        self.edges.append(e)
        return e

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

    def render_svg(self, path: Optional[Union[str, Path]] = None) -> str:
        """Render diagram to SVG string and optionally write to file."""
        if not self._is_solved:
            self.solve()
        renderer = SVGRenderer(self.theme)
        svg = renderer.render(
            elements=self.shapes,
            groups=self.groups,
            edges=self.edges,
            width=self.width,
            height=self.height,
            routes=self.routes,
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
        if not self._is_solved:
            self.solve()
        return self.bom.generate_readme(
            image_file=image_file,
            diagram_name=self.title,
            output_path=output_path,
            include_connections=include_connections,
        )
