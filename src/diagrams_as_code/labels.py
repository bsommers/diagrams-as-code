"""Where a node's label goes and how large it is.

One place decides this so layout, drawing and the visual audit always agree.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional

from diagrams_as_code.geometry import Rect
from diagrams_as_code.text import TextBlock, TextStyle, layout

#: Font sizes tried, largest first, for a label drawn inside its shape.
INSIDE_SIZES = (13.0, 12.0, 11.0, 10.0)
#: Font sizes tried for a label drawn below its shape.
BELOW_SIZES = (12.0, 11.0)
INSIDE_WEIGHT = 500
BELOW_WEIGHT = 600

PAD_X = 6.0  # clear space left and right of an inside label
PAD_Y = 3.0  # clear space above and below an inside label (and its icon)
ICON_GAP = 2.0  # between an icon and the label under it
BELOW_GAP = 2.0  # between a shape's bottom edge and a label drawn below it
BELOW_MIN_WIDTH = 100.0  # a below-label may be at least this wide before wrapping

LINE_HEIGHT = 1.2  # of the font size, for node labels

BADGE_FONT_SIZE = 10.0
BADGE_WEIGHT = 600
BADGE_PAD_X = 8.0


@dataclass(frozen=True)
class NodeLabel:
    """A node's label, laid out."""

    position: str  # "inside" | "bottom"
    block: Optional[TextBlock]
    icon_size: float  # 0 when the node has no icon
    fits: bool  # False when even the smallest size overflows the shape
    needed_width: float  # shape size that would make the label fit
    needed_height: float

    @property
    def content_height(self) -> float:
        """Height of icon plus label when stacked inside the shape."""
        text = self.block.height if self.block else 0.0
        gap = ICON_GAP if (self.icon_size and self.block) else 0.0
        return self.icon_size + gap + text


def label_position(shape: Any) -> str:
    """'inside' or 'bottom' for ``shape``."""
    kind = shape_kind(shape)
    pos = getattr(shape, "label_position", "auto")
    if pos == "auto":
        return "bottom" if kind == "icon" else "inside"
    return "bottom" if pos in ("below", "bottom") else "inside"


#: Kinds whose artwork fills the body; an inside label gets a plain plate behind it.
PLATE_KINDS = frozenset({"server_rack", "database"})


def shape_kind(shape: Any) -> str:
    return (getattr(shape, "kind", "box") or "box").lower().replace("-", "_")


def label_area(shape: Any) -> Rect:
    """The part of ``shape`` an inside label (and its icon) may occupy.

    It leaves out the artwork of the shape's kind: the rim of a cylinder, the
    lobes of a cloud, the corners of a diamond. Layout, drawing and the audit
    all use it, so a label that fits here is clear of the outline.
    """
    b = shape.bounds
    kind = shape_kind(shape)
    if kind == "cylinder":
        ry = min(12.0, b.height / 4.0)
        return Rect(b.x, b.y + 2.0 * ry, b.width, max(b.height - 2.5 * ry, 1.0))
    if kind == "database":
        tiers = max(1, int(getattr(shape, "metadata", {}).get("num_tiers", 3)))
        ry = min(12.0, b.height / (tiers * 2.0))
        return Rect(b.x, b.y + 2.0 * ry, b.width, max(b.height - 2.5 * ry, 1.0))
    if kind == "cloud":
        return Rect(b.x + 0.14 * b.width, b.y + 0.34 * b.height, 0.72 * b.width, 0.5 * b.height)
    if kind == "diamond":
        # A rectangle inscribed in a rhombus: its width and height shares sum to one.
        return Rect(b.x + 0.18 * b.width, b.y + 0.32 * b.height, 0.64 * b.width, 0.36 * b.height)
    return b


def _fit(
    text: str, max_width: float, max_height: float, sizes: tuple[float, ...], weight: int
) -> tuple[TextBlock, bool]:
    block = None
    for size in sizes:
        block = layout(
            text, TextStyle(size=size, weight=weight, line_height=LINE_HEIGHT), max_width=max_width
        )
        if block.width <= max_width + 0.01 and block.height <= max_height + 0.01:
            return block, True
    assert block is not None
    return block, False


