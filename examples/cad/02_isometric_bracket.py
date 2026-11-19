"""Isometric view of an L-bracket with dimensions.

Model axes: x to the lower right, z to the lower left, y up. Screen
x = (x - z) cos 30, screen y = -y + (x + z) sin 30. Faces are drawn
from the same parameters as Figure 1.
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

from diagrams_as_code import Diagram, Style
from diagrams_as_code.draft import Draft
from diagrams_as_code.output import render_all

W, D, H, T_, DH = 80.0, 50.0, 45.0, 10.0, 10.0  # mm
HOLE_X = (W * 0.25, W * 0.75)
S = 3.6
C30, S30 = math.cos(math.radians(30)), math.sin(math.radians(30))
INK = "#1F2F57"
ORIGIN = (330.0, 150.0)


def iso(x, y, z):
    return (ORIGIN[0] + (x - z) * C30 * S, ORIGIN[1] + (-y + (x + z) * S30) * S)


def diagram() -> Diagram:
    hz = (T_ + D) / 2.0
    face = lambda c: Style(fill=c, stroke=INK, stroke_width=1.8)
    with Diagram("Isometric view of an L-bracket", theme="paper") as diag:
        k = Draft(diag)
        # End cap at x = W (profile in z-y), then the tops and the +z faces.
        prof = [(0, 0), (D, 0), (D, T_), (T_, T_), (T_, H), (0, H)]
        diag.polygon([iso(W, y, z) for z, y in prof], style=face("#B9C9DE"))
        diag.polygon([iso(0, H, 0), iso(W, H, 0), iso(W, H, T_), iso(0, H, T_)], style=face("#EAF0F8"))
        diag.polygon([iso(0, T_, T_), iso(W, T_, T_), iso(W, T_, D), iso(0, T_, D)], style=face("#EAF0F8"))
        diag.polygon([iso(0, H, T_), iso(W, H, T_), iso(W, T_, T_), iso(0, T_, T_)], style=face("#D3DEEC"))
        diag.polygon([iso(0, T_, D), iso(W, T_, D), iso(W, 0, D), iso(0, 0, D)], style=face("#D3DEEC"))
        # Holes: ellipses (circles in the x-z plane) with a shaded bore.
        for hx in HOLE_X:
            ring = [iso(hx + DH / 2 * math.cos(a / 24 * math.tau), T_, hz + DH / 2 * math.sin(a / 24 * math.tau))
                    for a in range(24)]
            diag.polygon(ring, style=Style(fill="#8FA2BD", stroke=INK, stroke_width=1.6))
            k.centerline(iso(hx, T_, hz - 9), iso(hx, T_, hz + 9))
            k.centerline(iso(hx - 9, T_, hz), iso(hx + 9, T_, hz))
        # Dimensions.
        k.dimension(iso(0, 0, D), iso(W, 0, D), f"${W:g}$", offset=26, side=1)
        k.dimension(iso(W, 0, D), iso(W, 0, 0), f"${D:g}$", offset=26, side=1)
        k.dimension(iso(W, 0, 0), iso(W, H, 0), f"${H:g}$", offset=30, side=1)
        k.dimension(iso(0, T_, D), iso(0, 0, D), f"${T_:g}$", offset=30, side=1)
        k.leader(iso(HOLE_X[0], T_, hz - 2), (iso(0, 0, D)[0] - 105, iso(0, T_, D)[1] - 70),
                 f"2 $\\times$ $\\emptyset{DH:g}$ THRU", anchor="right_center")
        k.leader(iso(0, H, 0.5 * T_), (iso(0, H, 0)[0] - 60, iso(0, H, 0)[1] - 42),
                 f"wall $t = {T_:g}$", anchor="right_center")
        # Axis triad.
        o = (90.0, 330.0)
        for lab, v in (("$x$", (C30, S30)), ("$z$", (-C30, S30)), ("$y$", (0, -1))):
            e = (o[0] + v[0] * 34, o[1] + v[1] * 34)
            k.d.path(f"M {o[0]} {o[1]} L {e[0]:.1f} {e[1]:.1f}", style=Style(fill="none", stroke=INK, stroke_width=1.2))
            diag.text(lab, size=12).at(e[0] + v[0] * 9, e[1] + v[1] * 9, anchor="center")
        diag.text("All dimensions in mm", size=12).at(40, 400, anchor="left_center")
        diag.caption(
            "**Figure 2:** Isometric view of the L-bracket; the same parameters as Figure 1 give every edge length",
            small_caps=True)
    return diag


def build_diagram(output_dir: Path | str = "examples/cad") -> Path:
    return render_all(diagram(), output_dir, "02_isometric_bracket")["svg"]


if __name__ == "__main__":
    dest = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("examples/cad")
    build_diagram(dest)
