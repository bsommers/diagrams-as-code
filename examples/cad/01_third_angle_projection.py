"""Third-angle orthographic projection of an L-bracket.

The part is parametric: width W, depth D, height H, wall t and two through
holes of diameter d. Every view is computed from those numbers at one scale.
"""
from __future__ import annotations

import sys
from pathlib import Path

from diagrams_as_code import Diagram, Style
from diagrams_as_code.draft import Draft
from diagrams_as_code.output import render_all

W, D, H, T_, DH = 80.0, 50.0, 45.0, 10.0, 10.0  # mm
HOLE_X = (W * 0.25, W * 0.75)
S = 3.0  # px per mm
INK = "#1F2F57"
FILL = "#DCE6F2"
PROJ = Style(fill="none", stroke="#8A93A6", stroke_width=0.6, dash="2,3")


def diagram() -> Diagram:
    hz = (T_ + D) / 2.0  # hole centre depth from the back face
    fx, fy = 60.0, 330.0                 # front view: bottom-left
    gap = 70.0
    tx, ty = fx, fy - H * S - gap        # top view: above, bottom-left at (tx, ty)
    rx = fx + W * S + gap                # right view: to the right

    def front(x, y):  # mm -> px
        return (fx + x * S, fy - y * S)

    def top(x, z):    # z = distance from back face; front of part at bottom
        return (tx + x * S, ty - (D - z) * S)

    def right(z, y):  # front face (z=D) at the left
        return (rx + (D - z) * S, fy - y * S)

    with Diagram("Third-angle projection of an L-bracket", theme="paper") as diag:
        k = Draft(diag)
        # Front view.
        fv = [front(0, 0), front(W, 0), front(W, H), front(0, H)]
        diag.polygon(fv, style=Style(fill=FILL, stroke="none"), z=-2)
        k.outline(fv)
        k.d.path(f"M {front(0, T_)[0]} {front(0, T_)[1]} L {front(W, T_)[0]} {front(W, T_)[1]}",
                 style=Style(fill="none", stroke=INK, stroke_width=1.4))
        for hx in HOLE_X:
            for off in (-DH / 2, DH / 2):
                k.hidden_line([front(hx + off, 0), front(hx + off, T_)])
            k.centerline(front(hx, -3), front(hx, T_ + 3))
        # Top view.
        tv = [top(0, 0), top(W, 0), top(W, D), top(0, D)]
        diag.polygon(tv, style=Style(fill=FILL, stroke="none"), z=-2)
        k.outline(tv)
        k.d.path(f"M {top(0, T_)[0]} {top(0, T_)[1]} L {top(W, T_)[0]} {top(W, T_)[1]}",
                 style=Style(fill="none", stroke=INK, stroke_width=1.4))
        for hx in HOLE_X:
            c = top(hx, hz)
            r = DH / 2 * S
            diag.path(f"M {c[0] - r} {c[1]} a {r} {r} 0 1 0 {2 * r} 0 a {r} {r} 0 1 0 {-2 * r} 0",
                      style=Style(fill="#FFFFFF", stroke=INK, stroke_width=2.0))
            k.centerline((c[0] - r - 6, c[1]), (c[0] + r + 6, c[1]))
            k.centerline((c[0], c[1] - r - 6), (c[0], c[1] + r + 6))
        # Right view.
        rv = [right(D, 0), right(0, 0), right(0, H), right(D - D + T_, H), right(T_, T_), right(D, T_)]
        diag.polygon(rv, style=Style(fill=FILL, stroke="none"), z=-2)
        k.outline(rv)
        for hx in (HOLE_X[0],):
            for off in (-DH / 2, DH / 2):
                p = hz + off
                k.hidden_line([right(p, 0), right(p, T_)])
        k.centerline(right(hz, -3), right(hz, T_ + 3))
        # Projection lines.
        for x in (0, W):
            diag.path(f"M {front(x, H)[0]} {front(x, H)[1] - 4} L {top(x, 0)[0]} {top(x, D)[1] + 4}"
                      if False else
                      f"M {front(x, H)[0]} {front(x, H)[1] - 4} L {top(x, 0)[0]} {top(x, 0)[1] + 4}", style=PROJ)
        for y in (0, T_, H):
            diag.path(f"M {front(W, y)[0] + 4} {front(W, y)[1]} L {right(D, y)[0] - 4} {right(D, y)[1]}", style=PROJ)
        # Dimensions (generously offset).
        k.dimension(front(0, 0), front(W, 0), f"${W:g}$", offset=30, side=1)
        k.dimension(front(0, 0), front(0, H), f"${H:g}$", offset=34, side=-1)
        k.dimension(top(W, D), top(W, 0), f"${D:g}$", offset=30, side=1)
        k.dimension(right(D, 0), right(0, 0), f"${D:g}$", offset=30, side=1)
        k.dimension(right(0, H), right(0, 0), f"${H:g}$", offset=34, side=-1)
        k.dimension(right(T_, H), right(0, H), f"${T_:g}$", offset=22, side=-1)
        # View titles.
        diag.text("FRONT", size=12).at(front(W / 2, 0)[0], fy + 62, anchor="center")
        diag.text("TOP", size=12).at(top(W / 2, 0)[0], ty + 20 + 2 * 0, anchor="center")
        diag.text("RIGHT", size=12).at(right(D / 2, 0)[0], fy + 62, anchor="center")
        # Third-angle symbol: end view (circles) on the left, frustum on the right.
        sx, sy = rx + 10, ty - 50
        for r in (13, 22):
            diag.path(f"M {sx + 22 - r} {sy + 22} a {r} {r} 0 1 0 {2 * r} 0 a {r} {r} 0 1 0 {-2 * r} 0",
                      style=Style(fill="none", stroke=INK, stroke_width=1.3))
        k.centerline((sx - 8, sy + 22), (sx + 90, sy + 22))
        diag.polygon([(sx + 50, sy), (sx + 85, sy + 7), (sx + 85, sy + 37), (sx + 50, sy + 44)],
                     style=Style(fill="none", stroke=INK, stroke_width=1.3))
        diag.text("THIRD-ANGLE", size=10).at(sx + 45, sy + 60, anchor="center")
        diag.text(f"All dimensions in mm. Wall $t = {T_:g}$, two $\\emptyset{DH:g}$ through holes at $x = {HOLE_X[0]:g}$ and ${HOLE_X[1]:g}$.",
                  size=12).at(fx, fy + 100, anchor="left_center")
        diag.caption(
            "**Figure 1:** Third-angle orthographic projection of an L-bracket; the top view sits above the front view and the right view to its right",
            small_caps=True)
    return diag


def build_diagram(output_dir: Path | str = "examples/cad") -> Path:
    return render_all(diagram(), output_dir, "01_third_angle_projection")["svg"]


if __name__ == "__main__":
    dest = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("examples/cad")
    build_diagram(dest)
