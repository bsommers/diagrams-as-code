"""Slope field of y' = x - y with Runge-Kutta solution curves.

Every short segment has the slope the equation assigns to its point, so the
solution curves, integrated here with RK4, run tangent to the field. The exact
solution through (0, y0) is y = x - 1 + (y0 + 1) e^(-x), so every curve
approaches the straight solution y = x - 1; the script checks the RK4 end
values against that formula.
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

from diagrams_as_code import Diagram
from diagrams_as_code.output import render_all
from diagrams_as_code.plot import Plot

NAME = "01_slope_field"


def f(x: float, y: float) -> float:
    return x - y


def diagram() -> Diagram:
    with Diagram("Slope field of y' = x - y", theme="paper") as diag:
        p = Plot(diag, x=(-1, 4), y=(-2, 4), origin=(90, 400), size=(560, 336))
        p.slope_field(f, nx=20, ny=14, length=17)
        p.axes(xlabel="$x$", ylabel="$y$", xstep=1, ystep=1)
        # The straight solution y = x - 1 that all others approach.
        p.line((-1, -2), (4, 3), stroke="#8A5A00", width=1.2, dash="6,4")
        colours = ["#1F2F57", "#2E6F9E", "#1F2F57", "#2E6F9E", "#1F2F57"]
        starts = [3.0, 1.5, -0.5, -1.5, -2.0]
        for y0, colour in zip(starts, colours):
            pts = p.solve_ode(f, 0.0, y0, x1=4.0, steps=400, stroke=colour, width=1.9)
            # Backwards in x as well, to fill the left half of the window.
            h = -1.0 / 200
            x, y = 0.0, y0
            back = [(x, y)]
            for _ in range(200):
                k1 = f(x, y)
                k2 = f(x + h / 2, y + h / 2 * k1)
                k3 = f(x + h / 2, y + h / 2 * k2)
                k4 = f(x + h, y + h * k3)
                y += h / 6 * (k1 + 2 * k2 + 2 * k3 + k4)
                x += h
                back.append((x, y))
            p.polyline(back, stroke=colour, width=1.9)
            p.dot(0, y0, radius=3)
            assert abs(pts[-1][1] - (4 - 1 + (y0 + 1) * math.exp(-4))) < 1e-6
        p.label(4.0, 3.0, "$y = x - 1$", size=12, color="#8A5A00", anchor="left_center", dx=24)
        diag.caption(
            "**Figure 1:** Slope field of $y' = x - y$ with RK4 solution curves through "
            "$(0, y_0)$; all curves approach the line $y = x - 1$",
            small_caps=True,
        )
    return diag


def build_diagram(output_dir: Path | str = "examples/differential_equations") -> Path:
    return render_all(diagram(), output_dir, NAME)["svg"]


if __name__ == "__main__":
    dest = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("examples/differential_equations")
    build_diagram(dest)
