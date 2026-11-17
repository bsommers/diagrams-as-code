"""The derivative as the limit of secant slopes.

Secants through (a, f(a)) and (a + h, f(a + h)) are drawn for shrinking h. Their
slopes are computed from f and listed beside the plot; they approach the slope
of the tangent, which Plot.tangent measures numerically.
"""
from __future__ import annotations

import sys
from pathlib import Path

from diagrams_as_code import Diagram
from diagrams_as_code.output import render_all
from diagrams_as_code.plot import Plot

NAME = "01_derivative_limit"
A = 1.5
STEPS = [(2.0, "#7F99C4"), (1.0, "#5A7DB4"), (0.5, "#2F5799")]


def f(x: float) -> float:
    return 0.2 * x**2 + 0.5


def diagram() -> Diagram:
    with Diagram("Derivative as a limit of secant slopes", theme="paper") as diag:
        p = Plot(diag, x=(0, 5), y=(0, 5), origin=(70, 330), size=(400, 280))
        p.grid(1, 1)
        p.axes(xlabel="$x$", ylabel="$y$", xstep=1, ystep=1)
        p.function(f, stroke="#1F2F57", width=2.2)
        for h, colour in STEPS:
            m = (f(A + h) - f(A)) / h
            p.line((A - 1.2, f(A) - 1.2 * m), (A + h + 1.0, f(A + h) + 1.0 * m), stroke=colour, width=1.4)
            p.dot(A + h, f(A + h), radius=3.0)
        slope = p.tangent(f, A, half=2.6, width=1.8)
        p.dot(A, f(A), radius=4.0)
        p.label(A, 0, "$a$", size=13, anchor="top_center", dy=20)
        p.label(A, f(A), "$(a, f(a))$", size=12, anchor="bottom_right", dx=-8, dy=-6)
        p.label(3.6, f(3.6), "$y = f(x)$", size=13, anchor="bottom_right", dx=-8, dy=-10)
        p.label(A + 2.6, f(A) + slope * 2.6, "tangent", size=12, color="#8A5A00", anchor="left_center", dx=8)

        diag.text("**Secant slopes**", size=13).at(540, 110, anchor="left_center")
        diag.text("$m(h) = (f(a+h) - f(a)) / h$", size=12).at(540, 134, anchor="left_center")
        y = 170
        for h, colour in STEPS:
            m = (f(A + h) - f(A)) / h
            diag.text(f"$h = {h:g}$:  $m = {m:.3f}$", size=13, color=colour).at(540, y, anchor="left_center")
            y += 28
        diag.text(f"$h \\to 0$:  $f'(a) = {slope:.3f}$", size=13, color="#8A5A00").at(540, y, anchor="left_center")
        diag.text(r"$f'(a) = \lim_{h \to 0} (f(a+h) - f(a)) / h$", size=12).at(540, y + 44, anchor="left_center")
        diag.text(f"with $f(x) = 0.2x^2 + 0.5$, $a = {A:g}$", size=12).at(540, y + 80, anchor="left_center")

        diag.caption(
            "**Figure 1:** Secant lines tilt toward the tangent as the step shrinks; "
            "their computed slopes converge to the derivative",
            small_caps=True,
        )
    return diag


def build_diagram(output_dir: Path | str = "output/calculus_math") -> Path:
    return render_all(diagram(), output_dir, NAME)["svg"]


if __name__ == "__main__":
    build_diagram(Path(sys.argv[1]) if len(sys.argv) > 1 else Path("output/calculus_math"))
