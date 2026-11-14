"""Technical-drawing primitives: free text, captions, brackets, polygons, paths,
projected solids and layer bands.

Each one is a ``Shape`` that describes its own artwork as drawing items, so it
can be positioned, nested, grouped and connected like any other shape.
"""
from __future__ import annotations

from typing import Any, Optional, Sequence, Union

from diagrams_as_code import drawing, solids
from diagrams_as_code.drawing import DrawItem, PathItem, TextItem
from diagrams_as_code.elements import Element, Shape, SpanConstraint
from diagrams_as_code.geometry import Point, Rect, to_px
from diagrams_as_code.groups import Group
from diagrams_as_code.style import Style
from diagrams_as_code.text import TextBlock, TextStyle, layout

PointLike = Union[Point, Sequence[float]]

__all__ = [
    "Band",
    "Bracket",
    "Caption",
    "Path",
    "Polygon",
    "Polyline",
    "Primitive",
    "SolidShape",
    "Text",
]


class Primitive(Shape):
    """A shape that draws itself. Not listed in the bill of materials."""

    annotation = True

    def __init__(self, id: str, label: str = "", width: float = 0.0, height: float = 0.0,
                 kind: str = "primitive", **kwargs: Any) -> None:
        kwargs.setdefault("fit_label", False)
        super().__init__(id, label, width=width, height=height, kind=kind, **kwargs)

    def _resize(self, width: float, height: float) -> None:
        self.width, self.height = float(width), float(height)
        self.bounds = Rect(self.bounds.x, self.bounds.y, self.width, self.height)

    def _font(self, theme: Any, role: str) -> str:
        return theme.serif_family if role == "serif" else theme.font_family

    def draw(self, style: Style, theme: Any) -> list[DrawItem]:
        raise NotImplementedError


class Text(Primitive):
    """Text with no box around it; its size is the size of the text.

    The text takes the label markup: ``**bold**``, ``*italic*``, ``$math$`` and
    ``\\n``. ``max_width`` wraps it. ``font`` is ``"sans"`` or ``"serif"``.
    """

    def __init__(
        self,
        id: str,
        text: str,
        *,
        size: float = 13.0,
        bold: bool = False,
        italic: bool = False,
        font: str = "sans",
        align: str = "left",
        max_width: Optional[float] = None,
        color: Optional[str] = None,
        small_caps: bool = False,
        line_height: float = 1.25,
        padding: float = 0.0,
        **kwargs: Any,
    ) -> None:
        if align not in ("left", "center", "right"):
            raise ValueError(f"align must be left, center or right, got {align!r}")
        if font not in ("sans", "serif"):
            raise ValueError(f"font must be 'sans' or 'serif', got {font!r}")
        kwargs.setdefault("kind", "text")
        super().__init__(id, text, **kwargs)
        self.size = to_px(size)
        self.bold, self.italic, self.small_caps = bool(bold), bool(italic), bool(small_caps)
        self.font, self.align, self.color = font, align, color
        self.max_width = None if max_width is None else to_px(max_width)
        self.line_height = float(line_height)
        #: Clear space kept around the text, so a line to it stops short of the letters.
        self.padding = to_px(padding)
        self.prepare()

    @property
    def block(self) -> TextBlock:
        style = TextStyle(
            size=self.size, bold=self.bold, italic=self.italic,
            line_height=self.line_height, small_caps=self.small_caps,
        )
        return layout(self.label or "", style, self.max_width)

    def prepare(self) -> None:
        block = self.block
        self._resize(block.width + 2.0 * self.padding, block.height + 2.0 * self.padding)

    def draw(self, style: Style, theme: Any) -> list[DrawItem]:
        if not self.label:
            return []
        b, pad = self.bounds, self.padding
        x, anchor = {
            "left": (b.x + pad, "start"), "center": (b.center.x, "middle"), "right": (b.right - pad, "end"),
        }[self.align]
        return [
            TextItem(
                self.block, x, b.y + pad, anchor=anchor, valign="top",
                fill=self.color or style.text_color or theme.text,
                font_family=self._font(theme, self.font),
                # The bundled metrics describe the sans face; pin serif runs to them.
                precise=self.font == "serif",
            )
        ]


