"""Pure-Python standalone SVG renderer for IIoT diagrams."""
from __future__ import annotations

import html
import math
import re
from typing import Any, Mapping, Optional, Sequence

from diagrams_as_code.connections import Edge, Routing
from diagrams_as_code.elements import Element, Shape
from diagrams_as_code.geometry import CubicBezier, Point, Rect
from diagrams_as_code.groups import Group
from diagrams_as_code.metrics import LABEL_BELOW_OFFSET
from diagrams_as_code.router import OrthogonalRouter
from diagrams_as_code.shapes import ShapeLibrary
from diagrams_as_code.theme import Theme


def _render_filleted_path(
    pts: list[Point],
    corner_radius: float,
    obstacles: Optional[Sequence[Rect]] = None,
) -> str:
    """Format orthogonal Manhattan polyline into SVG path with rounded quadratic Bezier fillets."""
    n = len(pts)
    if n < 3 or corner_radius <= 0.0:
        return f"M {pts[0].x} {pts[0].y} " + " ".join(f"L {p.x} {p.y}" for p in pts[1:])

    # 1. Precalculate segment vectors, lengths, and unit vectors
    seg_lens: list[float] = []
    seg_units: list[Point] = []
    for j in range(n - 1):
        vx = pts[j + 1].x - pts[j].x
        vy = pts[j + 1].y - pts[j].y
        l = math.hypot(vx, vy)
        seg_lens.append(l)
        seg_units.append(Point(vx / l, vy / l) if l > 1e-6 else Point(0.0, 0.0))

    # 2. Compute effective radius per corner with dynamic clamping
    effective_radii: list[float] = [0.0] * n
    for i in range(1, n - 1):
        l_in = seg_lens[i - 1]
        l_out = seg_lens[i]

        if l_in < 1e-6 or l_out < 1e-6:
            continue

        u_in = seg_units[i - 1]
        u_out = seg_units[i]

        # Strict 90-degree orthogonal turn detection (D-07)
        dot = u_in.x * u_out.x + u_in.y * u_out.y
        if abs(dot) > 1e-6:
            continue

        # 50% segment budget (D-05)
        max_r_in = l_in / 2.0
        max_r_out = l_out / 2.0

        # Endpoint straight lead-in enforcement (D-08)
        if i == 1:
            lead_in = min(10.0, l_in / 2.0)
            max_r_in = min(max_r_in, max(0.0, l_in - lead_in))
        if i == n - 2:
            lead_in = min(10.0, l_out / 2.0)
            max_r_out = min(max_r_out, max(0.0, l_out - lead_in))

        r_corner = min(corner_radius, max_r_in, max_r_out)

        # Obstacle clearance guard (D-14, T-09-06)
        if obstacles and r_corner >= 2.0:
            p_c = pts[i]
            dx_apex = -0.25 * (u_in.x - u_out.x)
            dy_apex = -0.25 * (u_in.y - u_out.y)
            for obs in obstacles:
                exp = obs.expand(4.0)
                apex_x = p_c.x + r_corner * dx_apex
                apex_y = p_c.y + r_corner * dy_apex
                if exp.left < apex_x < exp.right and exp.top < apex_y < exp.bottom:
                    safe_r = r_corner
                    cands: list[float] = []
                    if abs(dx_apex) > 1e-6:
                        target_x = exp.right if dx_apex < 0 else exp.left
                        cands.append((target_x - p_c.x) / dx_apex)
                    if abs(dy_apex) > 1e-6:
                        target_y = exp.bottom if dy_apex < 0 else exp.top
                        cands.append((target_y - p_c.y) / dy_apex)
                    valid_cands = [c for c in cands if c >= 0.0]
                    if valid_cands:
                        safe_r = min(safe_r, *valid_cands)
                    else:
                        safe_r = 0.0
                    r_corner = min(r_corner, safe_r)

        # Minimum threshold suppression (D-06)
        if r_corner < 2.0:
            r_corner = 0.0

        effective_radii[i] = r_corner

    # 3. Assemble SVG path commands (D-09)
    parts = [f"M {pts[0].x} {pts[0].y}"]
    for i in range(1, n - 1):
        p_c = pts[i]
        r = effective_radii[i]
        if r >= 2.0:
            u_in = seg_units[i - 1]
            u_out = seg_units[i]
            t1 = Point(p_c.x - u_in.x * r, p_c.y - u_in.y * r)
            t2 = Point(p_c.x + u_out.x * r, p_c.y + u_out.y * r)
            parts.append(f"L {t1.x} {t1.y} Q {p_c.x} {p_c.y}, {t2.x} {t2.y}")
        else:
            parts.append(f"L {p_c.x} {p_c.y}")

    parts.append(f"L {pts[-1].x} {pts[-1].y}")
    return " ".join(parts)


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
            f'      #diagram-search-input {{\n'
            f'        box-sizing: border-box; width: 100%; height: 100%;\n'
            f'        background: {self.theme.background}; color: {self.theme.text};\n'
            f'        border: 1px solid {self.theme.node_stroke}; border-radius: 4px;\n'
            f'        padding: 0 6px; font-family: {self.theme.font_family}; font-size: 11px;\n'
            f'        outline: none;\n'
            f'      }}\n'
            f'      #diagram-search-input:focus {{ border-color: {self.theme.accent}; }}\n'
            f'      #diagram-search-input::placeholder {{ color: {self.theme.subtext}; opacity: 0.7; }}\n'
            "      .diagram-node, .diagram-edge, .diagram-group { transition: opacity 0.2s ease-in-out; }\n"
            "      #svg-minimap { cursor: pointer; user-select: none; }\n"
            "      #minimap-viewport { cursor: grab; }\n"
            "      #minimap-viewport:active { cursor: grabbing; }\n"
            "    </style>"
        )

    def _render_interactive_controls(self, width: float, height: float) -> list[str]:
        ctrl_w = 228.0
        ctrl_h = 30.0
        ctrl_x = float(width) - ctrl_w - 16.0
        ctrl_y = 16.0
        return [
            f'  <g id="svg-pan-zoom-controls" transform="translate({ctrl_x}, {ctrl_y})">',
            f'    <rect x="0" y="0" width="{ctrl_w}" height="{ctrl_h}" rx="6" '
            f'fill="{self.theme.node_fill}" stroke="{self.theme.node_stroke}" stroke-width="1.5" filter="url(#shadow)"/>',
            '    <foreignObject x="4" y="3" width="126" height="24">',
            f'      <input xmlns="http://www.w3.org/1999/xhtml" id="diagram-search-input" type="text" '
            f'placeholder="Search..." autocomplete="off" spellcheck="false" />',
            '    </foreignObject>',
            '    <g id="btn-zoom-in" class="hud-btn">'
            f'<rect x="134" y="3" width="26" height="24" rx="4" fill="{self.theme.background}" />'
            f'<text x="147" y="19" text-anchor="middle" fill="{self.theme.text}" font-family="{self.theme.font_family}" font-size="16" font-weight="bold">+</text>'
            '<title>Zoom In</title></g>',
            '    <g id="btn-zoom-out" class="hud-btn">'
            f'<rect x="165" y="3" width="26" height="24" rx="4" fill="{self.theme.background}" />'
            f'<text x="178" y="18" text-anchor="middle" fill="{self.theme.text}" font-family="{self.theme.font_family}" font-size="16" font-weight="bold">−</text>'
            '<title>Zoom Out</title></g>',
            '    <g id="btn-zoom-reset" class="hud-btn">'
            f'<rect x="196" y="3" width="26" height="24" rx="4" fill="{self.theme.background}" />'
            f'<text x="209" y="18" text-anchor="middle" fill="{self.theme.text}" font-family="{self.theme.font_family}" font-size="13" font-weight="bold">⟲</text>'
            '<title>Reset View</title></g>',
            '  </g>',
        ]

    def _render_interactive_minimap(self, width: float, height: float) -> list[str]:
        mm_w = 160.0
        mm_h = 100.0
        mm_x = float(width) - mm_w - 16.0
        mm_y = float(height) - mm_h - 16.0
        inner_w = mm_w - 8.0
        inner_h = mm_h - 8.0
        mm_s = min(inner_w / float(width), inner_h / float(height))
        mm_off_x = 4.0 + (inner_w - float(width) * mm_s) / 2.0
        mm_off_y = 4.0 + (inner_h - float(height) * mm_s) / 2.0
        init_vp_w = float(width) * mm_s
        init_vp_h = float(height) * mm_s

        return [
            f'  <g id="svg-minimap" transform="translate({mm_x}, {mm_y})">',
            f'    <rect class="minimap-bg" x="0" y="0" width="{mm_w}" height="{mm_h}" rx="6" '
            f'fill="{self.theme.node_fill}" stroke="{self.theme.node_stroke}" stroke-width="1.5" '
            f'filter="url(#shadow)" opacity="0.95"/>',
            '    <g clip-path="url(#minimap-clip)">',
            f'      <g transform="translate({mm_off_x:.2f}, {mm_off_y:.2f}) scale({mm_s:.6f})" opacity="0.65" pointer-events="none">',
            '        <use href="#diagram-content" />',
            '      </g>',
            '    </g>',
            f'    <rect id="minimap-viewport" x="{mm_off_x:.2f}" y="{mm_off_y:.2f}" width="{init_vp_w:.2f}" height="{init_vp_h:.2f}" rx="2" '
            f'fill="{self.theme.accent}" fill-opacity="0.18" stroke="{self.theme.accent}" stroke-width="1.5" style="cursor: move;" />',
            '  </g>',
        ]

    def _render_interactive_script(self, width: float, height: float) -> list[str]:
        w_val = int(width) if isinstance(width, (int, float)) and float(width).is_integer() else width
        h_val = int(height) if isinstance(height, (int, float)) and float(height).is_integer() else height
        ctrl_w = 228.0
        ctrl_x = float(width) - ctrl_w - 16.0
        ctrl_y = 16.0

        mm_w = 160.0
        mm_h = 100.0
        mm_x = float(width) - mm_w - 16.0
        mm_y = float(height) - mm_h - 16.0
        inner_w = mm_w - 8.0
        inner_h = mm_h - 8.0
        mm_s = min(inner_w / float(width), inner_h / float(height))
        mm_off_x = 4.0 + (inner_w - float(width) * mm_s) / 2.0
        mm_off_y = 4.0 + (inner_h - float(height) * mm_s) / 2.0

        js = f"""
(function() {{
  var svg = document.currentScript ? document.currentScript.closest('svg') : document.querySelector('svg');
  if (!svg) return;

  var vbAttr = svg.getAttribute('viewBox') || '0 0 {w_val} {h_val}';
  var parts = vbAttr.split(/[\\s,]+/).map(Number);
  var orig = {{ x: parts[0], y: parts[1], w: parts[2], h: parts[3] }};
  var vb = {{ x: orig.x, y: orig.y, w: orig.w, h: orig.h }};
  var updateMinimapViewport = null;

  function updateViewBox() {{
    svg.setAttribute('viewBox', vb.x + ' ' + vb.y + ' ' + vb.w + ' ' + vb.h);
    var scale = vb.w / orig.w;
    var ctrl = document.getElementById('svg-pan-zoom-controls');
    if (ctrl) {{
      var cx = vb.x + vb.w - (orig.w - {ctrl_x}) * scale;
      var cy = vb.y + {ctrl_y} * scale;
      ctrl.setAttribute('transform', 'translate(' + cx + ',' + cy + ') scale(' + scale + ')');
    }}
    var minimap = document.getElementById('svg-minimap');
    if (minimap) {{
      var mx = vb.x + vb.w - (orig.w - {mm_x}) * scale;
      var my = vb.y + vb.h - (orig.h - {mm_y}) * scale;
      minimap.setAttribute('transform', 'translate(' + mx + ',' + my + ') scale(' + scale + ')');
      if (typeof updateMinimapViewport === 'function') {{
        updateMinimapViewport();
      }}
    }}
  }}

  var isPanning = false;
  var startX = 0, startY = 0;

  svg.addEventListener('mousedown', function(e) {{
    if (e.target.closest('#svg-pan-zoom-controls') || e.target.closest('#svg-minimap') || e.target.closest('.group-header')) return;
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

  var searchInput = document.getElementById('diagram-search-input');
  if (searchInput) {{
    function applySearch(query) {{
      var q = (query || '').trim().toLowerCase();
      var nodes = svg.querySelectorAll('.diagram-node');
      var edges = svg.querySelectorAll('.diagram-edge');
      var groups = svg.querySelectorAll('.diagram-group');

      if (!q) {{
        nodes.forEach(function(n) {{ n.style.opacity = ''; }});
        edges.forEach(function(e) {{ e.style.opacity = ''; }});
        groups.forEach(function(g) {{ g.style.opacity = ''; }});
        return;
      }}

      var matchedNodeIds = {{}};
      nodes.forEach(function(n) {{
        var id = (n.getAttribute('data-node-id') || n.id || '').toLowerCase();
        var label = (n.getAttribute('data-label') || '').toLowerCase();
        if (id.indexOf(q) !== -1 || label.indexOf(q) !== -1) {{
          n.style.opacity = '1';
          matchedNodeIds[n.getAttribute('data-node-id') || n.id] = true;
        }} else {{
          n.style.opacity = '0.2';
        }}
      }});

      edges.forEach(function(e) {{
        var src = e.getAttribute('data-source-id');
        var tgt = e.getAttribute('data-target-id');
        if ((src && matchedNodeIds[src]) || (tgt && matchedNodeIds[tgt])) {{
          e.style.opacity = '1';
        }} else {{
          e.style.opacity = '0.15';
        }}
      }});

      groups.forEach(function(g) {{
        var gId = g.getAttribute('data-group-id') || g.id;
        var gLabel = (g.getAttribute('data-label') || '').toLowerCase();
        var hasMatch = (gId.toLowerCase().indexOf(q) !== -1) || (gLabel.indexOf(q) !== -1);
        if (!hasMatch) {{
          var children = g.querySelectorAll('.diagram-node');
          for (var i = 0; i < children.length; i++) {{
            var cId = children[i].getAttribute('data-node-id') || children[i].id;
            if (matchedNodeIds[cId]) {{
              hasMatch = true;
              break;
            }}
          }}
        }}
        g.style.opacity = hasMatch ? '1' : '0.25';
      }});
    }}

    searchInput.addEventListener('input', function() {{
      applySearch(this.value);
    }});

    searchInput.addEventListener('keydown', function(e) {{
      if (e.key === 'Escape') {{
        this.value = '';
        applySearch('');
        this.blur();
      }}
      e.stopPropagation();
    }});

    searchInput.addEventListener('mousedown', function(e) {{
      e.stopPropagation();
    }});
    searchInput.addEventListener('click', function(e) {{
      e.stopPropagation();
    }});
  }}

  var minimap = document.getElementById('svg-minimap');
  var minimapVp = document.getElementById('minimap-viewport');
  if (minimap && minimapVp) {{
    var mmS = {mm_s:.6f};
    var mmOffX = {mm_off_x:.2f};
    var mmOffY = {mm_off_y:.2f};
    var isMinimapDragging = false;

    updateMinimapViewport = function() {{
      var vx = mmOffX + vb.x * mmS;
      var vy = mmOffY + vb.y * mmS;
      var vw = vb.w * mmS;
      var vh = vb.h * mmS;
      minimapVp.setAttribute('x', vx);
      minimapVp.setAttribute('y', vy);
      minimapVp.setAttribute('width', vw);
      minimapVp.setAttribute('height', vh);
    }};

    function centerFromMinimap(evt) {{
      var mRect = minimap.getBoundingClientRect();
      if (!mRect.width || !mRect.height) return;
      var scale = vb.w / orig.w;
      var clickX = (evt.clientX - mRect.left) / scale;
      var clickY = (evt.clientY - mRect.top) / scale;

      var diagTargetX = (clickX - mmOffX) / mmS;
      var diagTargetY = (clickY - mmOffY) / mmS;

      vb.x = diagTargetX - vb.w / 2;
      vb.y = diagTargetY - vb.h / 2;
      updateViewBox();
    }}

    minimap.addEventListener('mousedown', function(e) {{
      if (e.button !== 0) return;
      e.stopPropagation();
      isMinimapDragging = true;
      centerFromMinimap(e);
    }});

    window.addEventListener('mousemove', function(e) {{
      if (isMinimapDragging) {{
        centerFromMinimap(e);
      }}
    }});

    window.addEventListener('mouseup', function() {{
      isMinimapDragging = false;
    }});

    updateMinimapViewport();
  }}

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
            lines.append('    <clipPath id="minimap-clip"><rect x="0" y="0" width="160" height="100" rx="6"/></clipPath>')
            lines.append(self._render_interactive_styles())
        lines.append("  </defs>")

        # Canvas background fill
        lines.append(
            f'  <rect width="100%" height="100%" fill="{self.theme.background}"/>'
        )
        if interactive:
            lines.append('  <g id="diagram-content">')

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
                g_label = html.escape(g.label or "", quote=True)
                lines.append(
                    f'  <g id="{escaped_g_id}" class="diagram-group" data-group-id="{escaped_g_id}" '
                    f'data-label="{g_label}" '
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

            if getattr(e, "waypoints", None) is None:
                try:
                    e.waypoints = pts
                except Exception:
                    pass

            # Path generation branching
            is_orthogonal = e.routing in (Routing.ORTHOGONAL, "orthogonal")
            corner_r = getattr(e, "corner_radius", None) or 0.0

            if e.routing in (Routing.CURVE, "curve") and len(pts) == 4:
                p0, c1, c2, p3 = pts
                path_d = f"M {p0.x} {p0.y} C {c1.x} {c1.y}, {c2.x} {c2.y}, {p3.x} {p3.y}"
            elif e.routing in (Routing.CURVE, "curve") and len(pts) >= 4 and (len(pts) - 1) % 3 == 0:
                parts = [f"M {pts[0].x} {pts[0].y}"]
                for i in range(1, len(pts), 3):
                    parts.append(
                        f"C {pts[i].x} {pts[i].y}, {pts[i+1].x} {pts[i+1].y}, {pts[i+2].x} {pts[i+2].y}"
                    )
                path_d = " ".join(parts)
            elif is_orthogonal and corner_r > 0.0:
                obs_bounds = [el.bounds for el in element_list if el not in (e.source, e.target)]
                path_d = _render_filleted_path(pts, corner_r, obstacles=obs_bounds)
            else:
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
                lines.append(
                    f'    <path d="{path_d}" fill="none" stroke="{edge_color}" stroke-width="2"{dash}{marker_start}{marker_end} />'
                )
            else:
                lines.append(
                    f'  <path d="{path_d}" fill="none" stroke="{edge_color}" stroke-width="2"{dash}{marker_start}{marker_end} />'
                )

            # Centered protocol badge so edge lines don't cross text
            if e.label:
                is_curve = e.routing in (Routing.CURVE, "curve")
                if is_curve and len(pts) == 4:
                    curve = CubicBezier(pts[0], pts[1], pts[2], pts[3])
                    mid = curve.arc_length_midpoint(num_samples=32)
                    lx, ly = mid.x, mid.y
                elif is_curve and len(pts) >= 4 and (len(pts) - 1) % 3 == 0:
                    # Multi-segment fallback: take arc-length midpoint of middle segment or first segment
                    num_segs = (len(pts) - 1) // 3
                    seg_idx = num_segs // 2
                    seg_start = seg_idx * 3
                    curve = CubicBezier(
                        pts[seg_start],
                        pts[seg_start + 1],
                        pts[seg_start + 2],
                        pts[seg_start + 3],
                    )
                    mid = curve.arc_length_midpoint(num_samples=32)
                    lx, ly = mid.x, mid.y
                elif is_orthogonal and corner_r > 0.0:
                    longest_idx = 0
                    longest_len = -1.0
                    for j in range(len(pts) - 1):
                        seg_l = math.hypot(pts[j + 1].x - pts[j].x, pts[j + 1].y - pts[j].y)
                        if seg_l > longest_len:
                            longest_len = seg_l
                            longest_idx = j
                    lx = (pts[longest_idx].x + pts[longest_idx + 1].x) / 2.0
                    ly = (pts[longest_idx].y + pts[longest_idx + 1].y) / 2.0
                else:
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
            if interactive:
                escaped_label = html.escape(el.label or "", quote=True)
                p_attr = f' data-parent-group="{html.escape(el.parent.id, quote=True)}"' if getattr(el, "parent", None) is not None else ""
                lines.append(
                    f'  <g id="{escaped_el_id}" class="diagram-node" data-node-id="{escaped_el_id}" data-label="{escaped_label}"{p_attr} filter="url(#shadow)">'
                )
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
            lines.append("  </g>")
            lines.extend(self._render_interactive_controls(width, height))
            lines.extend(self._render_interactive_minimap(width, height))
            lines.extend(self._render_interactive_script(width, height))

        lines.append("</svg>")
        return "\n".join(lines)
