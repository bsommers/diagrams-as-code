"""Upper and lower sums squeezing the integral of x^2 on [0, 2].

For an increasing function the lower sum uses left heights and the upper sum
right heights. Doubling the number of strips shows both closing in on the exact
value 8/3, which is computed from the antiderivative x^3 / 3.
"""
from __future__ import annotations

import sys
from pathlib import Path

from diagrams_as_code import Diagram
from diagrams_as_code.output import render_all
from diagrams_as_code.plot import Plot

NAME = "03_upper_lower_sums"
A, B = 0.0, 2.0
COUNTS = [4, 8, 16]
SIZE = (200.0, 170.0)


def f(x: float) -> float:
    return x * x


def antiderivative(x: float) -> float:
    return x**3 / 3


def diagram() -> Diagram:
    exact = antiderivative(B) - antiderivative(A)
    with Diagram("Upper and lower sums", theme="paper") as diag:
        for i, n in enumerate(COUNTS):
            ox = 70 + i * 280
            p = Plot(diag, x=(0, 2.4), y=(0, 4.4), origin=(ox, 340), size=SIZE)
            p.grid(1, 1)
            p.axes(xstep=1, ystep=1, size=10)
            upper = p.bars(A, B, f, n, "upper", fill="#F1D9A8", stroke="#8A5A00", width=0.7)
            lower = p.bars(A, B, f, n, "lower", fill="#A9C2E4", stroke="#1F2F57", width=0.7)
            p.function(f, stroke="#1F2F57", width=2.0, lo=A, hi=B)
            top = 340 - SIZE[1] - 30
            diag.text(f"**$n = {n}$ strips**", size=13).at(ox, top, anchor="left_center")
            diag.text(f"$L_n = {lower:.4f}$", size=12, color="#1F2F57").at(ox, 392, anchor="left_center")
            diag.text(f"$U_n = {upper:.4f}$", size=12, color="#8A5A00").at(ox, 416, anchor="left_center")
            diag.text(f"$U_n - L_n = {upper - lower:.4f}$", size=12).at(ox, 440, anchor="left_center")
        diag.text(r"$L_n \leq \int_0^2 x^2\,dx \leq U_n$,   exact value $= " f"{exact:.4f}$ (8 / 3)", size=14).at(
            70, 490, anchor="left_center")
        diag.caption(
            "**Figure 3:** Lower sums (blue) and upper sums (orange) squeeze the integral as the strips "
            "get thinner; the gap shrinks in proportion to the strip width",
            small_caps=True,
        )
    return diag


def build_diagram(output_dir: Path | str = "examples/calculus_math") -> Path:
    return render_all(diagram(), output_dir, NAME)["svg"]


if __name__ == "__main__":
    build_diagram(Path(sys.argv[1]) if len(sys.argv) > 1 else Path("examples/calculus_math"))