class Caption(Text):
    """A figure caption. Unless positioned, it is centred under the whole drawing."""

    obstacle = False

    def __init__(self, id: str, text: str, *, gap: float = 28.0, **kwargs: Any) -> None:
        kwargs.setdefault("font", "serif")
        kwargs.setdefault("size", 15.0)
        kwargs.setdefault("align", "center")
        kwargs.setdefault("kind", "caption")
        super().__init__(id, text, **kwargs)
        #: Space between the drawing and the caption.
        self.gap = to_px(gap)

    @property
    def floating(self) -> bool:  # type: ignore[override]
        return not self.constraints


class Bracket(Primitive):
    """A brace, square bracket or parenthesis along one side of what it groups.

    ``side`` is where the bracket sits relative to its content, so
    ``Bracket(..., side="right")`` opens to the left. ``spanning(a, b)`` sizes
    and places it against two elements; ``length`` sizes it by hand.
    """

    SHAPES = ("curly", "square", "round")
    LABEL_GAP = 6.0

    def __init__(
        self,
        id: str,
        label: str = "",
        *,
        length: float = 80.0,
        side: str = "right",
        shape: str = "curly",
        depth: float = 10.0,
        font_size: float = 12.0,
        **kwargs: Any,
    ) -> None:
        if side not in ("left", "right", "top", "bottom"):
            raise ValueError(f"side must be left, right, top or bottom, got {side!r}")
        if shape not in self.SHAPES:
            raise ValueError(f"shape must be one of {self.SHAPES}, got {shape!r}")
        kwargs.setdefault("kind", "bracket")
        super().__init__(id, label, **kwargs)
        self.side, self.shape = side, shape
        self.depth, self.font_size = to_px(depth), to_px(font_size)
        self.length = to_px(length)
        self.prepare()

    @property
    def _label_block(self) -> Optional[TextBlock]:
        return layout(self.label, TextStyle(size=self.font_size)) if self.label else None

    def set_length(self, length: float) -> None:
        self.length = float(length)
        self.prepare()

    def prepare(self) -> None:
        block = self._label_block
        extra_w = block.width + self.LABEL_GAP if block else 0.0
        extra_h = block.height + self.LABEL_GAP if block else 0.0
        if self.side in ("left", "right"):
            self._resize(self.depth + extra_w, max(self.length, block.height if block else 0.0))
        else:
            self._resize(max(self.length, block.width if block else 0.0), self.depth + extra_h)

    def spanning(self, first: Element, last: Optional[Element] = None, gap: float = 8.0) -> Bracket:
        """Run the bracket along ``first`` .. ``last`` on this bracket's side."""
        self.constraints.append(
            SpanConstraint(target=first, other=last, side=self.side, gap=to_px(gap))
        )
        return self

    def _outline(self) -> tuple[drawing.Command, ...]:
        """The bracket with its open ends at v=0 and its back at v=depth, along u."""
        d, n = self.depth, self.length
        if self.shape == "square":
            return drawing.polyline([(0, 0), (0, d), (n, d), (n, 0)])
        if self.shape == "round":
            return (("M", 0.0, 0.0), ("C", n * 0.2, d * 1.33, n * 0.8, d * 1.33, n, 0.0))
        h = d / 2.0
        q = min(h * 1.6, n / 4.0)
        m = n / 2.0
        return (
            ("M", 0.0, 0.0),
            ("C", 0.0, h, 0.0, h, q, h),
            ("L", m - q, h),
            ("C", m, h, m, h, m, d),
            ("C", m, h, m, h, m + q, h),
            ("L", n - q, h),
            ("C", n, h, n, h, n, 0.0),
        )

    def draw(self, style: Style, theme: Any) -> list[DrawItem]:
        b = self.bounds
        block = self._label_block

        def place(u: float, v: float) -> tuple[float, float]:
            if self.side == "right":
                return (b.x + v, b.y + (b.height - self.length) / 2.0 + u)
            if self.side == "left":
                return (b.right - v, b.y + (b.height - self.length) / 2.0 + u)
            if self.side == "bottom":
                return (b.x + (b.width - self.length) / 2.0 + u, b.y + v)
            return (b.x + (b.width - self.length) / 2.0 + u, b.bottom - v)

        commands = tuple(
            (c[0], *[v for i in range(1, len(c), 2) for v in place(c[i], c[i + 1])])
            for c in self._outline()
        )
        stroke = style.stroke if style.stroke and style.stroke != "none" else theme.text
        items: list[DrawItem] = [
            PathItem(commands, stroke=stroke, stroke_width=style.stroke_width or 1.0,
                     dash=style.dash or "", linejoin="round")
        ]
        if block is not None:
            color = style.text_color or theme.text
            family = theme.font_family
            if self.side == "right":
                items.append(TextItem(block, b.right, b.center.y, "end", "middle", color, family))
            elif self.side == "left":
                items.append(TextItem(block, b.x, b.center.y, "start", "middle", color, family))
            elif self.side == "bottom":
                items.append(TextItem(block, b.center.x, b.bottom, "middle", "bottom", color, family))
            else:
                items.append(TextItem(block, b.center.x, b.y, "middle", "top", color, family))
        return items


