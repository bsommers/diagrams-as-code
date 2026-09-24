"""Pure-Python standalone SVG renderer for IIoT diagrams."""
from __future__ import annotations

import html
import re
from typing import Any, Mapping, Optional, Sequence

from diagrams_as_code.connections import Edge
from diagrams_as_code.elements import Element, Shape
from diagrams_as_code.geometry import Point
from diagrams_as_code.groups import Group
from diagrams_as_code.metrics import LABEL_BELOW_OFFSET
from diagrams_as_code.router import OrthogonalRouter
from diagrams_as_code.shapes import ShapeLibrary
from diagrams_as_code.theme import Theme


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

    @staticmethod
    def wrap_text(text: str, max_chars: int = 15) -> list[str]:
        """Break label text into visually balanced lines at word boundaries."""
        if not text:
            return []
        words = text.split()
        if not words:
            return []
        lines: list[str] = []
        curr: list[str] = []
        curr_len = 0
        for w in words:
            addition = len(w) + (1 if curr else 0)
            if curr_len + addition <= max_chars:
                curr.append(w)
                curr_len += addition
            else:
                if curr:
                    lines.append(" ".join(curr))
                curr = [w]
                curr_len = len(w)
        if curr:
            lines.append(" ".join(curr))
        return lines

    def _render_interactive_styles(self) -> str:
        contrast = self._contrast_color(self.theme.accent)
        return (
            "    <style>\n"
            "      .diagram-interactive { cursor: grab; user-select: none; }\n"
            "      .diagram-interactive:active { cursor: grabbing; }\n"
            "      .group-header { cursor: pointer; }\n"
            "      .group-header:hover text { opacity: 0.8; }\n"
            f'      .group-toggle {{ font-size: 12px; fill: {self.theme.accent}; user-select: none; }}\n'
            "      .hud-btn { cursor: pointer; }\n"
            "      .hud-btn rect { transition: fill 0.15s; }\n"
            f'      .hud-btn:hover rect {{ fill: {self.theme.accent}; }}\n'
            f'      .hud-btn:hover text {{ fill: {contrast}; }}\n'
            "    </style>"
        )

    def _render_interactive_controls(self, width: float, height: float) -> list[str]:
        ctrl_x = float(width) - 110.0
        ctrl_y = 16.0
        ctrl_w = 94.0
        ctrl_h = 30.0
        return [
            f'  <g id="svg-pan-zoom-controls" transform="translate({ctrl_x}, {ctrl_y})">',
            f'    <rect x="0" y="0" width="{ctrl_w}" height="{ctrl_h}" rx="6" '
            f'fill="{self.theme.node_fill}" stroke="{self.theme.node_stroke}" stroke-width="1.5" filter="url(#shadow)"/>',
            '    <g id="btn-zoom-in" class="hud-btn">'
            f'<rect x="3" y="3" width="26" height="24" rx="4" fill="{self.theme.background}" />'
            f'<text x="16" y="19" text-anchor="middle" fill="{self.theme.text}" font-family="{self.theme.font_family}" font-size="16" font-weight="bold">+</text>'
            '<title>Zoom In</title></g>',
            '    <g id="btn-zoom-out" class="hud-btn">'
            f'<rect x="34" y="3" width="26" height="24" rx="4" fill="{self.theme.background}" />'
            f'<text x="47" y="18" text-anchor="middle" fill="{self.theme.text}" font-family="{self.theme.font_family}" font-size="16" font-weight="bold">−</text>'
            '<title>Zoom Out</title></g>',
            '    <g id="btn-zoom-reset" class="hud-btn">'
            f'<rect x="65" y="3" width="26" height="24" rx="4" fill="{self.theme.background}" />'
            f'<text x="78" y="18" text-anchor="middle" fill="{self.theme.text}" font-family="{self.theme.font_family}" font-size="13" font-weight="bold">⟲</text>'
            '<title>Reset View</title></g>',
            '  </g>',
        ]

    def _render_interactive_script(self, width: float, height: float) -> list[str]:
        w_val = int(width) if isinstance(width, (int, float)) and float(width).is_integer() else width
        h_val = int(height) if isinstance(height, (int, float)) and float(height).is_integer() else height
        ctrl_x = float(width) - 110.0
        ctrl_y = 16.0
        js = f"""
(function() {{
  var svg = document.currentScript ? document.currentScript.closest('svg') : document.querySelector('svg');
  if (!svg) return;

  var vbAttr = svg.getAttribute('viewBox') || '0 0 {w_val} {h_val}';
  var parts = vbAttr.split(/[\\s,]+/).map(Number);
  var orig = {{ x: parts[0], y: parts[1], w: parts[2], h: parts[3] }};
  var vb = {{ x: orig.x, y: orig.y, w: orig.w, h: orig.h }};

  function updateViewBox() {{
    svg.setAttribute('viewBox', vb.x + ' ' + vb.y + ' ' + vb.w + ' ' + vb.h);
    var ctrl = document.getElementById('svg-pan-zoom-controls');
    if (ctrl) {{
      var scale = vb.w / orig.w;
      var cx = vb.x + vb.w - (orig.w - {ctrl_x}) * scale;
      var cy = vb.y + {ctrl_y} * scale;
      ctrl.setAttribute('transform', 'translate(' + cx + ',' + cy + ') scale(' + scale + ')');
    }}
  }}

  var isPanning = false;
  var startX = 0, startY = 0;

  svg.addEventListener('mousedown', function(e) {{
    if (e.target.closest('#svg-pan-zoom-controls') || e.target.closest('.group-header')) return;
    if (e.button !== 0) return;
    isPanning = true;
    startX = e.clientX;
    startY = e.clientY;
  }});

  window.addEventListener('mousemove', function(e) {{
    if (!isPanning) return;
    var rect = svg.getBoundingClientRect();
    if (!rect.width || !rect.height) return;
    var dx = (e.clientX - startX) * (vb.w / rect.width);
    var dy = (e.clientY - startY) * (vb.h / rect.height);
    vb.x -= dx;
    vb.y -= dy;
    startX = e.clientX;
    startY = e.clientY;
    updateViewBox();
  }});

  window.addEventListener('mouseup', function() {{
    isPanning = false;
  }});

  function zoomAt(factor, clientX, clientY) {{
    var rect = svg.getBoundingClientRect();
    var mouseX = clientX !== undefined && rect.width ? (clientX - rect.left) / rect.width : 0.5;
    var mouseY = clientY !== undefined && rect.height ? (clientY - rect.top) / rect.height : 0.5;
    var newW = vb.w * factor;
    var newH = vb.h * factor;
    if (newW < orig.w * 0.05 || newW > orig.w * 20.0) return;
    vb.x += (vb.w - newW) * mouseX;
    vb.y += (vb.h - newH) * mouseY;
    vb.w = newW;
    vb.h = newH;
    updateViewBox();
  }}

  svg.addEventListener('wheel', function(e) {{
    e.preventDefault();
    var factor = e.deltaY > 0 ? 1.15 : 0.85;
    zoomAt(factor, e.clientX, e.clientY);
  }}, {{ passive: false }});

  var btnIn = document.getElementById('btn-zoom-in');
  if (btnIn) btnIn.addEventListener('click', function(e) {{
    e.stopPropagation();
    zoomAt(0.8);
  }});

  var btnOut = document.getElementById('btn-zoom-out');
  if (btnOut) btnOut.addEventListener('click', function(e) {{
    e.stopPropagation();
    zoomAt(1.25);
  }});

  var btnReset = document.getElementById('btn-zoom-reset');
  if (btnReset) btnReset.addEventListener('click', function(e) {{
    e.stopPropagation();
    vb.x = orig.x; vb.y = orig.y; vb.w = orig.w; vb.h = orig.h;
    updateViewBox();
  }});

  var groupHeaders = svg.querySelectorAll('.group-header');
  groupHeaders.forEach(function(header) {{
    header.addEventListener('click', function(e) {{
      e.stopPropagation();
      var groupId = header.getAttribute('data-group-id');
      var groupG = document.getElementById(groupId);
      if (!groupG) return;
      var isCollapsed = groupG.getAttribute('data-collapsed') === 'true';
      var newCollapsed = !isCollapsed;
      groupG.setAttribute('data-collapsed', newCollapsed ? 'true' : 'false');

      var toggle = groupG.querySelector('.group-toggle');
      if (toggle) toggle.textContent = newCollapsed ? '▶' : '▼';

      var rect = groupG.querySelector('.group-box');
      if (rect) {{
        var origH = parseFloat(groupG.getAttribute('data-orig-height') || rect.getAttribute('height'));
        var headerH = parseFloat(groupG.getAttribute('data-header-height') || '35');
        rect.setAttribute('height', newCollapsed ? headerH : origH);
      }}

      function setVisibility(gId, hide) {{
        var directChildren = svg.querySelectorAll('[data-parent-group=\"' + gId + '\"]');
        directChildren.forEach(function(child) {{
          child.style.display = hide ? 'none' : '';
          if (child.classList.contains('diagram-group')) {{
            var childGId = child.getAttribute('data-group-id') || child.id;
            var childCollapsed = child.getAttribute('data-collapsed') === 'true';
            if (!hide && childCollapsed) {{
              setVisibility(childGId, true);
            }} else {{
              setVisibility(childGId, hide);
            }}
          }}
        }});
        var edges = svg.querySelectorAll('[data-source-group=\"' + gId + '\"], [data-target-group=\"' + gId + '\"]');
        edges.forEach(function(edge) {{
          edge.style.display = hide ? 'none' : '';
        }});
      }}

      setVisibility(groupId, newCollapsed);
    }});
  }});
}})();
"""
        return [
            '  <script type="text/javascript"><![CDATA[',
            js.strip(),
            '  ]]></script>',
        ]

    def render(
        self,
        elements: Optional[Sequence[Element]] = None,
        groups: Optional[Sequence[Group]] = None,
        edges: Optional[Sequence[Edge]] = None,
        width: float = 1200.0,
        height: float = 800.0,
        routes: Optional[Mapping[int, list[Point]]] = None,
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


            "  <defs>",
            '    <marker id="arrow" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">',
            f'      <path d="M 0 1 L 10 5 L 0 9 z" fill="{self.theme.accent}"/>',
            "    </marker>",
            '    <marker id="arrow-tail" viewBox="0 0 10 10" refX="2" refY="5" markerWidth="6" markerHeight="6" orient="auto">',
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
                    f'    <marker id="{m_id}" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">'
                )
                lines.append(
                    f'      <path d="M 0 1 L 10 5 L 0 9 z" fill="{c}"/>'
                )
                lines.append("    </marker>")
                lines.append(
                    f'    <marker id="{m_id}-tail" viewBox="0 0 10 10" refX="2" refY="5" markerWidth="6" markerHeight="6" orient="auto">'
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
            lines.append(self._render_interactive_styles())
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
            if interactive:
                p_attr = f' data-parent-group="{html.escape(g.parent.id, quote=True)}"' if g.parent is not None else ""
                h_h = getattr(g, "header_height", 35.0)
                lines.append(
                    f'  <g id="{escaped_g_id}" class="diagram-group" data-group-id="{escaped_g_id}" '
                    f'data-collapsed="false" data-orig-height="{b.height}" data-header-height="{h_h}"{p_attr}>'
                )
                lines.append(
                    f'    <rect class="group-box" x="{b.x}" y="{b.y}" width="{b.width}" height="{b.height}" rx="8" '
                    f'fill="{g_fill}" stroke="{g_stroke}" stroke-width="1.5" />'
                )
                lines.append(f'    <g class="group-header" data-group-id="{escaped_g_id}">')
                lines.append(
                    f'      <rect x="{b.x}" y="{b.y}" width="{b.width}" height="{h_h}" rx="8" fill="transparent" />'
                )
                lines.append(
                    f'      <text class="group-toggle" x="{b.x + 14}" y="{b.y + 22}">▼</text>'
                )
                if g.label:
                    lines.append(
                        f'      <text x="{b.x + 32}" y="{b.y + 24}" fill="{self.theme.accent}" '
                        f'font-family="{self.theme.font_family}" font-size="14" font-weight="bold">{html.escape(g.label)}</text>'
                    )
                lines.append("    </g>")
                lines.append("  </g>")
            else:
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
        def _get_group_id(elem: Any) -> Optional[str]:
            if isinstance(elem, Group):
                return elem.id
            if getattr(elem, "parent", None) is not None:
                return elem.parent.id
            return None

        for e in edge_list:
            pts = (
                e.waypoints
                if getattr(e, "waypoints", None) is not None
                else (routes[id(e)] if routes is not None and id(e) in routes else self.router.route(e))
            )
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

            if interactive:
                src_gid = _get_group_id(e.source)
                tgt_gid = _get_group_id(e.target)
                edge_attrs = ""
                if src_gid:
                    edge_attrs += f' data-source-group="{html.escape(src_gid, quote=True)}"'
                if tgt_gid:
                    edge_attrs += f' data-target-group="{html.escape(tgt_gid, quote=True)}"'
                lines.append(f'  <g class="diagram-edge"{edge_attrs}>')
                lines.append(
                    f'    <path d="{path_d}" fill="none" stroke="{edge_color}" stroke-width="2"{dash}{marker_start}{marker_end} />'
                )
            else:
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
                indent = "    " if interactive else "  "
                lines.append(f"{indent}{badge_svg}")

            if interactive:
                lines.append("  </g>")

        # 4. Render Shapes
        for el in element_list:
            b = el.bounds
            escaped_el_id = html.escape(el.id, quote=True)
            if interactive and getattr(el, "parent", None) is not None:
                escaped_p_id = html.escape(el.parent.id, quote=True)
                lines.append(f'  <g id="{escaped_el_id}" data-parent-group="{escaped_p_id}" filter="url(#shadow)">')
            else:
                lines.append(f'  <g id="{escaped_el_id}" filter="url(#shadow)">')

            kind_raw = getattr(el, "kind", "box")
            kind = (kind_raw or "box").lower().replace("-", "_")

            label_pos = getattr(el, "label_position", "auto")
            if label_pos == "auto":
                label_pos = "bottom" if kind == "icon" else "inside"
            elif label_pos == "below":
                label_pos = "bottom"

            fill = el.metadata.get("fill", self.theme.node_fill)
            stroke = el.metadata.get("stroke", self.theme.node_stroke)
            stroke_width = float(el.metadata.get("stroke_width", 2.0))

            if kind == "icon":
                # Pure icon: no container background box
                pass
            elif kind == "box":
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
                if label_pos == "bottom" or kind == "icon":
                    text_color = self.theme.text
                elif fill != self.theme.node_fill:
                    text_color = self._contrast_color(fill)
                else:
                    text_color = self.theme.text

            icon_name = getattr(el, "icon", None)

            if kind == "icon":
                # Render pure vector icon centered in bounds
                icon_size = float(
                    el.metadata.get("icon_size", min(36.0, max(24.0, min(b.width, b.height) * 0.6)))
                )
                icon_color = str(el.metadata.get("icon_color", self.theme.accent))
                icon_x = b.center.x - icon_size / 2.0
                icon_y = b.y + max(2.0, (b.height - icon_size) / 2.0)
                if icon_name:
                    lines.append(
                        f"    {self.shapes.render_icon(icon_name, icon_x, icon_y, size=icon_size, color=icon_color)}"
                    )
                if el.label:
                    text_y = b.y + b.height + LABEL_BELOW_OFFSET
                    lines.append(
                        f'    <text x="{b.center.x}" y="{text_y}" text-anchor="middle" '
                        f'fill="{text_color}" font-family="{self.theme.font_family}" '
                        f'font-size="12" font-weight="600">{html.escape(el.label)}</text>'
                    )
            elif label_pos == "bottom":
                # Render icon centered inside the container tile, with label below the container
                if icon_name:
                    icon_size = float(
                        el.metadata.get("icon_size", min(28.0, max(18.0, b.height * 0.45)))
                    )
                    icon_color = str(el.metadata.get("icon_color", self.theme.accent))
                    icon_x = b.center.x - icon_size / 2.0
                    icon_y = b.center.y - icon_size / 2.0
                    lines.append(
                        f"    {self.shapes.render_icon(icon_name, icon_x, icon_y, size=icon_size, color=icon_color)}"
                    )
                if el.label:
                    text_y = b.y + b.height + LABEL_BELOW_OFFSET
                    char_budget = max(14, int(max(b.width, 100.0) / 7.0))
                    label_lines = self.wrap_text(el.label, max_chars=char_budget)
                    if len(label_lines) <= 1:
                        lines.append(
                            f'    <text x="{b.center.x}" y="{text_y}" text-anchor="middle" '
                            f'fill="{text_color}" font-family="{self.theme.font_family}" '
                            f'font-size="12" font-weight="600">{html.escape(el.label)}</text>'
                        )
                    else:
                        font_size = 11.0
                        line_h = font_size * 1.25
                        tspan_parts = [
                            f'<tspan x="{b.center.x}" dy="{0 if i == 0 else line_h}">{html.escape(line)}</tspan>'
                            for i, line in enumerate(label_lines)
                        ]
                        lines.append(
                            f'    <text x="{b.center.x}" y="{text_y}" text-anchor="middle" '
                            f'fill="{text_color}" font-family="{self.theme.font_family}" '
                            f'font-size="{font_size}" font-weight="600">{" ".join(tspan_parts)}</text>'
                        )
            else:
                # label_pos == "inside": Render embedded icon and wrapped label inside the card
                if icon_name:
                    icon_size = float(
                        el.metadata.get("icon_size", min(24.0, max(16.0, b.height * 0.38)))
                    )
                    icon_color = str(el.metadata.get("icon_color", self.theme.accent))
                    if el.label:
                        char_budget = max(10, int(b.width / 7.2))
                        label_lines = self.wrap_text(el.label, max_chars=char_budget)
                        if len(label_lines) <= 1:
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
                            font_size = 11.0 if len(label_lines) == 2 else 10.0
                            line_h = font_size * 1.25
                            total_text_h = len(label_lines) * line_h
                            icon_x = b.center.x - icon_size / 2.0
                            icon_y = b.y + max(3.0, (b.height - icon_size - total_text_h - 2.0) / 2.0)
                            lines.append(
                                f"    {self.shapes.render_icon(icon_name, icon_x, icon_y, size=icon_size, color=icon_color)}"
                            )
                            text_start_y = icon_y + icon_size + font_size + 1.0
                            tspan_parts = [
                                f'<tspan x="{b.center.x}" dy="{0 if i == 0 else line_h}">{html.escape(line)}</tspan>'
                                for i, line in enumerate(label_lines)
                            ]
                            lines.append(
                                f'    <text x="{b.center.x}" y="{text_start_y}" text-anchor="middle" '
                                f'fill="{text_color}" font-family="{self.theme.font_family}" '
                                f'font-size="{font_size}" font-weight="500">{" ".join(tspan_parts)}</text>'
                            )
                    else:
                        icon_x = b.center.x - icon_size / 2.0
                        icon_y = b.center.y - icon_size / 2.0
                        lines.append(
                            f"    {self.shapes.render_icon(icon_name, icon_x, icon_y, size=icon_size, color=icon_color)}"
                        )
                elif el.label:
                    char_budget = max(10, int(b.width / 7.2))
                    label_lines = self.wrap_text(el.label, max_chars=char_budget)
                    if len(label_lines) <= 1:
                        lines.append(
                            f'    <text x="{b.center.x}" y="{b.center.y + 4}" text-anchor="middle" '
                            f'fill="{text_color}" font-family="{self.theme.font_family}" '
                            f'font-size="13" font-weight="500">{html.escape(el.label)}</text>'
                        )
                    else:
                        font_size = 11.5
                        line_h = font_size * 1.25
                        start_y = b.center.y - ((len(label_lines) - 1) * line_h) / 2.0 + 4.0
                        tspan_parts = [
                            f'<tspan x="{b.center.x}" dy="{0 if i == 0 else line_h}">{html.escape(line)}</tspan>'
                            for i, line in enumerate(label_lines)
                        ]
                        lines.append(
                            f'    <text x="{b.center.x}" y="{start_y}" text-anchor="middle" '
                            f'fill="{text_color}" font-family="{self.theme.font_family}" '
                            f'font-size="{font_size}" font-weight="500">{" ".join(tspan_parts)}</text>'
                        )

            lines.append("  </g>")

        if interactive:
            lines.extend(self._render_interactive_controls(width, height))
            lines.extend(self._render_interactive_script(width, height))

        lines.append("</svg>")
        return "\n".join(lines)
