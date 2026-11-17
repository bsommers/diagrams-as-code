"""The area between a parabola and a line.

The crossing points are found by bisection on f - g, the area by Simpson's
rule on f - g between them, and one vertical strip of height f(x) - g(x) shows
what the integral adds up.
"""
from __future__ import annotations

import sys
from pathlib import Path

from diagrams_as_code import Diagram
from diagrams_as_code.output import render_all
from diagrams_as_code.plot import Plot

NAME = "04_area_between_curves"
STRIP = -1.5


def f(x: float) -> float:
    return 4 - x * x


def g(x: float) -> float:
    return x + 2


def bisect(h, lo: float, hi: float) -> float:
    for _ in range(60):
        mid = (lo + hi) / 2
        if h(lo) * h(mid) <= 0:
            hi = mid
        else:
            lo = mid
    return (lo + hi) / 2


def simpson(h, a: float, b: float, n: int = 2000) -> float:
    step = (b - a) / n
    s = h(a) + h(b) + sum((4 if i % 2 else 2) * h(a + i * step) for i in range(1, n))
    return s * step / 3


def diagram() -> Diagram:
    d = lambda x: f(x) - g(x)
    x1, x2 = bisect(d, -3, -1), bisect(d, 0, 2)
    area = simpson(d, x1, x2)
    with Diagram("Area between two curves", theme="paper") as diag:
        p = Plot(diag, x=(-3, 3), y=(-1, 5), origin=(70, 340), size=(420, 280))
        p.grid(1, 1)
        p.axes(xlabel="$x$", ylabel="$y$", xstep=1, ystep=1)
        p.area(f, x1, x2, g=g, fill="#CFE0F5")
        p.function(f, stroke="#1F2F57", width=2.2)
        p.function(g, stroke="#8A5A00", width=2.2)
        p.line((STRIP, g(STRIP)), (STRIP, f(STRIP)), stroke="#C0392B", width=1.8)
        for x in (x1, x2):
            p.dot(x, g(x), radius=3.5)
            p.line((x, 0), (x, g(x)), stroke="#8A5A00", dash="5,4", width=1.0)
        p.label(x1, g(x1), f"$({x1:g}, {g(x1):g})$", size=12, anchor="right_center", dx=-8, dy=-12)
        p.label(x2, f(x2), f"$({x2:g}, {f(x2):g})$", size=12, anchor="top_left", dx=16, dy=8)
        p.label(-1.15, f(-1.15), "$y = f(x)$", size=13, anchor="bottom_right", dx=-10, dy=-10)
        p.label(2.3, g(2.3), "$y = g(x)$", size=13, color="#8A5A00", anchor="top_left", dx=2, dy=14)


        diag.text("**Computed**", size=13).at(560, 130, anchor="left_center")
        diag.text("$f(x) = 4 - x^2$", size=13).at(560, 160, anchor="left_center")
        diag.text("$g(x) = x + 2$", size=13, color="#8A5A00").at(560, 186, anchor="left_center")
        diag.text(f"crossings at $x = {x1:g}$ and $x = {x2:g}$", size=13).at(560, 222, anchor="left_center")
        diag.text(f"red strip at $x = {STRIP:g}$: $f - g = {d(STRIP):g}$", size=12, color="#C0392B").at(
            560, 244, anchor="left_center")
        diag.text(r"$A = \int_{a}^{b} (f(x) - g(x))\,dx$", size=13).at(560, 284, anchor="left_center")
        diag.text(f"$A = {area:.4f}$", size=15).at(560, 318, anchor="left_center")
        diag.caption(
            "**Figure 4:** The area between two curves is the integral of the upper minus the lower, "
            "taken between their crossing points",
            small_caps=True,
        )
    return diag


def build_diagram(output_dir: Path | str = "output/calculus_math") -> Path:
    return render_all(diagram(), output_dir, NAME)["svg"]


if __name__ == "__main__":
    build_diagram(Path(sys.argv[1]) if len(sys.argv) > 1 else Path("output/calculus_math"))