class Path(Primitive):
    """A free path given as SVG path data, in its own coordinates.

    Until positioned it is drawn where its coordinates say; ``at()`` and the
    relative placements move its bounding box. The label, if any, is centred
    on that box.
    """

    FILLED = True
    self_placed = True

    def __init__(self, id: str, d: Union[str, Sequence[drawing.Command]], label: str = "",
                 *, font_size: float = 12.0, **kwargs: Any) -> None:
        kwargs.setdefault("kind", "path")
        super().__init__(id, label, **kwargs)
        commands = drawing.parse_path(d) if isinstance(d, str) else tuple(d)
        if not commands:
            raise ValueError("a path needs at least one command")
        box = drawing.commands_bbox(commands)
        #: The outline with its bounding box at the origin.
        self.commands = drawing.translate(commands, -box.x, -box.y)
        self.font_size = to_px(font_size)
        self._resize(box.width, box.height)
        self.bounds = Rect(box.x, box.y, box.width, box.height)

    def draw(self, style: Style, theme: Any) -> list[DrawItem]:
        b = self.bounds
        fill = style.fill if self.FILLED and style.fill not in (None, "none", "transparent") else None
        items: list[DrawItem] = [
            PathItem(
                drawing.translate(self.commands, b.x, b.y),
                fill=fill,
                stroke=None if style.stroke in (None, "none") else style.stroke,
                stroke_width=style.stroke_width if style.stroke_width is not None else 1.0,
                dash=style.dash or "",
                fill_opacity=style.fill_opacity,
                linejoin="round",
            )
        ]
        if self.label:
            block = layout(self.label, TextStyle(size=self.font_size))
            items.append(
                TextItem(block, b.center.x, b.center.y, fill=style.text_color or theme.text,
                         font_family=theme.font_family)
            )
        return items


class Polygon(Path):
    """A closed outline through ``points``, filled."""

    def __init__(self, id: str, points: Sequence[PointLike], label: str = "", **kwargs: Any) -> None:
        if len(points) < 3:
            raise ValueError("a polygon needs at least three points")
        kwargs.setdefault("kind", "polygon")
        super().__init__(id, drawing.polyline(points, closed=True), label, **kwargs)


