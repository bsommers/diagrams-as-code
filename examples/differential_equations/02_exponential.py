"""Exponential growth and decay: y' = k y.

Two panels share one form. For k > 0 the solutions double every ln 2 / k; for
k < 0 they halve every ln 2 / |k|. The curves are RK4 solutions and the script
checks them against y0 e^{kt}; the marked doubling time and half-life are
computed from k.
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

from diagrams_as_code import Diagram
from diagrams_as_code.output import render_all
from diagrams_as_code.plot import Plot

NAME = "02_exponential"
K = 0.6
INK, BLUE, AMBER = "#1F2F57", "#2E6F9E", "#8A5A00"


def panel(diag: Diagram, k: float, starts: list[float], origin, ymax: float, title: str) -> Plot:
    p = Plot(diag, x=(0, 4), y=(0, ymax), origin=origin, size=(380, 280))
    p.grid(xstep=1, ystep=1)
    p.axes(xlabel="$t$", ylabel="$y$", xstep=1, ystep=1)
    for y0, colour in zip(starts, (INK, BLUE, INK)):
        pts = p.solve_ode(lambda t, y: k * y, 0.0, y0, x1=4.0, steps=200, stroke=colour, width=2.0)
        assert abs(pts[-1][1] - y0 * math.exp(k * 4)) < 1e-4 * max(1.0, y0 * math.exp(k * 4))
        p.dot(0, y0, radius=3)
    diag.text(title, size=14).at(origin[0] + 190, origin[1] - 280 - 38, anchor="bottom_center")
    return p


def diagram() -> Diagram:
    with Diagram("Exponential growth and decay", theme="paper") as diag:
        # Growth: y' = k y, doubling time ln 2 / k from y0 = 1.
        grow = panel(diag, K, [0.5, 1.0, 2.0], (80, 420), 8, f"Growth: $y' = {K} y$, $k > 0$")
        td = math.log(2) / K
        grow.line((0, 2), (td, 2), stroke=AMBER, dash="5,4", width=1.1)
        grow.line((td, 0), (td, 2), stroke=AMBER, dash="5,4", width=1.1)
        grow.label(td, 0, f"$t_d = {td:.2f}$", size=12, color=AMBER, anchor="bottom_left", dx=6, dy=-6)
        grow.label(0.15, 5.0, "$y = y_0 e^{kt}$", size=13, anchor="left_center")
        # Decay: y' = -k y, half-life ln 2 / k from y0 = 4.
        decay = panel(diag, -K, [2.0, 4.0, 6.0], (580, 420), 8, f"Decay: $y' = -{K} y$, $k < 0$")
        th = math.log(2) / K
        decay.line((0, 2), (th, 2), stroke=AMBER, dash="5,4", width=1.1)
        decay.line((th, 0), (th, 2), stroke=AMBER, dash="5,4", width=1.1)
        decay.label(th, 0, f"$t_h = {th:.2f}$", size=12, color=AMBER, anchor="bottom_left", dx=6, dy=-6)
        decay.label(1.9, 6.6, "$y = y_0 e^{-kt}$", size=13, anchor="left_center")
        diag.caption(
            "**Figure 2:** Exponential growth and decay, $y' = k y$: solutions through three initial values, "
            "with the doubling time and half-life $\\ln 2 / |k|$ marked",
            small_caps=True,
        )
    return diag


def build_diagram(output_dir: Path | str = "output/differential_equations") -> Path:
    return render_all(diagram(), output_dir, NAME)["svg"]


if __name__ == "__main__":
    dest = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("output/differential_equations")
    build_diagram(dest)
