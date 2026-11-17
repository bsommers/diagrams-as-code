"""The Intermediate Value Theorem and the Mean Value Theorem.

Left: a continuous curve must reach every level k between f(a) and f(b); the
crossing c is found by bisection. Right: somewhere between a and b the tangent
is parallel to the secant; every such c is located by scanning f' for sign
changes of f'(x) - m and refining each by bisection.
"""
from __future__ import annotations

import sys
from pathlib import Path

from diagrams_as_code import Diagram
from diagrams_as_code.output import render_all
from diagrams_as_code.plot import Plot

NAME = "07_ivt_mvt"
A, B = 0.5, 3.8
ORANGE = "#8A5A00"


def f(x: float) -> float:
    return 0.06 * x**3 - 0.1 * x**2 + 0.6 * x + 0.9


def df(x: float) -> float:
    return 0.18 * x**2 - 0.2 * x + 0.6


def bisect(h, lo: float, hi: float) -> float:
    for _ in range(60):
        mid = (lo + hi) / 2
        if h(lo) * h(mid) <= 0:
            hi = mid
        else:
            lo = mid
    return (lo + hi) / 2


def roots(h, lo: float, hi: float, n: int = 400) -> list[float]:
    xs = [lo + (hi - lo) * i / n for i in range(n + 1)]
    return [bisect(h, p, q) for p, q in zip(xs, xs[1:]) if h(p) * h(q) < 0]


def diagram() -> Diagram:
    fa, fb = f(A), f(B)
    k = (fa + fb) / 2
    c_ivt = roots(lambda x: f(x) - k, A, B)[0]
    m = (fb - fa) / (B - A)
    c_mvt = roots(lambda x: df(x) - m, A, B)
    with Diagram("Intermediate and Mean Value Theorems", theme="paper") as diag:
        def frame(ox: float) -> Plot:
            p = Plot(diag, x=(0, 4.5), y=(0, 6), origin=(ox, 330), size=(300, 260))
            p.grid(1, 1)
            p.axes(xlabel="$x$", xstep=1, ystep=1, size=10)
            p.function(f, stroke="#1F2F57", width=2.2, lo=0, hi=4.5)
            p.line((A, 0), (A, fa), dash="2,3", stroke="#7C8AA8")
            p.line((B, 0), (B, fb), dash="2,3", stroke="#7C8AA8")
            p.dot(A, fa, radius=3.5)
            p.dot(B, fb, radius=3.5)
            return p

        left = frame(70)
        left.hline(k)
        left.dot(c_ivt, k, radius=4.0)
        left.label(4.5, k, "$k$", size=13, color=ORANGE, anchor="left_center", dx=8)
        left.label(c_ivt, k, "$c$", size=13, anchor="top_left", dx=8, dy=8)
        left.label(A, fa, "$f(a)$", size=12, anchor="top_left", dx=8, dy=6)
        left.label(B, fb, "$f(b)$", size=12, anchor="bottom_right", dx=-8, dy=-6)
        diag.text("**Intermediate Value Theorem**", size=13).at(70, 52, anchor="left_center")
        diag.text(f"$f(a) = {fa:.2f}$,  $f(b) = {fb:.2f}$,  $k = {k:.2f}$", size=12).at(70, 410, anchor="left_center")
        diag.text(f"$f(c) = k$ at $c = {c_ivt:.3f}$", size=12).at(70, 434, anchor="left_center")

        right = frame(470)
        right.line((0, fa - m * A), (4.5, fa + m * (4.5 - A)), stroke="#7C8AA8", width=1.3)
        for c in c_mvt:
            right.tangent(f, c, half=1.6, width=1.8)
            right.dot(c, f(c), radius=4.0)
            right.line((c, 0), (c, f(c)), dash="2,3", stroke=ORANGE)
            right.label(c, 0, "$c$", size=13, color=ORANGE, anchor="top_center", dy=22)
        diag.text("**Mean Value Theorem**", size=13).at(470, 52, anchor="left_center")
        diag.text(f"secant slope $(f(b) - f(a)) / (b - a) = {m:.3f}$", size=12).at(470, 410, anchor="left_center")
        found = ",  ".join(f"$c = {c:.3f}$" for c in c_mvt)
        diag.text(f"$f'(c) = {m:.3f}$ at {found}", size=12).at(470, 434, anchor="left_center")
        diag.caption(
            "**Figure 7:** A continuous curve takes every value between its endpoint heights, and "
            "somewhere inside the interval the tangent runs parallel to the secant",
            small_caps=True,
        )
    return diag


def build_diagram(output_dir: Path | str = "output/calculus_math") -> Path:
    return render_all(diagram(), output_dir, NAME)["svg"]


if __name__ == "__main__":
    build_diagram(Path(sys.argv[1]) if len(sys.argv) > 1 else Path("output/calculus_math"))
