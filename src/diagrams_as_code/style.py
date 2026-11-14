"""How a node or group is drawn, and where each setting comes from.

A ``Style`` holds only what was set; unset fields are ``None``. Styles are
merged in order, later ones winning:

    theme  ->  enclosing groups' ``child_style`` (outermost first)
           ->  the element's own ``style``
           ->  legacy ``metadata`` keys (``fill``, ``stroke``, ...)

so a whole diagram can be restyled from its theme, a region from its group, and
one element from itself, without touching the others.
"""
from __future__ import annotations

import dataclasses
from dataclasses import dataclass
from typing import Any, Mapping, Optional

from diagrams_as_code.theme import Theme


@dataclass(frozen=True)
class Style:
    """Drawing attributes of a node or group. ``None`` means "inherit"."""

    fill: Optional[str] = None
    stroke: Optional[str] = None
    stroke_width: Optional[float] = None
    #: Corner radius of a box or group; 0 gives square corners.
    radius: Optional[float] = None
    #: SVG dash pattern such as ``"6,4"``; ``""`` forces a solid line.
    dash: Optional[str] = None
    shadow: Optional[bool] = None
    text_color: Optional[str] = None
    font_size: Optional[float] = None
    opacity: Optional[float] = None
    #: Opacity of the fill alone, leaving the outline and text solid.
    fill_opacity: Optional[float] = None
    #: Gap in pixels to a second border drawn inside the first; 0 for a single one.
    double: Optional[float] = None

    def __post_init__(self) -> None:
        for name in ("stroke_width", "radius", "font_size", "double"):
            value = getattr(self, name)
            if value is not None and not (float(value) >= 0.0 and float(value) != float("inf")):
                raise ValueError(f"{name} must be a finite number >= 0, got {value!r}")
        for name in ("opacity", "fill_opacity"):
            value = getattr(self, name)
            if value is not None and not 0.0 <= float(value) <= 1.0:
                raise ValueError(f"{name} must be between 0 and 1, got {value!r}")

    def merged(self, over: Optional[Style]) -> Style:
        """This style with every field ``over`` sets replaced by ``over``'s value."""
        if over is None:
            return self
        changes = {
            f.name: getattr(over, f.name)
            for f in dataclasses.fields(over)
            if getattr(over, f.name) is not None
        }
        return dataclasses.replace(self, **changes) if changes else self

    @classmethod
    def from_metadata(cls, metadata: Optional[Mapping[str, Any]]) -> Style:
        """The style expressed by legacy ``metadata`` keys."""
        meta = metadata or {}
        picked: dict[str, Any] = {}
        for name in ("fill", "stroke", "text_color", "dash"):
            if meta.get(name) is not None:
                picked[name] = str(meta[name])
        for name in ("stroke_width", "radius", "font_size", "opacity", "fill_opacity", "double"):
            if meta.get(name) is not None:
                picked[name] = float(meta[name])
        if meta.get("shadow") is not None:
            picked["shadow"] = bool(meta["shadow"])
        return cls(**picked)


def theme_node_style(theme: Theme) -> Style:
    return Style(
        fill=theme.node_fill,
        stroke=theme.node_stroke,
        stroke_width=theme.node_stroke_width,
        radius=theme.node_radius,
        dash="",
        shadow=theme.shadow,
    )


def theme_group_style(theme: Theme) -> Style:
    return Style(
        fill=theme.group_bg,
        stroke=theme.group_stroke,
        stroke_width=theme.group_stroke_width,
        radius=theme.group_radius,
        dash=theme.group_dash,
        shadow=False,
    )


def _ancestors(element: Any) -> list[Any]:
    """Enclosing groups of ``element``, outermost first."""
    chain: list[Any] = []
    parent = getattr(element, "parent", None)
    while parent is not None and parent not in chain:
        chain.append(parent)
        parent = getattr(parent, "parent", None)
    return chain[::-1]


def resolve_node_style(theme: Theme, element: Any) -> Style:
    """The style ``element`` is drawn with."""
    style = theme_node_style(theme)
    for group in _ancestors(element):
        style = style.merged(getattr(group, "child_style", None))
    style = style.merged(getattr(element, "style", None))
    return style.merged(Style.from_metadata(getattr(element, "metadata", None)))


def resolve_group_style(theme: Theme, group: Any) -> Style:
    """The style the frame of ``group`` is drawn with."""
    style = theme_group_style(theme).merged(getattr(group, "style", None))
    return style.merged(Style.from_metadata(getattr(group, "metadata", None)))