class Polyline(Path):
    """An open line through ``points``; never filled."""

    FILLED = False

    def __init__(self, id: str, points: Sequence[PointLike], label: str = "", **kwargs: Any) -> None:
        if len(points) < 2:
            raise ValueError("a polyline needs at least two points")
        kwargs.setdefault("kind", "polyline")
        super().__init__(id, drawing.polyline(points), label, **kwargs)


class SolidShape(Primitive):
    """A convex solid in parallel projection, hidden edges dashed.

    ``scale`` is pixels per model unit. ``cut`` is an optional ``(point,
    normal)`` plane: its section through the solid is outlined and a patch of
    the plane is drawn through it. The label is set underneath.
    """

    LABEL_GAP = 6.0

    def __init__(
        self,
        id: str,
        solid: solids.Solid,
        label: str = "",
        *,
        projection: Optional[solids.Projection] = None,
        scale: float = 1.0,
        hidden: str = "dashed",
        face_opacity: float = 1.0,
        cut: Optional[tuple[solids.Vec3, solids.Vec3]] = None,
        cut_size: Optional[float] = None,
        cut_fill: str = "#888888",
        font_size: float = 12.0,
        **kwargs: Any,
    ) -> None:
        if hidden not in ("dashed", "none", "solid"):
            raise ValueError(f"hidden must be dashed, none or solid, got {hidden!r}")
        kwargs.setdefault("kind", "solid")
        super().__init__(id, label, **kwargs)
        self.solid = solid
        self.projection = projection or solids.oblique()
        self.scale = float(scale)
        self.hidden = hidden
        self.face_opacity = float(face_opacity)
        self.cut, self.cut_size, self.cut_fill = cut, cut_size, cut_fill
        self.font_size = to_px(font_size)
        self.prepare()

    def _geometry(self) -> tuple[list[solids.ProjectedFace], list[solids.ProjectedEdge], list[Point], list[Point]]:
        faces, edges = self.solid.project(self.projection, self.scale)
        plane: list[Point] = []
        section: list[Point] = []
        if self.cut is not None:
            point, normal = self.cut
            section = solids.section_points(self.solid, point, normal, self.projection, self.scale)
            if self.cut_size:
                plane = solids.plane_points(point, normal, self.cut_size, self.projection, self.scale)
        return faces, edges, plane, section

    def _extent(self) -> Rect:
        faces, _, plane, _ = self._geometry()
        pts = [p for f in faces for p in f.points] + plane
        xs, ys = [p.x for p in pts], [p.y for p in pts]
        return Rect(min(xs), min(ys), max(xs) - min(xs), max(ys) - min(ys))

    def prepare(self) -> None:
        box = self._extent()
        self._resize(box.width, box.height)

    def draw(self, style: Style, theme: Any) -> list[DrawItem]:
        faces, edges, plane, section = self._geometry()
        box = self._extent()
        dx, dy = self.bounds.x - box.x, self.bounds.y - box.y

        def moved(points: Sequence[Point], closed: bool = True) -> tuple[drawing.Command, ...]:
            return drawing.polyline([(p.x + dx, p.y + dy) for p in points], closed)

        stroke = style.stroke or theme.node_stroke
        width = style.stroke_width if style.stroke_width is not None else 1.0
        fill = None if style.fill in (None, "none", "transparent") else style.fill
        opacity = style.fill_opacity if style.fill_opacity is not None else self.face_opacity
        items: list[DrawItem] = []
        if fill:
            # Seen faces only when opaque; every face when you can see through them.
            items += [
                PathItem(moved(f.points), fill=fill, fill_opacity=opacity)
                for f in faces
                if f.front or opacity < 1.0
            ]
        if self.hidden != "none":
            items += [
                PathItem(moved([e.a, e.b], False), stroke=stroke, stroke_width=width * 0.75,
                         dash="4,3" if self.hidden == "dashed" else "", linecap="round")
                for e in edges
                if not e.visible
            ]
        if plane:
            items.append(PathItem(moved(plane), fill=self.cut_fill, fill_opacity=0.25,
                                  stroke=stroke, stroke_width=width * 0.75, linejoin="round"))
        if section:
            items.append(PathItem(moved(section), fill=self.cut_fill, fill_opacity=0.35,
                                  stroke=stroke, stroke_width=width * 0.75, dash="2,2", linejoin="round"))
        items += [
            PathItem(moved([e.a, e.b], False), stroke=stroke, stroke_width=width, linecap="round")
            for e in edges
            if e.visible
        ]
        if self.label:
            block = layout(self.label, TextStyle(size=self.font_size))
            items.append(
                TextItem(block, self.bounds.center.x, self.bounds.bottom + self.LABEL_GAP,
                         valign="top", fill=style.text_color or theme.text, font_family=theme.font_family)
            )
        return items


