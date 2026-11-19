"""Logistic growth y' = r y (1 - y / K) with its equilibria.

Left: solution curves in the (t, y) plane, RK4 from four initial values. All
settle at the carrying capacity K; the curve from below K is S-shaped with its
inflection at K / 2. Right: the phase line, y' against y, whose zeros are the
equilibria: y = 0 repels (open dot) and y = K attracts (filled dot).
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

from diagrams_as_code import Diagram
from diagrams_as_code.output import render_all
from diagrams_as_code.plot import Plot

NAME = "03_logistic"
R, CAP = 1.0, 10.0
INK, BLUE, AMBER, RED = "#1F2F57", "#2E6F9E", "#8A5A00", "#9C2B2B"


def f(t: float, y: float) -> float:
    return R * y * (1 - y / CAP)


def exact(t: float, y0: float) -> float:
    return CAP / (1 + (CAP / y0 - 1) * math.exp(-R * t))


def diagram() -> Diagram:
    with Diagram("Logistic growth", theme="paper") as diag:
        a = Plot(diag, x=(0, 8), y=(0, 14), origin=(80, 420), size=(420, 300))
        a.grid(xstep=2, ystep=2)
        a.axes(xlabel="$t$", ylabel="$y$", xstep=2, ystep=2)
        a.hline(CAP)
        a.hline(CAP / 2, stroke="#7C8AA8", dash="2,4")
        for y0, colour in ((0.5, INK), (2.0, BLUE), (5.0, INK), (14.0, BLUE)):
            pts = a.solve_ode(f, 0.0, y0, x1=8.0, steps=320, stroke=colour, width=2.0)
            assert abs(pts[-1][1] - exact(8.0, y0)) < 1e-6
            a.dot(0, y0, radius=3)
        a.label(8, CAP, "$K$", size=13, color=AMBER, anchor="left_center", dx=24, dy=-12)
        a.label(8, CAP / 2, "$K / 2$", size=12, anchor="left_center", dx=24)
        # Inflection of the curve from y0 = 0.5, where y reaches K / 2.
        t_half = math.log(CAP / 0.5 - 1) / R
        a.dot(t_half, CAP / 2, radius=3.5, label="inflection", size=12, dx=8, dy=14, anchor="top_left")
        diag.text("Solutions  $y(t)$", size=14).at(290, 82, anchor="bottom_center")

        b = Plot(diag, x=(-2, 13), y=(-3, 4), origin=(620, 420), size=(360, 300))
        b.grid(xstep=2, ystep=1)
        b.axes(xlabel="$y$", ylabel="$y'$", xstep=2, ystep=1)
        b.function(lambda y: f(0, y), -2, 13, stroke=INK, width=2.0)
        diag.text("Phase line  $y' = r y (1 - y / K)$", size=14).at(800, 82, anchor="bottom_center")
        # Arrows on the y axis show the direction of flow between equilibria.
        base = b.px(0, 0)[1]
        for lo, hi in ((-1.6, -0.4), (1.2, 8.8), (10.8, 12.6)):
            lo_p, hi_p = b.px(lo, 0), b.px(hi, 0)
            right = hi > lo
            flow = right if lo > -1 and hi < CAP + 3 else False
            if lo < 0:
                flow = False  # y' < 0 for y < 0, flow to the left
            if hi > CAP:
                flow = False  # y' < 0 for y > K, flow to the left
            a0, a1 = (lo_p, hi_p) if flow else (hi_p, lo_p)
            diag.connect((a0[0], base - 14), (a1[0], base - 14), routing="direct", width=1.8, color=RED, head="stealth")
        b.dot(0, 0, radius=4.5)
        b.dot(CAP, 0, radius=4.5)
        b.label(0, 0, "unstable", size=11, anchor="bottom_right", dx=-18, dy=-24)
        b.label(CAP, 0, "stable", size=11, anchor="bottom_left", dx=4, dy=-24)
        diag.caption(
            "**Figure 3:** Logistic growth with $r = 1$, $K = 10$: solution curves approach the carrying "
            "capacity (left); the phase line shows $y = 0$ unstable and $y = K$ stable (right)",
            small_caps=True,
        )
    return diag


def build_diagram(output_dir: Path | str = "examples/differential_equations") -> Path:
    return render_all(diagram(), output_dir, NAME)["svg"]


if __name__ == "__main__":
    dest = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("examples/differential_equations")
    build_diagram(dest)
