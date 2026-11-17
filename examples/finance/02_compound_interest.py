"""Growth of 1,000 at several annual rates."""
from __future__ import annotations

import math
import sys
from pathlib import Path

from diagrams_as_code import Diagram, Style
from diagrams_as_code.output import render_all
from diagrams_as_code.plot import Plot

INK = "#1F2F57"
AMBER = "#8A5A00"

PRINCIPAL = 1000.0
YEARS = 30
RATES = [(0.02, "#7C8AA8"), (0.04, "#4F6D9A"), (0.06, "#2E8B57"), (0.08, AMBER), (0.10, "#C0392B")]


def value(rate: float, t: float) -> float:
    return PRINCIPAL * (1 + rate) ** t


def diagram() -> Diagram:
    with Diagram("Compound interest growth", theme="paper") as diag:
        p = Plot(diag, x=(0, YEARS), y=(0, 18000), origin=(100, 360), size=(560, 300))
        p.grid(xstep=6, ystep=3000)
        p.axes(xlabel="Years $t$", ylabel="Value", xstep=6, ystep=3000, through_zero=False)
        for rate, colour in RATES:
            p.function(lambda t, r=rate: value(r, t), 0, YEARS, stroke=colour, width=2.0)
            p.label(YEARS, value(rate, YEARS), f"{rate:.0%}", size=12, dx=8, color=colour)
        diag.text(
            "$A(t) = P(1 + r)^t$ with $P = 1{,}000$", size=13
        ).at(*p.px(1, 17500), anchor="top_left")
        diag.caption(
            "**Figure 2:** Compound interest. A principal of 1,000 grows as $P(1+r)^t$ at annual rates of 2% to 10%.\n"
            "After 30 years 1,000 has become 1,811 at 2% and 17,449 at 10%.",
            small_caps=True,
        )
    return diag


def build_diagram(output_dir: Path | str = "output/finance") -> Path:
    return render_all(diagram(), output_dir, "02_compound_interest")["svg"]


if __name__ == "__main__":
    build_diagram(Path(sys.argv[1]) if len(sys.argv) > 1 else Path("output/finance"))