def inside_icon_size(shape: Any) -> float:
    if not getattr(shape, "icon", None):
        return 0.0
    h = shape.bounds.height
    return float(shape.metadata.get("icon_size", min(24.0, max(16.0, h * 0.38))))


def _sizes(shape: Any, default: tuple[float, ...]) -> tuple[float, ...]:
    """Font sizes to try: the shape's own ``font_size`` if it set one."""
    pinned = getattr(shape, "metadata", {}).get("font_size")
    return (float(pinned),) if pinned else default


def node_label(shape: Any) -> NodeLabel:
    """Lay out the label of ``shape`` for its current size."""
    b = shape.bounds
    text = getattr(shape, "label", "") or ""
    position = label_position(shape)
    if position == "bottom":
        if not text:
            return NodeLabel(position, None, 0.0, True, b.width, b.height)
        block, _ = _fit(text, max(b.width, BELOW_MIN_WIDTH), float("inf"), _sizes(shape, BELOW_SIZES), BELOW_WEIGHT)
        return NodeLabel(position, block, 0.0, True, b.width, b.height)

    icon = inside_icon_size(shape)
    if not text:
        return NodeLabel(position, None, icon, True, b.width, b.height)
    chrome = icon + (ICON_GAP if icon else 0.0)
    area = label_area(shape)
    max_w = max(area.width - 2 * PAD_X, 1.0)
    max_h = max(area.height - 2 * PAD_Y - chrome, 1.0)
    block, fits = _fit(text, max_w, max_h, _sizes(shape, INSIDE_SIZES), INSIDE_WEIGHT)
    # The artwork takes the same share of a larger shape, so scale the need up.
    share_w = area.width / b.width if b.width > 0 else 1.0
    share_h = area.height / b.height if b.height > 0 else 1.0
    return NodeLabel(
        position,
        block,
        icon,
        fits,
        needed_width=max(b.width, (block.width + 2 * PAD_X) / max(share_w, 0.1)),
        needed_height=max(b.height, (block.height + chrome + 2 * PAD_Y) / max(share_h, 0.1)),
    )


def below_label_extent(shape: Any) -> tuple[float, float]:
    """(width, height) a label drawn below ``shape`` occupies, gap included."""
    nl = node_label(shape)
    if nl.position != "bottom" or nl.block is None:
        return (0.0, 0.0)
    return (nl.block.width, BELOW_GAP + nl.block.height)


def badge_block(label: str, font_size: float = BADGE_FONT_SIZE,
                max_width: Optional[float] = None) -> TextBlock:
    """The text of an edge label badge, wrapped at ``max_width`` if given."""
    return layout(label, TextStyle(size=font_size, weight=BADGE_WEIGHT), max_width)


def badge_size(label: str, font_size: float = BADGE_FONT_SIZE, height: float = 18.0,
               padding_x: float = BADGE_PAD_X, max_width: Optional[float] = None) -> tuple[float, float]:
    """(width, height) of an edge label badge."""
    block = badge_block(label, font_size, max_width)
    return (max(block.width + 2.0 * padding_x, 24.0), max(height, block.height + 4.0))


def edge_badge_rect(edge: Any, path: Any) -> Optional[Rect]:
    """The box of an edge's label badge, or ``None`` if the edge draws none.

    An edge draws no badge when it has no label, or when the layout let it share
    the badge of another edge carrying the same label along a common trunk
    (``edge._label_owner``). Otherwise the badge is centred on the anchor the
    layout chose (``edge._label_anchor``), or on the path's own midpoint when no
    layout ran, and its text is wrapped at ``edge._label_wrap`` if that is set.
    """
    if not getattr(edge, "label", None) or getattr(edge, "_label_owner", None) is not None:
        return None
    meta = getattr(edge, "metadata", {}) or {}
    w, h = badge_size(
        edge.label,
        float(meta.get("font_size", BADGE_FONT_SIZE)),
        float(meta.get("badge_height", 18.0)),
        max_width=getattr(edge, "_label_wrap", None),
    )
    anchor = getattr(edge, "_label_anchor", None)
    x, y = (anchor.x, anchor.y) if anchor is not None else path.label_anchor()
    return Rect(x - w / 2.0, y - h / 2.0, w, h)
