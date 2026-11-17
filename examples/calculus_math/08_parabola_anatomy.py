"""The anatomy of a parabola y = a x^2 + b x + c.

Vertex, axis, roots, focus and directrix are all computed from the three
coefficients. A point P on the curve shows the defining property: its distance
to the focus equals its distance to the directrix.
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

from diagrams_as_code import Diagram
from diagrams_as_code.output import render_all
from diagrams_as_code.plot import Plot

NAME = "08_parabola_anatomy"
A, B, C = 0.2, -0.4, -1.6
PX = 3.4  # the abscissa of the sample point P
BLUE, ORANGE, RED, GREEN = "#1F2F57", "#8A5A00", "#C0392B", "#2E8B57"


def diagram() -> Diagram:
    f = lambda x: A * x * x + B * x + C
    h = -B / (2 * A)
    k = f(h)
    disc = B * B - 4 * A * C
    r1, r2 = (-B - math.sqrt(disc)) / (2 * A), (-B + math.sqrt(disc)) / (2 * A)
    pdist = 1 / (4 * A)
    focus = (h, k + pdist)
    directrix = k - pdist
    py = f(PX)
    to_focus = math.dist((PX, py), focus)
    to_directrix = py - directrix
    with Diagram("Anatomy of a parabola", theme="paper") as diag:
        p = Plot(diag, x=(-3, 5), y=(-4, 4), origin=(70, 340), size=(440, 300))
        p.grid(1, 1)
        p.axes(xlabel="$x$", ylabel="$y$", xstep=1, ystep=1, labels=False)
        p.function(f, stroke=BLUE, width=2.4)
        p.line((h, -4), (h, 4), stroke="#7C8AA8", dash="6,4", width=1.0)
        p.line((-3, directrix), (5, directrix), stroke=ORANGE, width=1.5)
        p.line((PX, py), focus, stroke=GREEN, width=1.5)
        p.line((PX, py), (PX, directrix), stroke=GREEN, width=1.5)
        p.dot(h, k, radius=4.0)
        p.dot(*focus, radius=4.0)
        p.dot(r1, 0, radius=4.0)
        p.dot(r2, 0, radius=4.0)
        p.dot(PX, py, radius=4.0)
        p.label(h, k, f"vertex $({h:g}, {k:g})$", size=12, anchor="top_left", dx=10, dy=8)
        p.label(*focus, f"focus $({focus[0]:g}, {focus[1]:g})$", size=12, color=GREEN, anchor="top_left", dx=8, dy=7)
        p.label(r1, 0, f"$({r1:g}, 0)$", size=12, anchor="top_center", dx=-12, dy=10)
        p.label(r2, 0, f"$({r2:g}, 0)$", size=12, anchor="top_center", dy=10)
        p.label(PX, py, "$P$", size=13, anchor="top_left", dx=8, dy=6)
        p.label(-3, directrix, f"directrix $y = {directrix:g}$", size=12, color=ORANGE, anchor="bottom_left", dx=8, dy=-5)
        p.label(h, 4, "axis $x = 1$", size=12, color="#566180", anchor="left_center", dx=8, dy=14)

        diag.text("**Computed**", size=13).at(590, 110, anchor="left_center")
        rows = [
            f"$y = {A:g}x^2 {B:+g}x {C:+g}$".replace("-", "−"),
            f"vertex $x = -b / 2a = {h:g}$",
            f"$y$ at vertex $= {k:g}$",
            f"$b^2 - 4ac = {disc:g}$",
            f"roots $x = {r1:g}$ and ${r2:g}$",
            f"$1 / 4a = {pdist:g}$",
            f"focus height $= {focus[1]:g}$",
            f"directrix $y = {directrix:g}$",
        ]
        for i, row in enumerate(rows):
            diag.text(row, size=12).at(590, 140 + 26 * i, anchor="left_center")
        diag.text(f"$|PF| = {to_focus:.3f}$", size=13, color=GREEN).at(590, 360, anchor="left_center")
        diag.text(f"distance to directrix $= {to_directrix:.3f}$", size=13, color=GREEN).at(590, 386, anchor="left_center")
        diag.caption(
            "**Figure 8:** The vertex, roots, focus and directrix of a parabola follow from its three "
            "coefficients, and every point on the curve is equally far from focus and directrix",
            small_caps=True,
        )
    return diag


def build_diagram(output_dir: Path | str = "output/calculus_math") -> Path:
    return render_all(diagram(), output_dir, NAME)["svg"]


if __name__ == "__main__":
    build_diagram(Path(sys.argv[1]) if len(sys.argv) > 1 else Path("output/calculus_math"))
