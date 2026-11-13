"""The pan, zoom, search and minimap overlay of an interactive SVG.

Kept apart from the drawing passes in ``renderer_svg``: nothing here depends on
the diagram's content, only on the theme and the canvas size.
"""
from __future__ import annotations

from diagrams_as_code.theme import Theme


class InteractiveOverlay:
    """Styles, controls, minimap and script for ``Diagram(interactive=True)``."""

    theme: Theme

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
