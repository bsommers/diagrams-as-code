"""Taylor polynomials of sin x converging.

Each polynomial T_n is built from the series sin x = x - x^3/3! + x^5/5! - ...
and plotted with sin x. The largest error on [-pi, pi] is measured on a fine
grid and listed beside the plot.
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

from diagrams_as_code import Diagram
from diagrams_as_code.output import render_all
from diagrams_as_code.plot import Plot

NAME = "05_taylor_sine"
DEGREES = [1, 3, 5, 7, 9]
COLOURS = ["#C0392B", "#D9822B", "#2E8B57", "#2F7FB5", "#6B4BA1"]


def taylor(n: int):
    def poly(x: float) -> float:
        return sum((-1) ** k * x ** (2 * k + 1) / math.factorial(2 * k + 1) for k in range((n + 1) // 2))
    return poly


def max_error(n: int) -> float:
    t = taylor(n)
    xs = [-math.pi + 2 * math.pi * i / 2000 for i in range(2001)]
    return max(abs(t(x) - math.sin(x)) for x in xs)


def diagram() -> Diagram:
    with Diagram("Taylor polynomials of sine", theme="paper") as diag:
        p = Plot(diag, x=(-7, 7), y=(-2.5, 2.5), origin=(60, 300), size=(520, 260))
        p.grid(2, 1)
        p.axes(xlabel="$x$", xstep=2, ystep=1)
        p.function(math.sin, stroke="#1F2F57", width=3.0, n=600)
        for n, colour in zip(DEGREES, COLOURS):
            p.function(taylor(n), stroke=colour, width=1.5, n=600)

        diag.text("**Polynomial**", size=13).at(660, 120, anchor="left_center")
        diag.text("**Max error**", size=13).at(790, 120, anchor="left_center")
        diag.text("on $[-\\pi, \\pi]$", size=11).at(790, 140, anchor="left_center")
        diag.text("$\\sin x$", size=13, color="#1F2F57").at(660, 176, anchor="left_center")
        diag.text("exact", size=12, color="#1F2F57").at(790, 176, anchor="left_center")
        y = 206
        for n, colour in zip(DEGREES, COLOURS):
            diag.text(f"$T_{{{n}}}(x)$", size=13, color=colour).at(660, y, anchor="left_center")
            diag.text(f"{max_error(n):.3g}", size=12, color=colour).at(790, y, anchor="left_center")
            y += 28
        diag.caption(
            "**Figure 5:** Taylor polynomials of the sine about zero hug the curve over a wider "
            "interval with each added term",
            small_caps=True,
        )
    return diag


def build_diagram(output_dir: Path | str = "output/calculus_math") -> Path:
    return render_all(diagram(), output_dir, NAME)["svg"]


if __name__ == "__main__":
    build_diagram(Path(sys.argv[1]) if len(sys.argv) > 1 else Path("output/calculus_math"))
