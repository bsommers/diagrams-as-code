"""Pure-Python standalone SVG renderer for IIoT diagrams."""
from __future__ import annotations

import html
import re
from typing import Any, Optional, Sequence

from iiot_diagrams.connections import Edge
from iiot_diagrams.elements import Element, Shape
from iiot_diagrams.groups import Group
from iiot_diagrams.router import OrthogonalRouter
from iiot_diagrams.shapes import ShapeLibrary
from iiot_diagrams.theme import Theme


class SVGRenderer:
    """Renderer converting diagram elements, groups, and edges into crisp SVG XML."""

    def __init__(self, theme: Theme) -> None:
        self.theme = theme
        self.shapes = ShapeLibrary()
        self.router = OrthogonalRouter()

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

    def render(
        self,
        elements: Optional[Sequence[Element]] = None,
        groups: Optional[Sequence[Group]] = None,
        edges: Optional[Sequence[Edge]] = None,
        width: float = 1200.0,
        height: float = 800.0,
    ) -> str:
        """Render elements, groups, and edges into an SVG document string."""
        element_list = list(elements) if elements is not None else []
        group_list = list(groups) if groups is not None else []
        edge_list = list(edges) if edges is not None else []

        # 1. Collect markers for defs
        arrow_markers: dict[str, str] = {"arrow": self.theme.accent}
        tail_markers: dict[str, str] = {}

        for e in edge_list:
            edge_color = e.color or self.theme.edge_color
            m_id = self._marker_id_for_color(edge_color)
            if e.arrow_head and m_id not in arrow_markers:
                arrow_markers[m_id] = edge_color
            if e.arrow_tail:
                tail_id = f"{m_id}-tail"
                tail_markers[tail_id] = edge_color

        lines: list[str] = [
            f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}">',
            "  <defs>",
        ]

        # Render arrowhead markers
        for m_id, m_color in arrow_markers.items():
            lines.append(
                f'    <marker id="{m_id}" viewBox="0 0 10 10" refX="8" refY="5" '
                f'markerWidth="6" markerHeight="6" orient="auto-start-reverse">'
            )
            lines.append(f'      <path d="M 0 1 L 10 5 L 0 9 z" fill="{m_color}"/>')
            lines.append("    </marker>")

        # Render arrowtail markers
        for t_id, t_color in tail_markers.items():
            lines.append(
                f'    <marker id="{t_id}" viewBox="0 0 10 10" refX="2" refY="5" '
                f'markerWidth="6" markerHeight="6" orient="auto">'
            )
            lines.append(f'      <path d="M 10 1 L 0 5 L 10 9 z" fill="{t_color}"/>')
            lines.append("    </marker>")

        # Render shadow filter
        lines.append(
            '    <filter id="shadow" x="-10%" y="-10%" width="120%" height="120%">'
        )
        lines.append(
            '      <feDropShadow dx="0" dy="4" stdDeviation="6" flood-color="#000000" flood-opacity="0.4"/>'
        )
        lines.append("    </filter>")
        lines.append("  </defs>")

        # Canvas background fill
        lines.append(
            f'  <rect width="100%" height="100%" fill="{self.theme.background}"/>'
        )

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
            g_meta = getattr(g, "metadata", {}) or {}
            g_fill = g_meta.get("fill", self.theme.group_bg)
            g_stroke = g_meta.get("stroke", self.theme.group_stroke)
            lines.append(f'  <g id="{escaped_g_id}">')
            lines.append(
                f'    <rect x="{b.x}" y="{b.y}" width="{b.width}" height="{b.height}" rx="8" '
                f'fill="{g_fill}" stroke="{g_stroke}" stroke-width="1.5" />'
            )
            if g.label:
                lines.append(
                    f'    <text x="{b.x + 16}" y="{b.y + 24}" fill="{self.theme.accent}" '
                    f'font-family="{self.theme.font_family}" font-size="14" font-weight="bold">{html.escape(g.label)}</text>'
                )
            lines.append("  </g>")

        # 3. Render Edges
        for e in edge_list:
            pts = self.router.route(e)
            if len(pts) < 2:
                continue

            path_d = f"M {pts[0].x} {pts[0].y} " + " ".join(
                f"L {p.x} {p.y}" for p in pts[1:]
            )
            edge_color = e.color or self.theme.edge_color
            dash = (
                ' stroke-dasharray="5,5"'
                if e.style == "dashed"
                else (' stroke-dasharray="2,2"' if e.style == "dotted" else "")
            )

            m_id = self._marker_id_for_color(edge_color)
            marker_end = f' marker-end="url(#{m_id})"' if e.arrow_head else ""
            marker_start = (
                f' marker-start="url(#{m_id}-tail)"' if e.arrow_tail else ""
            )

            lines.append(
                f'  <path d="{path_d}" fill="none" stroke="{edge_color}" stroke-width="2"{dash}{marker_start}{marker_end} />'
            )

            # Centered protocol badge so edge lines don't cross text
            if e.label:
                mid_idx = len(pts) // 2
                lx = (pts[mid_idx - 1].x + pts[mid_idx].x) / 2.0
                ly = (pts[mid_idx - 1].y + pts[mid_idx].y) / 2.0
                edge_meta = getattr(e, "metadata", {}) or {}
                badge_fill = edge_meta.get("badge_fill", self.theme.node_fill)
                badge_text_color = edge_meta.get(
                    "badge_text_color", self.theme.text
                )
                font_size = float(edge_meta.get("font_size", 10.0))
                badge_h = float(edge_meta.get("badge_height", 18.0))
                char_w = font_size * 0.62
                badge_w = max(len(e.label) * char_w + 16.0, 24.0)
                bx = lx - badge_w / 2.0
                by = ly - badge_h / 2.0
                badge_svg = self.shapes.render_badge(
                    bx,
                    by,
                    e.label,
                    fill=badge_fill,
                    text_color=badge_text_color,
                    font_size=font_size,
                    height=badge_h,
                    font_family=self.theme.font_family,
                )
                lines.append(f"  {badge_svg}")

        # 4. Render Shapes
        for el in element_list:
            b = el.bounds
            escaped_el_id = html.escape(el.id, quote=True)
            lines.append(f'  <g id="{escaped_el_id}" filter="url(#shadow)">')

            kind_raw = getattr(el, "kind", "box")
            kind = (kind_raw or "box").lower().replace("-", "_")

            fill = el.metadata.get("fill", self.theme.node_fill)
            stroke = el.metadata.get("stroke", self.theme.node_stroke)
            stroke_width = float(el.metadata.get("stroke_width", 2.0))

            if kind == "box":
                radius = float(el.metadata.get("radius", 6.0))
                lines.append(
                    f"    {self.shapes.render_box(b.x, b.y, b.width, b.height, fill, stroke, stroke_width, radius=radius)}"
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
            text_color = el.metadata.get("text_color")
            if text_color is None:
                if fill != self.theme.node_fill:
                    text_color = self._contrast_color(fill)
                else:
                    text_color = self.theme.text

            # Render embedded icon and label
            icon_name = getattr(el, "icon", None)
            if icon_name:
                icon_size = float(
                    el.metadata.get(
                        "icon_size", min(24.0, max(16.0, b.height * 0.4))
                    )
                )
                icon_color = str(
                    el.metadata.get("icon_color", self.theme.accent)
                )
                if el.label:
                    icon_x = b.center.x - icon_size / 2.0
                    icon_y = b.y + max(4.0, (b.height - icon_size - 18.0) / 2.0)
                    lines.append(
                        f"    {self.shapes.render_icon(icon_name, icon_x, icon_y, size=icon_size, color=icon_color)}"
                    )
                    text_y = icon_y + icon_size + 14.0
                    lines.append(
                        f'    <text x="{b.center.x}" y="{text_y}" text-anchor="middle" '
                        f'fill="{text_color}" font-family="{self.theme.font_family}" '
                        f'font-size="12" font-weight="500">{html.escape(el.label)}</text>'
                    )
                else:
                    icon_x = b.center.x - icon_size / 2.0
                    icon_y = b.center.y - icon_size / 2.0
                    lines.append(
                        f"    {self.shapes.render_icon(icon_name, icon_x, icon_y, size=icon_size, color=icon_color)}"
                    )
            elif el.label:
                lines.append(
                    f'    <text x="{b.center.x}" y="{b.center.y + 4}" text-anchor="middle" '
                    f'fill="{text_color}" font-family="{self.theme.font_family}" '
                    f'font-size="13" font-weight="500">{html.escape(el.label)}</text>'
                )

            lines.append("  </g>")

        lines.append("</svg>")
        return "\n".join(lines)
