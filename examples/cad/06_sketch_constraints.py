"""A 2D parametric sketch with geometric constraints and driving dimensions.

A slot (two parallel lines closed by two equal tangent arcs) and a rectangle
are placed from a fixed origin. Geometry is computed from the dimensions
(L = 90, R = 20, angle = 15 degrees, rectangle 75 x 45 mm at x = 120 mm), then
constraint glyphs are attached to the entities they act on.
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

from diagrams_as_code import Diagram, Style
from diagrams_as_code.draft import Draft
from diagrams_as_code.output import render_all

L, R, ANG = 90.0, 20.0, 15.0     # slot: centre distance, end radius, tilt (mm, mm, deg)
RW, RH, RX = 75.0, 45.0, 120.0   # rectangle width, height, offset from origin (mm)
S = 2.4
INK = "#1F2F57"
GREEN = "#2E6B3F"
BLUE = "#1F4FA8"
O = (110.0, 330.0)               # sketch origin (slot centre C1), pixels


def p(a, b, k=1.0):
    return (a[0] + b[0] * k, a[1] + b[1] * k)


def glyph(diag, text, at, color=GREEN, size=11):
    x, y = at
    diag.polygon([(x - 10, y - 9), (x + 10, y - 9), (x + 10, y + 9), (x - 10, y + 9)],
                 style=Style(fill="#FFFFFF", stroke=color, stroke_width=1.2), z=3)
    diag.text(text, size=size, color=color, z=4).at(x, y, anchor="center")


def circle(diag, c, r, style):
    diag.path(f"M {c[0] - r:.2f} {c[1]:.2f} a {r} {r} 0 1 0 {2 * r} 0 a {r} {r} 0 1 0 {-2 * r} 0", style=style)


def diagram() -> Diagram:
    th = math.radians(ANG)
    u = (math.cos(th), -math.sin(th))        # axis direction (screen)
    nu = (-math.sin(th), -math.cos(th))      # normal, up-left
    r = R * S
    c1 = O
    c2 = p(c1, u, L * S)
    a1, a2 = p(c1, nu, r), p(c2, nu, r)       # upper line ends
    b1, b2 = p(c1, nu, -r), p(c2, nu, -r)     # lower line ends
    with Diagram("Sketch with geometric constraints", theme="paper") as diag:
        k = Draft(diag, ink=INK)
        slot = (f"M {a1[0]:.2f} {a1[1]:.2f} L {a2[0]:.2f} {a2[1]:.2f} A {r:.2f} {r:.2f} 0 0 1 {b2[0]:.2f} {b2[1]:.2f} "
                f"L {b1[0]:.2f} {b1[1]:.2f} A {r:.2f} {r:.2f} 0 0 1 {a1[0]:.2f} {a1[1]:.2f} Z")
        diag.path(slot, style=Style(fill="#E6EEF8", stroke=INK, stroke_width=2.2))
        k.centerline(p(c1, u, -r - 14), p(c2, u, r + 14))
        # Origin reference line, rectangle.
        k.centerline((O[0] - 40, O[1]), (O[0] + (RX + RW) * S + 40, O[1]))
        rx0 = O[0] + RX * S
        rect = [(rx0, O[1]), (rx0 + RW * S, O[1]), (rx0 + RW * S, O[1] - RH * S), (rx0, O[1] - RH * S)]
        diag.polygon(rect, style=Style(fill="#E6EEF8", stroke=INK, stroke_width=2.2))
        # Fixed origin: anchor glyph at C1.
        diag.polygon([(c1[0], c1[1]), (c1[0] - 8, c1[1] + 13), (c1[0] + 8, c1[1] + 13)],
                     style=Style(fill=GREEN, stroke=GREEN, stroke_width=1), z=3)
        # Coincident points (ringed) at slot junctions and rectangle corners.
        for q in (a1, a2, b1, b2, *rect):
            circle(diag, q, 4.5, Style(fill="#FFFFFF", stroke=GREEN, stroke_width=1.3))
        # Constraint glyphs.
        mid = lambda a, b: ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2)
        glyph(diag, "//", p(mid(a1, a2), nu, 22))
        glyph(diag, "//", p(mid(b1, b2), nu, -22))
        glyph(diag, "T", p(a2, (u[0] + nu[0], u[1] + nu[1]), 14))
        glyph(diag, "T", p(b2, (u[0] - nu[0], u[1] - nu[1]), 14))
        glyph(diag, "T", p(a1, (-u[0] + nu[0], -u[1] + nu[1]), 14))
        glyph(diag, "T", p(b1, (-u[0] - nu[0], -u[1] - nu[1]), 14))
        glyph(diag, "=", p(c2, u, r + 26))
        glyph(diag, "=", p(c1, u, -r - 26))
        glyph(diag, "H", (rx0 + RW * S / 2, O[1] + 22))
        glyph(diag, "H", (rx0 + RW * S / 2, O[1] - RH * S - 22))
        glyph(diag, "V", (rx0 + RW * S - 22, O[1] - RH * S / 2))
        glyph(diag, "V", (rx0 + 22, O[1] - RH * S / 2))
        glyph(diag, "$\\perp$", (rx0 + 52, O[1] - 24), size=12)
        # Driving dimensions (blue).
        kb = Draft(diag, ink=BLUE)
        kb.dimension(c1, c2, f"${L:g}$", offset=112, side=-1)
        kb.radius_dim(c2, r, 50, f"$R{R:g}$", overshoot=40)
        kb.dimension((rx0, O[1]), (rx0 + RW * S, O[1]), f"${RW:g}$", offset=62, side=1)
        kb.dimension((rx0 + RW * S, O[1]), (rx0 + RW * S, O[1] - RH * S), "", offset=66, side=1)
        diag.text(f"${RH:g}$", size=11, color=BLUE).at(rx0 + RW * S + 66 + 12, O[1] - RH * S / 2, anchor="left_center")
        kb.dimension(O, (rx0, O[1]), f"${RX:g}$", offset=96, side=1)
        arc_r = 98.0
        diag.path(f"M {O[0] + arc_r:.2f} {O[1]:.2f} A {arc_r} {arc_r} 0 0 0 {O[0] + arc_r * u[0]:.2f} {O[1] + arc_r * u[1]:.2f}",
                  style=Style(fill="none", stroke=BLUE, stroke_width=0.9))
        diag.text(f"${ANG:g}^\\circ$", size=12, color=BLUE).at(O[0] + arc_r + 12, O[1] - 16, anchor="left_center")
        # Legend.
        lx, ly = 730.0, 110.0
        diag.text("Constraint key", size=14).at(lx, ly - 28, anchor="left_center")
        items = [("//", "Parallel"), ("T", "Tangent"), ("=", "Equal"), ("H", "Horizontal"),
                 ("V", "Vertical"), ("$\\perp$", "Perpendicular")]
        for i, (g, name) in enumerate(items):
            glyph(diag, g, (lx + 10, ly + i * 30))
            diag.text(name, size=12).at(lx + 30, ly + i * 30, anchor="left_center")
        yy = ly + len(items) * 30
        circle(diag, (lx + 10, yy), 4.5, Style(fill="#FFFFFF", stroke=GREEN, stroke_width=1.3))
        diag.text("Coincident point", size=12).at(lx + 30, yy, anchor="left_center")
        diag.polygon([(lx + 10, yy + 22), (lx + 2, yy + 36), (lx + 18, yy + 36)], style=Style(fill=GREEN, stroke=GREEN))
        diag.text("Fixed to origin", size=12).at(lx + 30, yy + 30, anchor="left_center")
        diag.path(f"M {lx} {yy + 62} L {lx + 20} {yy + 62}", style=Style(fill="none", stroke=BLUE, stroke_width=1.6))
        diag.text("Driving dimension (mm)", size=12, color=BLUE).at(lx + 30, yy + 62, anchor="left_center")
        diag.text("Slot: origin 2 + $L$ 1 + angle 1 + $R$ 1 = 5 DOF removed,\nso it is fully constrained.",
                  size=12).at(lx, yy + 105, anchor="top_left")
        diag.caption(
            "**Figure 6:** A 2D sketch with geometric constraints (parallel, tangent, equal, horizontal, vertical, perpendicular, coincident, fixed) and driving dimensions",
            small_caps=True)
    return diag


def build_diagram(output_dir: Path | str = "examples/cad") -> Path:
    return render_all(diagram(), output_dir, "06_sketch_constraints")["svg"]


if __name__ == "__main__":
    dest = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("examples/cad")
    build_diagram(dest)
