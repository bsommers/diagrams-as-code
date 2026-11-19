"""Normal, flat and inverted yield curves from a three-factor (Nelson-Siegel) shape."""
from __future__ import annotations

import math
import sys
from pathlib import Path

from diagrams_as_code import Diagram
from diagrams_as_code.output import render_all
from diagrams_as_code.plot import Plot

MATURITIES = [0.25, 1, 2, 3, 5, 7, 10, 20, 30]
TAU = 3.0
# (name, level, slope, curvature, colour): y(t) = b0 + b1 * L(t) + b2 * (L(t) - e^{-t/tau}), L = (1 - e^{-t/tau}) / (t/tau)
CURVES = [
    ("Normal", 5.6, -3.2, 1.5, "#2E8B57"),
    ("Flat", 4.1, 0.0, 0.0, "#4F6D9A"),
    ("Inverted", 3.0, 2.6, -1.0, "#C0392B"),
]


def curve_yield(b0: float, b1: float, b2: float, t: float) -> float:
    load = (1 - math.exp(-t / TAU)) / (t / TAU)
    return b0 + b1 * load + b2 * (load - math.exp(-t / TAU))


def diagram() -> Diagram:
    with Diagram("Yield curves", theme="paper") as diag:
        p = Plot(diag, x=(0, 30), y=(2, 6.5), origin=(100, 340), size=(540, 280))
        p.grid(xstep=5, ystep=1)
        p.axes(xlabel="Maturity (years)", ylabel="Yield (%)", xstep=5, ystep=1, through_zero=False)
        for name, b0, b1, b2, colour in CURVES:
            f = lambda t, a=(b0, b1, b2): curve_yield(*a, t)
            p.function(f, 0.05, 30, stroke=colour, width=2.2)
            for m in MATURITIES:
                p.dot(m, f(m), radius=2.6)
            p.label(30, f(30), name, size=13, dx=8, color=colour)
        diag.caption(
            "**Figure 4:** Three shapes of the yield curve (illustrative Nelson-Siegel curves, not market data).\n"
            "Normal: long rates above short rates. Flat: no term premium. Inverted: short rates above long rates.",
            small_caps=True,
        )
    return diag


def build_diagram(output_dir: Path | str = "examples/finance") -> Path:
    return render_all(diagram(), output_dir, "04_yield_curve")["svg"]


if __name__ == "__main__":
    build_diagram(Path(sys.argv[1]) if len(sys.argv) > 1 else Path("examples/finance"))
