"""Left, right and midpoint Riemann sums beside the exact area.

Each panel draws n rectangles for one sampling rule (Plot.bars returns the
sum). The exact area comes from Simpson's rule on many subintervals, and the
error of every sum is computed against it.
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

from diagrams_as_code import Diagram
from diagrams_as_code.output import render_all
from diagrams_as_code.plot import Plot

NAME = "02_riemann_sums"
LO, HI, N = 0.0, 3.0, 6
SIZE = (250.0, 140.0)
CELLS = [  # panel title, rule, origin
    ("Left sum", "left", (70.0, 190.0)),
    ("Right sum", "right", (400.0, 190.0)),
    ("Midpoint sum", "mid", (70.0, 410.0)),
    ("Exact area", "exact", (400.0, 410.0)),
]


def f(x: float) -> float:
    return 1.6 + math.sin(1.4 * x) * 0.9 - 0.15 * x


def simpson(g, a: float, b: float, n: int = 2000) -> float:
    h = (b - a) / n
    s = g(a) + g(b) + sum((4 if i % 2 else 2) * g(a + i * h) for i in range(1, n))
    return s * h / 3


def diagram() -> Diagram:
    exact = simpson(f, LO, HI)
    with Diagram("Riemann sums", theme="paper") as diag:
        for title, rule, origin in CELLS:
            p = Plot(diag, x=(0, 3.4), y=(0, 3), origin=origin, size=SIZE)
            p.grid(1, 1)
            p.axes(xstep=1, ystep=1, size=10)
            if rule == "exact":
                p.area(f, LO, HI, fill="#DCE6F2")
                text = f"area $= {exact:.4f}$"
            else:
                total = p.bars(LO, HI, f, N, rule)
                text = f"sum $= {total:.4f}$,  error $= {total - exact:+.4f}$".replace("-", "−")
            p.function(f, stroke="#1F2F57", width=2.0, lo=LO, hi=HI)
            diag.text(f"**{title}**", size=13).at(origin[0], origin[1] - SIZE[1] - 24, anchor="left_center")
            diag.text(text, size=12).at(origin[0], origin[1] + 32, anchor="left_center")
        diag.text(f"$n = {N}$ rectangles of width $\\Delta x = {(HI - LO) / N:g}$ on $[{LO:g}, {HI:g}]$", size=12).at(
            70, 478, anchor="left_center")
        diag.caption(
            "**Figure 2:** Left, right and midpoint rectangle sums for the same curve; "
            "the midpoint rule lands closest to the exact area",
            small_caps=True,
        )
    return diag


def build_diagram(output_dir: Path | str = "examples/calculus_math") -> Path:
    return render_all(diagram(), output_dir, NAME)["svg"]


if __name__ == "__main__":
    build_diagram(Path(sys.argv[1]) if len(sys.argv) > 1 else Path("examples/calculus_math"))