class Band(Group):
    """A layer of a figure: a dashed frame with a bold title and optional side notes.

    Notes are set in a column of ``note_width`` down one side, outside the
    content area. ``min_width``/``min_height`` let a stack of bands share a size.
    """

    NOTE_SIZE = 11.0
    NOTE_GAP = 8.0

    def __init__(
        self,
        id: str,
        label: str,
        *,
        notes: Union[str, Sequence[str], None] = None,
        note_width: float = 150.0,
        note_side: str = "right",
        min_width: float = 0.0,
        min_height: float = 0.0,
        padding: float = 20.0,
        header_height: float = 34.0,
        metadata: Optional[dict[str, Any]] = None,
        style: Optional[Style] = None,
        child_style: Optional[Style] = None,
    ) -> None:
        if note_side not in ("left", "right"):
            raise ValueError(f"note_side must be 'left' or 'right', got {note_side!r}")
        base = Style(fill="none", radius=0.0, dash="6,4", stroke_width=1.0)
        super().__init__(id, label, padding=padding, header_height=header_height,
                         metadata=metadata, style=base.merged(style), child_style=child_style)
        self.notes: list[str] = [notes] if isinstance(notes, str) else list(notes or [])
        self.note_width, self.note_side = to_px(note_width), note_side
        self.min_width, self.min_height = to_px(min_width), to_px(min_height)

    def note(self, text: str) -> Band:
        """Add a side note."""
        self.notes.append(text)
        return self

    @property
    def _note_column(self) -> float:
        return self.note_width + self.padding if self.notes else 0.0

    def note_blocks(self) -> list[TextBlock]:
        style = TextStyle(size=self.NOTE_SIZE, italic=True)
        return [layout(n, style, self.note_width) for n in self.notes]

    def calculate_bounds(self) -> Rect:
        if not self.is_auto_sized or not self.children:
            return self.bounds
        b = super().calculate_bounds()
        column = self._note_column
        notes_h = sum(k.height for k in self.note_blocks()) + self.NOTE_GAP * max(len(self.notes) - 1, 0)
        width = max(b.width + column, self.min_width)
        height = max(b.height, self.min_height, notes_h + self.header_height + self.padding if self.notes else 0.0)
        x = b.x - column if self.note_side == "left" else b.x
        self.bounds = Rect(x, b.y, width, height)
        self.width, self.height = width, height
        return self.bounds

    def note_items(self, theme: Any) -> list[DrawItem]:
        """The side notes, stacked and centred down their column."""
        blocks = self.note_blocks()
        if not blocks:
            return []
        b = self.bounds
        total = sum(k.height for k in blocks) + self.NOTE_GAP * (len(blocks) - 1)
        top = b.y + self.header_height
        y = top + max((b.bottom - self.padding - top - total) / 2.0, 0.0)
        x = b.x + self.padding if self.note_side == "left" else b.right - self.padding - self.note_width
        items: list[DrawItem] = []
        for block in blocks:
            items.append(TextItem(block, x, y, "start", "top", theme.subtext, theme.font_family))
            y += block.height + self.NOTE_GAP
        return items
