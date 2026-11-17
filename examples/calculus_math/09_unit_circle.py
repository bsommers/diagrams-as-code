"""Sine, cosine and tangent on the unit circle.

The point P = (cos t, sin t) is placed from the angle; the sine is the vertical
leg, the cosine the horizontal leg, and the tangent is the length cut off on the
vertical line x = 1 by the ray through P. The values listed are computed from t.
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

from diagrams_as_code import Diagram
from diagrams_as_code.output import render_all
from diagrams_as_code.plot import Plot

NAME = "09_unit_circle"
THETA = math.radians(40)
BLUE, RED, GREEN, ORANGE = "#1F2F57", "#C0392B", "#2E8B57", "#8A5A00"


def diagram() -> Diagram:
    c, s, t = math.cos(THETA), math.sin(THETA), math.tan(THETA)
    with Diagram("Unit circle construction", theme="paper") as diag:
        p = Plot(diag, x=(-1.5, 1.8), y=(-1.4, 1.4), origin=(70, 340), size=(363, 308))
        p.axes(xlabel="$x$", ylabel="$y$", labels=False, xstep=1, ystep=1)
        p.parametric(math.cos, math.sin, 0, math.tau, stroke=BLUE, width=2.0)
        p.line((1, -1.4), (1, 1.4), stroke="#7C8AA8", dash="5,4", width=1.0)
        p.line((0, 0), (1, t), stroke=BLUE, width=1.4)
        p.line((c, 0), (c, s), stroke=RED, width=3.0)
        p.line((0, 0), (c, 0), stroke=GREEN, width=3.0)
        p.line((1, 0), (1, t), stroke=ORANGE, width=3.0)
        p.parametric(lambda a: 0.22 * math.cos(a), lambda a: 0.22 * math.sin(a), 0, THETA, stroke=BLUE, width=1.2, n=60)
        p.dot(c, s, radius=4.0)
        p.dot(1, 0, radius=3.0)
        p.dot(1, t, radius=3.0)
        p.label(0.3 * math.cos(THETA / 2), 0.3 * math.sin(THETA / 2), r"$\theta$", size=13, anchor="left_center", dx=6)
        p.label(c, s, "$P$", size=13, anchor="bottom_right", dx=-8, dy=-8)
        p.label(c, s / 2, r"$\sin\theta$", size=13, color=RED, anchor="right_center", dx=-6)
        p.label(c / 2, 0, r"$\cos\theta$", size=13, color=GREEN, anchor="top_center", dy=8)
        p.label(1, t / 2, r"$\tan\theta$", size=13, color=ORANGE, anchor="left_center", dx=8)
        p.label(1, 0, "$1$", size=12, anchor="top_left", dx=4, dy=6)
        p.label(-1, 0, "$-1$", size=12, anchor="top_right", dx=-4, dy=6)
        p.label(0, 1, "$1$", size=12, anchor="bottom_left", dx=6, dy=-2)
        p.label(0, -1, "$-1$", size=12, anchor="top_left", dx=6, dy=2)

        diag.text("**Computed**", size=13).at(520, 120, anchor="left_center")
        diag.text(f"$\\theta = {math.degrees(THETA):g}^\\circ = {THETA:.4f}$ rad", size=13).at(520, 152, anchor="left_center")
        diag.text(f"$\\cos\\theta = {c:.4f}$", size=13, color=GREEN).at(520, 186, anchor="left_center")
        diag.text(f"$\\sin\\theta = {s:.4f}$", size=13, color=RED).at(520, 212, anchor="left_center")
        diag.text(f"$\\tan\\theta = {t:.4f}$", size=13, color=ORANGE).at(520, 238, anchor="left_center")
        diag.text(f"$\\sin\\theta / \\cos\\theta = {s / c:.4f}$", size=12).at(520, 274, anchor="left_center")
        diag.text(f"$(\\cos\\theta)^2 + (\\sin\\theta)^2 = {c * c + s * s:.4f}$", size=12).at(520, 300, anchor="left_center")
        diag.caption(
            "**Figure 9:** On the unit circle the sine and cosine are the legs of the right triangle "
            "below a point, and the tangent is cut off by the ray on the line through 1",
            small_caps=True,
        )
    return diag


def build_diagram(output_dir: Path | str = "output/calculus_math") -> Path:
    return render_all(diagram(), output_dir, NAME)["svg"]


if __name__ == "__main__":
    build_diagram(Path(sys.argv[1]) if len(sys.argv) > 1 else Path("output/calculus_math"))
