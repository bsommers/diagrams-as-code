"""Standing waves on a string fixed at both ends: the first five harmonics.

Each row is $y_n(x, t) = A \\sin(n\\pi x / L)\\cos(2\\pi f_n t)$, drawn at the
two extreme displacements (solid) and partway between (dashed). The nodes are the zeros of the sine, so they are
computed rather than placed; wavelength and frequency follow from
$\\lambda_n = 2L/n$ and $f_n = n f_1$.
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

from diagrams_as_code import Diagram, Style
from diagrams_as_code.output import render_all

L_PX, X0 = 460.0, 190.0
AMP, PITCH, TOP = 26.0, 84.0, 90.0
HARMONICS = 5
F1, LENGTH_M = 110.0, 0.65  # fundamental (Hz) and string length (m); v = 2 L f1
INK, BLUE = "#111111", "#1F2F57"


def curve(n: int, y0: float, phase: float, steps: int = 160):
    pts = []
    for i in range(steps + 1):
        u = i / steps
        pts.append((X0 + u * L_PX, y0 - AMP * phase * math.sin(n * math.pi * u)))
    return pts


def diagram() -> Diagram:
    v = 2 * LENGTH_M * F1
    with Diagram("Standing waves on a string", theme="paper") as diag:
        for n in range(1, HARMONICS + 1):
            y0 = TOP + (n - 1) * PITCH
            for x, side in ((X0, -1), (X0 + L_PX, 1)):  # fixed ends: a wall with hatching
                diag.polyline([(x, y0 - AMP - 10), (x, y0 + AMP + 10)], style=Style(stroke=INK, stroke_width=2.0))
                hatch = " ".join(f"M {x:.1f} {y0 - AMP - 10 + 8 * k:.1f} l {side * 7} 7" for k in range(0, int((2 * AMP + 20) / 8)))
                diag.path(hatch, style=Style(fill="none", stroke=INK, stroke_width=0.8))
            diag.polyline([(X0, y0), (X0 + L_PX, y0)], style=Style(stroke="#B5B9C4", stroke_width=0.8), obstacle=False)
            diag.polyline(curve(n, y0, 1.0), style=Style(stroke=BLUE, stroke_width=2.0))
            diag.polyline(curve(n, y0, -1.0), style=Style(stroke=BLUE, stroke_width=2.0))
            diag.polyline(curve(n, y0, 0.5), style=Style(stroke="#7C8AA8", stroke_width=1.1, dash="4,3"))
            for k in range(n + 1):  # nodes at x = k L / n
                diag.point(X0 + k * L_PX / n, y0, dot=True, radius=3.2)
            name = "fundamental" if n == 1 else f"harmonic {n}"
            diag.text(f"$n = {n}$  {name}", size=13, align="right").at(X0 - 30, y0, anchor="right_center")
            lam = "2L" if n == 1 else f"2L/{n}"
            diag.text(
                f"$\\lambda_{n} = {lam}$ = {2 * LENGTH_M / n:.3f} m\n$f_{n} = {n}f_1$ = {n * F1:g} Hz",
                size=12,
            ).at(X0 + L_PX + 40, y0, anchor="left_center")

        bottom = TOP + (HARMONICS - 1) * PITCH + AMP + 34
        diag.connect((X0, bottom), (X0 + L_PX, bottom), routing="direct", two_way=True, width=0.8, arrow_size=0.6)
        diag.text(f"$L = {LENGTH_M}$ m", size=13).at(X0 + L_PX / 2, bottom + 6, anchor="top_center")
        diag.leader("antinode", (X0 + L_PX / 2, TOP - AMP), at=(X0 + L_PX / 2 + 40, TOP - AMP - 28),
                    anchor="bottom_left", head="circle")
        diag.leader("node", (X0 + L_PX / 2, TOP + PITCH), at=(X0 + L_PX / 2 + 30, TOP + PITCH - AMP - 14),
                    anchor="bottom_left", head="circle")
        diag.text(
            f"Wave speed $v = 2 L f_1 = {v:g}$ m/s. Solid: extreme displacements; dashed: partway between them.",
            size=12, font="serif", italic=True,
        ).at(X0 + L_PX / 2, bottom + 34, anchor="top_center")
        diag.caption("**Figure 6:** The first five harmonics of a string fixed at both ends, with nodes at the zeros of the mode",
                     small_caps=True)
    return diag


def build_diagram(output_dir: Path | str = "output/physics") -> Path:
    return render_all(diagram(), output_dir, "06_standing_waves")["svg"]


if __name__ == "__main__":
    dest = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("output/physics")
    build_diagram(dest)
