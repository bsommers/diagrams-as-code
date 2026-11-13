"""Pure-Python standalone SVG renderer for IIoT diagrams."""
from __future__ import annotations

import html
import math
import re
from typing import Any, Mapping, Optional, Sequence

import dataclasses

from diagrams_as_code import drawing
from diagrams_as_code.connections import Edge, Routing
from diagrams_as_code.elements import Element, Shape
from diagrams_as_code.geometry import PathKind, Point, Rect, RoutedPath, flatten
from diagrams_as_code.groups import Group
from diagrams_as_code.renderer_interactive import InteractiveOverlay
from diagrams_as_code.style import resolve_group_style, resolve_node_style
from diagrams_as_code.labels import (
    BELOW_GAP,
    GROUP_TITLE_BASELINE,
    ICON_GAP,
    PLATE_KINDS,
    badge_size,
    edge_badge_rect,
    group_title_block,
    label_area,
    label_valign,
    node_label,
    shape_kind,
)
from diagrams_as_code.metrics import wrap_text
from diagrams_as_code.text import TextStyle, layout
from diagrams_as_code.shapes import ShapeLibrary
from diagrams_as_code.theme import Theme


def _num(value: Any) -> str:
    """A number as SVG text: no trailing ``.0``, at most three decimals."""
    number = round(float(value), 3)
    return str(int(number)) if number == int(number) else repr(number)


#: Attributes whose values are lengths or coordinates.
_NUMERIC_ATTRS = (
    "x|y|x1|y1|x2|y2|cx|cy|r|rx|ry|width|height|d|points|transform|dx|dy|"
    "stroke-width|font-size|viewBox|opacity|fill-opacity"
)
_ATTR_RE = re.compile(rf'(?<=\s)({_NUMERIC_ATTRS})="([^"]*)"')
_DECIMAL_RE = re.compile(r"-?\d+\.\d+(?:[eE][-+]?\d+)?")
_TRANSFORM_RE = re.compile(r"(\w+)\(([^)]*)\)")


def fix_precision(markup: str, places: int = 2) -> str:
    """``markup`` with every coordinate and length rounded to ``places`` decimals.

    Only numeric attributes are touched, never text content or names, so a
    label such as "p < 0.00125" is left as written. Scale and rotation factors
    in a ``transform`` keep four more places, since a glyph scale of 0.013
    rounded to 0.01 would shrink the glyph by a quarter. Trailing zeros are
    dropped and a negative zero is written as 0.
    """
    def rounded(text: str, digits: int) -> str:
        value = round(float(text), digits)
        out = f"{value:.{digits}f}".rstrip("0").rstrip(".") if digits > 0 else f"{value:.0f}"
        return "0" if out in ("-0", "") else out

    def length(match: re.Match[str]) -> str:
        return rounded(match.group(0), places)

    def factor(match: re.Match[str]) -> str:
        return rounded(match.group(0), places + 4)

    def transform(match: re.Match[str]) -> str:
        # Offsets are lengths; scale and rotation factors need their precision.
        digits = length if match.group(1) == "translate" else factor
        return f"{match.group(1)}({_DECIMAL_RE.sub(digits, match.group(2))})"

    def attribute(match: re.Match[str]) -> str:
        name, value = match.group(1), match.group(2)
        if name == "transform":
            return f'{name}="{_TRANSFORM_RE.sub(transform, value)}"'
        return f'{name}="{_DECIMAL_RE.sub(length, value)}"'

    return _ATTR_RE.sub(attribute, markup)


