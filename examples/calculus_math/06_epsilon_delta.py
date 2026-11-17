"""The epsilon-delta definition of a limit for f(x) = x^2 at a = 1.

Given epsilon, the largest delta that keeps f(x) inside (L - epsilon, L + epsilon)
is found by inverting f on each side of a; the smaller of the two distances is
the delta that works. The band edges and the delta are all computed.
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

from diagrams_as_code import Diagram, Style
from diagrams_as_code.output import render_all
from diagrams_as_code.plot import Plot

NAME = "06_epsilon_delta"
A, EPS = 1.0, 0.6
ORANGE, BLUE = "#8A5A00", "#2F5799"


def f(x: float) -> float:
    return x * x


def diagram() -> Diagram:
    limit = f(A)
    left = A - math.sqrt(limit - EPS)   # distance to the left end of the x-interval
    right = math.sqrt(limit + EPS) - A  # distance to the right end
    delta = min(left, right)
    with Diagram("Epsilon-delta limit", theme="paper") as diag:
        p = Plot(diag, x=(0, 2), y=(0, 3), origin=(80, 340), size=(400, 280))
        p.axes(xlabel="$x$", ylabel="$y$", labels=False)
        # The epsilon band (horizontal) and the delta band (vertical).
        p.area(lambda x: limit + EPS, 0, 2, g=lambda x: limit - EPS, fill="#F3E3C3")
        corners = [p.px(A - delta, 0), p.px(A + delta, 0), p.px(A + delta, 3), p.px(A - delta, 3)]
        diag.polygon(corners, style=Style(fill="#CFE0F5", stroke="none", opacity=0.7), z=-2)
        p.function(f, stroke="#1F2F57", width=2.2, hi=1.7)
        for y in (limit - EPS, limit, limit + EPS):
            p.line((0, y), (A + delta if y != limit else A, y), stroke=ORANGE, dash="5,4", width=1.0)
        for x in (A - delta, A, A + delta):
            p.line((x, 0), (x, f(x)), stroke=BLUE, dash="5,4", width=1.0)
        # The part of the curve inside the box, drawn heavier.
        p.function(f, lo=A - delta, hi=A + delta, stroke="#C0392B", width=3.0, n=100)
        p.dot(A, limit, radius=4.0)

        for y, text in ((limit + EPS, r"$L + \varepsilon$"), (limit, "$L$"), (limit - EPS, r"$L - \varepsilon$")):
            p.label(0, y, text, size=13, color=ORANGE, anchor="right_center", dx=-8)
        for x, text in ((A - delta, r"$a - \delta$"), (A, "$a$"), (A + delta, r"$a + \delta$")):
            p.label(x, 0, text, size=13, color=BLUE, anchor="top_center", dy=8)
        p.label(1.7, f(1.7), "$y = f(x)$", size=13, anchor="left_center", dx=10, dy=-4)

        diag.text("**Computed**", size=13).at(560, 130, anchor="left_center")
        diag.text("$f(x) = x^2$,  $a = 1$,  $L = 1$", size=13).at(560, 160, anchor="left_center")
        diag.text(f"$\\varepsilon = {EPS:g}$", size=13, color=ORANGE).at(560, 196, anchor="left_center")
        diag.text(f"left reach $= {left:.4f}$", size=13, color=BLUE).at(560, 226, anchor="left_center")
        diag.text(f"right reach $= {right:.4f}$", size=13, color=BLUE).at(560, 252, anchor="left_center")
        diag.text(f"$\\delta = \\min = {delta:.4f}$", size=14, color=BLUE).at(560, 290, anchor="left_center")
        diag.text(r"$0 < |x - a| < \delta \Rightarrow |f(x) - L| < \varepsilon$", size=12).at(
            560, 330, anchor="left_center")
        diag.caption(
            "**Figure 6:** For the chosen tolerance on the output, a window around the input exists "
            "whose whole curve stays inside the band",
            small_caps=True,
        )
    return diag


def build_diagram(output_dir: Path | str = "output/calculus_math") -> Path:
    return render_all(diagram(), output_dir, NAME)["svg"]


if __name__ == "__main__":
    build_diagram(Path(sys.argv[1]) if len(sys.argv) > 1 else Path("output/calculus_math"))