class SVGRenderer(InteractiveOverlay):
    """Renderer converting diagram elements, groups, and edges into crisp SVG XML."""

    def __init__(self, theme: Theme, precision: int = 2, crisp: bool = False) -> None:
        self.theme = theme
        #: Decimal places kept in coordinates and lengths.
        self.precision = max(0, int(precision))
        #: Shift the drawing half a pixel so odd-width strokes on whole-pixel
        #: coordinates cover whole pixels instead of straddling two.
        self.crisp = bool(crisp)
        self.shapes = ShapeLibrary()

    def _marker_id_for_color(self, color: str) -> str:
        if color == self.theme.accent:
            return "arrow"
        slug = re.sub(r"[^a-zA-Z0-9_-]", "", color)
        return f"arrow-{slug}"

    def _contrast_color(self, hex_color: Any) -> str:
        if not isinstance(hex_color, str):
            return self.theme.text
        clean = hex_color.strip().lstrip("#")
        if len(clean) == 3:
            clean = "".join(ch * 2 for ch in clean)
        if len(clean) == 6:
            try:
                r = int(clean[0:2], 16)
                g = int(clean[2:4], 16)
                b = int(clean[4:6], 16)
                lum = (0.299 * r + 0.587 * g + 0.114 * b) / 255.0
                return "#000000" if lum > 0.55 else "#FFFFFF"
            except ValueError:
                pass
        return self.theme.text

    @staticmethod
    def wrap_text(text: str, max_chars: int = 15) -> list[str]:
        """Break label text into visually balanced lines at word boundaries."""
        return wrap_text(text, max_chars)

    def _group_label(self, label: str, x: float, top: float, indent: str) -> str:
        """A group's title, set on the same baseline as before (24px below its top)."""
        block = group_title_block(label)
        first = block.baselines(0.0)[0]
        return block.to_svg(
            x, top + GROUP_TITLE_BASELINE - first, anchor="start", valign="top",
            fill=self.theme.accent, font_family=self.theme.font_family, indent=indent,
        )

    def render(
        self,
        elements: Optional[Sequence[Element]] = None,
        groups: Optional[Sequence[Group]] = None,
        edges: Optional[Sequence[Edge]] = None,
        width: float = 1200.0,
        height: float = 800.0,
        routes: Optional[Mapping[Any, RoutedPath]] = None,
        interactive: bool = False,
    ) -> str:
        """Render complete SVG string for provided diagram elements and connections."""
        element_list = list(elements) if elements is not None else []
        group_list = list(groups) if groups is not None else []
        edge_list = list(edges) if edges is not None else []

        w_val = int(width) if isinstance(width, (int, float)) and float(width).is_integer() else width
        h_val = int(height) if isinstance(height, (int, float)) and float(height).is_integer() else height

        svg_class = ' class="diagram-interactive"' if interactive else ""
        lines: list[str] = [
            f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w_val} {h_val}" width="{w_val}" height="{h_val}"{svg_class}>',
        ]
        lines.extend(self._defs(edge_list, interactive))

        # Canvas background fill
        lines.append(
            f'  <rect width="100%" height="100%" fill="{self.theme.background}"/>'
        )
        if interactive:
            lines.append('  <g id="diagram-content">')

        # Painted back to front: group frames, edge lines, edge badges, nodes.
        half_pixel = self.crisp and round(float(self.theme.node_stroke_width)) % 2 == 1
        if half_pixel:
            lines.append('  <g transform="translate(0.5 0.5)">')
        # Within the nodes, lower ``z`` first; a negative ``z`` goes under the
        # edges and an edge with a positive ``z`` goes over the nodes.
        # A shape that holds others is a frame, like a group: it also goes under
        # the edges, so a line to a shape inside it is not hidden by its fill.
        ordered = sorted(element_list, key=lambda el: getattr(el, "z", 0.0))

        def backdrop(el: Element) -> bool:
            return getattr(el, "z", 0.0) < 0.0 or bool(getattr(el, "children", None))

        lines.extend(self._groups_pass(group_list, interactive))
        lines.extend(self._nodes_pass([el for el in ordered if backdrop(el)], interactive))
        lines.extend(self._edges_pass([e for e in edge_list if getattr(e, "z", 0.0) <= 0.0], routes, interactive))
        lines.extend(self._nodes_pass([el for el in ordered if not backdrop(el)], interactive))
        lines.extend(self._edges_pass([e for e in edge_list if getattr(e, "z", 0.0) > 0.0], routes, interactive))
        if half_pixel:
            lines.append("  </g>")
        lines = [fix_precision(line, self.precision) for line in lines]

        if interactive:
            lines.append("  </g>")
            lines.extend(self._render_interactive_controls(width, height))
            lines.extend(self._render_interactive_minimap(width, height))
            lines.extend(self._render_interactive_script(width, height))

        lines.append("</svg>")
        return "\n".join(lines)

    def _defs(self, edge_list: Sequence[Edge], interactive: bool) -> list[str]:
        """Arrow markers for every edge colour, the shadow filter, interactive styles."""
        # Marker size is in stroke widths; keep arrowheads readable on hairlines.
        edge_w = max(float(self.theme.edge_width), 0.1)
        marker = _num(6.0 * max(edge_w, 1.5) / edge_w)
        lines: list[str] = [
            "  <defs>",
            f'    <marker id="arrow" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="{marker}" markerHeight="{marker}" orient="auto-start-reverse">',
            f'      <path d="M 0 1 L 10 5 L 0 9 z" fill="{self.theme.accent}"/>',
            "    </marker>",
            f'    <marker id="arrow-tail" viewBox="0 0 10 10" refX="2" refY="5" markerWidth="{marker}" markerHeight="{marker}" orient="auto">',
            f'      <path d="M 10 1 L 0 5 L 10 9 z" fill="{self.theme.accent}"/>',
            "    </marker>",
        ]

        # Register dynamic colored arrow markers for distinct edge styles
        registered_colors = {self.theme.accent}
        for e in edge_list:
            c = e.color or self.theme.edge_color
            if c not in registered_colors:
                registered_colors.add(c)
                m_id = self._marker_id_for_color(c)
                lines.append(
                    f'    <marker id="{m_id}" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="{marker}" markerHeight="{marker}" orient="auto-start-reverse">'
                )
                lines.append(
                    f'      <path d="M 0 1 L 10 5 L 0 9 z" fill="{c}"/>'
                )
                lines.append("    </marker>")
                lines.append(
                    f'    <marker id="{m_id}-tail" viewBox="0 0 10 10" refX="2" refY="5" markerWidth="{marker}" markerHeight="{marker}" orient="auto">'
                )
                lines.append(
                    f'      <path d="M 10 1 L 0 5 L 10 9 z" fill="{c}"/>'
                )
                lines.append("    </marker>")

        lines.append('    <filter id="shadow" x="-10%" y="-10%" width="120%" height="120%">')
        lines.append(
            '      <feDropShadow dx="0" dy="4" stdDeviation="6" flood-color="#000000" flood-opacity="0.4"/>'
        )
        lines.append("    </filter>")
        if interactive:
            lines.append('    <clipPath id="minimap-clip"><rect x="0" y="0" width="160" height="100" rx="6"/></clipPath>')
            lines.append(self._render_interactive_styles())
        lines.append("  </defs>")
        return lines

    def _groups_pass(self, group_list: Sequence[Group], interactive: bool) -> list[str]:
        """Group frames and titles, outermost first."""
        lines: list[str] = []
        # 2. Render Groups (hierarchically: outermost parent groups first)
        def _get_depth(g: Group) -> int:
            d = 0
            curr = g.parent
            while curr is not None:
                d += 1
                curr = curr.parent
            return d

        sorted_groups = sorted(group_list, key=_get_depth)
        for g in sorted_groups:
            b = g.bounds
            escaped_g_id = html.escape(g.id, quote=True)
            g_style = resolve_group_style(self.theme, g)
            g_fill, g_stroke = g_style.fill, g_style.stroke
            g_frame = f'rx="{_num(g_style.radius)}" fill="{g_fill}" stroke="{g_stroke}" stroke-width="{_num(g_style.stroke_width)}"'
            if g_style.dash:
                g_frame += f' stroke-dasharray="{g_style.dash}"'
            if interactive:
                p_attr = f' data-parent-group="{html.escape(g.parent.id, quote=True)}"' if g.parent is not None else ""
                h_h = getattr(g, "header_height", 35.0)
                g_label = html.escape(g.label or "", quote=True)
                lines.append(
                    f'  <g id="{escaped_g_id}" class="diagram-group" data-group-id="{escaped_g_id}" '
                    f'data-label="{g_label}" '
                    f'data-collapsed="false" data-orig-height="{b.height}" data-header-height="{h_h}"{p_attr}>'
                )
                lines.append(
                    f'    <rect class="group-box" x="{b.x}" y="{b.y}" width="{b.width}" height="{b.height}" '
                    f'{g_frame} />'
                )
                lines.append(f'    <g class="group-header" data-group-id="{escaped_g_id}">')
                lines.append(
                    f'      <rect x="{b.x}" y="{b.y}" width="{b.width}" height="{h_h}" rx="8" fill="transparent" />'
                )
                lines.append(
                    f'      <text class="group-toggle" x="{b.x + 14}" y="{b.y + 22}">▼</text>'
                )
                if g.label:
                    lines.append(self._group_label(g.label, b.x + 32, b.y, "      "))
                lines.append("    </g>")
                lines.extend(self._group_notes(g, "    "))
                lines.append("  </g>")
            else:
                lines.append(f'  <g id="{escaped_g_id}">')
                lines.append(
                    f'    <rect x="{b.x}" y="{b.y}" width="{b.width}" height="{b.height}" '
                    f'{g_frame} />'
                )
                if g.label:
                    lines.append(self._group_label(g.label, b.x + 16, b.y, "    "))
                lines.extend(self._group_notes(g, "    "))
                lines.append("  </g>")
        return lines

    def _group_notes(self, g: Group, indent: str) -> list[str]:
        """Side notes of a band, if the group has any."""
        notes = getattr(g, "note_items", None)
        return drawing.items_svg(notes(self.theme), indent) if notes is not None else []

    def _custom_edge(self, e: Edge, path: RoutedPath, color: str, dash: str) -> list[str]:
        """An edge whose weight or arrowheads are its own: heads drawn as shapes.

        The line stops short of each filled head so its square end does not
        show through the point. With ``ellipsis`` the middle is three dots.
        """
        width = float(e.width if e.width is not None else self.theme.edge_width)
        length = drawing.arrow_length(width, e.arrow_size)
        pts = list(path.points)
        ends: list[tuple[Point, Point, str]] = []  # tip, direction, style
        flat = flatten(path)

        def direction(a: Point, b: Point) -> Point:
            return Point(b.x - a.x, b.y - a.y)

        def distinct(points: list[Point]) -> Point:
            return next((p for p in points[1:] if p.distance_to(points[0]) > 1e-6), points[0])

        if e.arrow_head and e.head != "none":
            ends.append((flat[-1], direction(distinct(flat[::-1]), flat[-1]), e.head))
            pts[-1] = self._pulled_back(pts[-1], distinct(pts[::-1]), drawing.arrow_trim(e.head, length))
        if e.arrow_tail and e.tail != "none":
            ends.append((flat[0], direction(distinct(flat), flat[0]), e.tail))
            pts[0] = self._pulled_back(pts[0], distinct(pts), drawing.arrow_trim(e.tail, length))
        line = dataclasses.replace(path, points=tuple(pts))
        attrs = f'fill="none" stroke="{color}" stroke-width="{_num(width)}"{dash}'
        out: list[str] = []
        if e.ellipsis:
            # Centre the dots on the whole line, not on what is left after trimming.
            skew = (path.points[-1].distance_to(pts[-1]) - path.points[0].distance_to(pts[0])) / 2.0
            before, dots, after = self._ellipsis(flatten(line), max(6.0, 3.0 * width), skew)
            for part in (before, after):
                if len(part) >= 2:
                    out.append(f'<path d="{drawing.svg_d(drawing.polyline(part))}" {attrs} />')
            radius = max(1.25, 0.75 * width)
            out += [drawing.PathItem(drawing.ellipse(p.x, p.y, radius), fill=color).to_svg() for p in dots]
        else:
            out.append(f'<path d="{line.svg_d()}" {attrs} />')
        for tip, toward, style in ends:
            out += drawing.items_svg(drawing.arrowhead(tip, toward, style, length, color, width))
        return out

    @staticmethod
    def _pulled_back(end: Point, neighbour: Point, distance: float) -> Point:
        """``end`` moved ``distance`` towards ``neighbour``, at most most of the way."""
        span = end.distance_to(neighbour)
        if distance <= 0.0 or span <= 1e-6:
            return end
        t = min(distance, 0.9 * span) / span
        return Point(end.x + (neighbour.x - end.x) * t, end.y + (neighbour.y - end.y) * t)

    @staticmethod
    def _ellipsis(
        pts: list[Point], pitch: float, skew: float = 0.0
    ) -> tuple[list[Point], list[Point], list[Point]]:
        """Split a polyline around its middle: (before, three dot centres, after).

        ``skew`` moves the middle along the line, towards its end when positive.
        """
        lengths = [a.distance_to(b) for a, b in zip(pts, pts[1:])]
        total = sum(lengths)
        gap = min(4.0 * pitch, total * 0.6)

        def at(distance: float) -> tuple[Point, int]:
            run = 0.0
            for i, seg in enumerate(lengths):
                if run + seg >= distance and seg > 0.0:
                    t = (distance - run) / seg
                    a, b = pts[i], pts[i + 1]
                    return Point(a.x + (b.x - a.x) * t, a.y + (b.y - a.y) * t), i
                run += seg
            return pts[-1], len(pts) - 2

        mid = total / 2.0 + skew
        start, i0 = at(mid - gap / 2.0)
        stop, i1 = at(mid + gap / 2.0)
        step = gap / 4.0
        dots = [at(mid + k * step)[0] for k in (-1, 0, 1)]
        return pts[: i0 + 1] + [start], dots, [stop] + pts[i1 + 1 :]

    def _edge_path(self, e: Edge, routes: Optional[Mapping[Any, RoutedPath]]) -> RoutedPath:
        """The path to draw for ``e``.

        Normally the route the layout produced. An edge drawn without a layout
        (the renderer called directly) falls back to its own waypoints, or to a
        straight line between its ports.
        """
        path: Optional[RoutedPath] = None
        if routes is not None:
            path = routes.get(e) or routes.get(id(e))
        if path is None:
            path = getattr(e, "_resolved_path", None)
        if path is not None:
            return path

        waypoints = getattr(e, "manual_waypoints", None) or getattr(e, "waypoints", None)
        if waypoints:
            kind = PathKind.BEZIER_CHAIN if e.routing in (Routing.CURVE, "curve") else PathKind.POLYLINE
            return RoutedPath(kind, tuple(waypoints), corner_radius=float(e.corner_radius or 0.0))

        src_b = getattr(getattr(e, "source", None), "bounds", None)
        tgt_b = getattr(getattr(e, "target", None), "bounds", None)
        if src_b is None or tgt_b is None:
            raise ValueError(f"No route provided for edge {e}")

        def port_point(box: Rect, port: Any) -> Point:
            return box.get_anchor(port.to_anchor()) if hasattr(port, "to_anchor") else box.center

        return RoutedPath(
            PathKind.POLYLINE,
            (port_point(src_b, getattr(e, "source_port", None)), port_point(tgt_b, getattr(e, "target_port", None))),
        )

    def _edges_pass(
        self, edge_list: Sequence[Edge], routes: Optional[Mapping[Any, RoutedPath]], interactive: bool
    ) -> list[str]:
        """Edge lines, then their badges on top so no line strikes through a label."""
        lines: list[str] = []
        # 3. Render Edges
        def _get_group_id(elem: Any) -> Optional[str]:
            if isinstance(elem, Group):
                return elem.id
            if getattr(elem, "parent", None) is not None:
                return elem.parent.id
            return None

        badge_layer: list[str] = []
        for e in edge_list:
            path = self._edge_path(e, routes)
            if len(path.points) < 2:
                continue

            path_d = path.svg_d()
            edge_color = e.color or self.theme.edge_color
            dash = (
                ' stroke-dasharray="5,5"'
                if e.style == "dashed"
                else (' stroke-dasharray="2,2"' if e.style == "dotted" else "")
            )

            m_id = self._marker_id_for_color(edge_color)
            marker_end = f' marker-end="url(#{m_id})"' if e.arrow_head and e.head != "none" else ""
            marker_start = (
                f' marker-start="url(#{m_id}-tail)"' if e.arrow_tail and e.tail != "none" else ""
            )
            custom = self._custom_edge(e, path, edge_color, dash) if getattr(e, "custom_arrows", False) else None

            if interactive:
                src_gid = _get_group_id(e.source)
                tgt_gid = _get_group_id(e.target)
                src_id = getattr(e.source, "id", "")
                tgt_id = getattr(e.target, "id", "")
                edge_attrs = ""
                if src_id:
                    edge_attrs += f' data-source-id="{html.escape(src_id, quote=True)}"'
                if tgt_id:
                    edge_attrs += f' data-target-id="{html.escape(tgt_id, quote=True)}"'
                if src_gid:
                    edge_attrs += f' data-source-group="{html.escape(src_gid, quote=True)}"'
                if tgt_gid:
                    edge_attrs += f' data-target-group="{html.escape(tgt_gid, quote=True)}"'
                lines.append(f'  <g class="diagram-edge"{edge_attrs}>')
                if custom is not None:
                    lines.extend(f"    {part}" for part in custom)
                else:
                    lines.append(
                        f'    <path d="{path_d}" fill="none" stroke="{edge_color}" stroke-width="{_num(self.theme.edge_width)}"{dash}{marker_start}{marker_end} />'
                    )
            elif custom is not None:
                lines.extend(f"  {part}" for part in custom)
            else:
                lines.append(
                    f'  <path d="{path_d}" fill="none" stroke="{edge_color}" stroke-width="{_num(self.theme.edge_width)}"{dash}{marker_start}{marker_end} />'
                )

            # Centered protocol badge so edge lines don't cross text
            badge_rect = edge_badge_rect(e, path)
            if badge_rect is not None:
                edge_meta = getattr(e, "metadata", {}) or {}
                badge_fill = edge_meta.get("badge_fill", self.theme.node_fill)
                badge_text_color = edge_meta.get(
                    "badge_text_color", self.theme.text
                )
                font_size = float(edge_meta.get("font_size", 10.0))
                bx, by, badge_h = badge_rect.x, badge_rect.y, badge_rect.height
                badge_svg = self.shapes.render_badge(
                    bx,
                    by,
                    e.label,
                    fill=badge_fill,
                    text_color=badge_text_color,
                    font_size=font_size,
                    height=badge_h,
                    font_family=self.theme.font_family,
                    max_width=getattr(e, "_label_wrap", None),
                )
                if interactive:
                    # Kept with its edge so collapsing a group hides both together.
                    lines.append(f"    {badge_svg}")
                else:
                    badge_layer.append(f"  {badge_svg}")

            if interactive:
                lines.append("  </g>")

        # Badges go above every edge line, so no line strikes through a label.
        lines.extend(badge_layer)
        return lines

    def _nodes_pass(self, element_list: Sequence[Element], interactive: bool) -> list[str]:
        """Node shapes with their icons and labels."""
        lines: list[str] = []
        # 4. Render Shapes
        for el in element_list:
            b = el.bounds
            escaped_el_id = html.escape(el.id, quote=True)
            style = resolve_node_style(self.theme, el)
            items = el.draw(style, self.theme) if hasattr(el, "draw") else None
            if items is not None and not items:
                continue  # an element that draws itself and has nothing to show
            node_attrs = ' filter="url(#shadow)"' if style.shadow and items is None else ""
            if style.opacity is not None and style.opacity < 1.0:
                node_attrs += f' opacity="{_num(style.opacity)}"'
            if interactive:
                escaped_label = html.escape(el.label or "", quote=True)
                p_attr = f' data-parent-group="{html.escape(el.parent.id, quote=True)}"' if getattr(el, "parent", None) is not None else ""
                lines.append(
                    f'  <g id="{escaped_el_id}" class="diagram-node" data-node-id="{escaped_el_id}" data-label="{escaped_label}"{p_attr}{node_attrs}>'
                )
            else:
                lines.append(f'  <g id="{escaped_el_id}"{node_attrs}>')

            if items is not None:
                lines.extend(drawing.items_svg(items, "    "))
                lines.append("  </g>")
                continue

            kind_raw = getattr(el, "kind", "box")
            kind = (kind_raw or "box").lower().replace("-", "_")

            label_pos = getattr(el, "label_position", "auto")
            if label_pos == "auto":
                label_pos = "bottom" if kind == "icon" else "inside"
            elif label_pos == "below":
                label_pos = "bottom"

            fill, stroke = style.fill, style.stroke
            stroke_width = _num(style.stroke_width)

            if kind == "icon":
                # Pure icon: no container background box
                pass
            elif kind == "box":
                lines.append(
                    f"    {self.shapes.render_box(b.x, b.y, b.width, b.height, fill, stroke, stroke_width, radius=_num(style.radius), dash=style.dash or '', fill_opacity=style.fill_opacity)}"
                )
                gap = float(style.double or 0.0)
                if gap > 0.0 and b.width > 2.0 * gap and b.height > 2.0 * gap:
                    # Second border, inset; its corners follow the outer ones.
                    lines.append(
                        f"    {self.shapes.render_box(b.x + gap, b.y + gap, b.width - 2.0 * gap, b.height - 2.0 * gap, 'none', stroke, stroke_width, radius=_num(max(float(style.radius or 0.0) - gap, 0.0)), dash=style.dash or '')}"
                    )
            elif kind == "cylinder":
                lines.append(
                    f"    {self.shapes.render_cylinder(b.x, b.y, b.width, b.height, fill, stroke, stroke_width)}"
                )
            elif kind in ("database", "db"):
                num_tiers = int(el.metadata.get("num_tiers", 3))
                lines.append(
                    f"    {self.shapes.render_database(b.x, b.y, b.width, b.height, fill, stroke, stroke_width, num_tiers=num_tiers)}"
                )
            elif kind in ("server_rack", "rack", "server"):
                num_units = int(el.metadata.get("num_units", 4))
                lines.append(
                    f"    {self.shapes.render_server_rack(b.x, b.y, b.width, b.height, fill, stroke, stroke_width, num_units=num_units)}"
                )
            elif kind == "cloud":
                lines.append(
                    f"    {self.shapes.render_cloud(b.x, b.y, b.width, b.height, fill, stroke, stroke_width)}"
                )
            elif kind in ("diamond", "rhombus", "decision"):
                lines.append(
                    f"    {self.shapes.render_diamond(b.x, b.y, b.width, b.height, fill, stroke, stroke_width)}"
                )
            else:
                lines.append(
                    f"    {self.shapes.render_box(b.x, b.y, b.width, b.height, fill, stroke, stroke_width)}"
                )

            # Determine text color with proper contrast
            text_color = style.text_color
            if text_color is None:
                if label_pos == "bottom" or kind == "icon":
                    text_color = self.theme.text
                elif fill != self.theme.node_fill:
                    text_color = self._contrast_color(fill)
                else:
                    text_color = self.theme.text

            icon_name = getattr(el, "icon", None)
            label = node_label(el)
            family = self.theme.font_family

            if label.position == "bottom":
                # Icon centred in the shape (or alone, for kind="icon"); label underneath.
                if icon_name:
                    if kind == "icon":
                        icon_size = float(
                            el.metadata.get("icon_size", min(36.0, max(24.0, min(b.width, b.height) * 0.6)))
                        )
                        icon_y = b.y + max(2.0, (b.height - icon_size) / 2.0)
                    else:
                        icon_size = float(
                            el.metadata.get("icon_size", min(28.0, max(18.0, b.height * 0.45)))
                        )
                        icon_y = b.center.y - icon_size / 2.0
                    icon_color = str(el.metadata.get("icon_color", self.theme.accent))
                    lines.append(
                        f"    {self.shapes.render_icon(icon_name, b.center.x - icon_size / 2.0, icon_y, size=icon_size, color=icon_color)}"
                    )
                if label.block is not None:
                    lines.append(
                        label.block.to_svg(
                            b.center.x, b.bottom + BELOW_GAP, valign="top",
                            fill=text_color, font_family=family, indent="    ",
                        )
                    )
            else:
                # Icon (if any) stacked above the label, the pair centred in the
                # part of the shape its artwork leaves free.
                area = label_area(el)
                cx = area.center.x
                top = area.y + (area.height - label.content_height) / 2.0
                if label_valign(el) == "top":
                    top = area.y + 6.0 + float(style.double or 0.0)
                if shape_kind(el) in PLATE_KINDS and (icon_name or label.block is not None):
                    # The artwork fills the body: clear a plate for the label to sit on.
                    plate_w = max(label.block.width if label.block is not None else 0.0, label.icon_size) + 12.0
                    plate_w = min(plate_w, b.width - 8.0)
                    plate_h = min(label.content_height + 6.0, b.height - 4.0)
                    lines.append(
                        f'    <rect class="label-plate" x="{cx - plate_w / 2.0}" y="{top - 3.0}" '
                        f'width="{plate_w}" height="{plate_h}" rx="3" fill="{fill}" />'
                    )
                if icon_name:
                    icon_color = str(el.metadata.get("icon_color", self.theme.accent))
                    lines.append(
                        f"    {self.shapes.render_icon(icon_name, cx - label.icon_size / 2.0, top, size=label.icon_size, color=icon_color)}"
                    )
                    top += label.icon_size + (ICON_GAP if label.block is not None else 0.0)
                if label.block is not None:
                    lines.append(
                        label.block.to_svg(
                            cx, top, valign="top",
                            fill=text_color, font_family=family, indent="    ",
                        )
                    )

            lines.append("  </g>")
        return lines
