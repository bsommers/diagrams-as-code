"""Dose-response curves from the Hill equation: E = Emax C^n / (EC50^n + C^n).

Three drugs share Emax but differ in potency (EC50) and a fourth in steepness (Hill
coefficient n). Response is a percentage of the maximum effect; concentration is
on a log axis so each curve is the familiar symmetric sigmoid about its EC50.
"""
import sys
from pathlib import Path

from diagrams_as_code import Diagram
from diagrams_as_code.output import render_all
from diagrams_as_code.plot import Plot

INK = "#1F2F57"
AMBER = "#8A5A00"
CURVES = [  # name, EC50 (nM), Hill n, colour
    ("A: $\\mathrm{EC}_{50} = 10$ nM, $n = 1$", 10.0, 1.0, "#B03A3A"),
    ("B: $\\mathrm{EC}_{50} = 100$ nM, $n = 1$", 100.0, 1.0, "#2F5FA8"),
    ("C: $\\mathrm{EC}_{50} = 100$ nM, $n = 2$", 100.0, 2.0, "#2E6B3F"),
]


def hill(c, ec50, n):
    return 100.0 * c ** n / (ec50 ** n + c ** n)


def diagram() -> Diagram:
    with Diagram("Dose-response curves (Hill equation)", theme="paper") as diag:
        pl = Plot(diag, x=(0.1, 10000), y=(-6, 104), origin=(110, 420), size=(560, 330), xscale="log")
        pl.grid(ystep=25)
        for dec in (1, 10, 100, 1000):
            pl.vline(dec, stroke="#E3E6EE", dash="", width=0.8)
        pl.axes(xlabel="[Drug] (nM)", ylabel="Effect (% of $E_{\\max}$)", ystep=25, through_zero=False, arrows=False)
        pl.hline(50, stroke=AMBER)
        for _, ec50, n, colour in CURVES:
            pl.function(lambda c, e=ec50, k=n: hill(c, e, k), lo=0.1, hi=10000, stroke=colour, width=2.4)
        for ec50 in (10.0, 100.0):
            pl.vline(ec50, stroke=AMBER)
            pl.dot(ec50, 50, radius=4.0)
        pl.label(10, 0, "$\\mathrm{EC}_{50}$", size=12, anchor="bottom_right", dx=-5, dy=-4, color=AMBER)
        pl.label(100, 0, "$\\mathrm{EC}_{50}$", size=12, anchor="bottom_left", dx=5, dy=-4, color=AMBER)
        pl.label(0.1, 50, "50 %", size=12, anchor="bottom_left", dx=6, dy=-4, color=AMBER)
        pl.legend([(name, colour, "") for name, _, _, colour in CURVES], at=(130, 125), size=12)
        diag.text(
            "$E = E_{\\max}\\, C^{n} / (\\mathrm{EC}_{50}^{\\,n} + C^{n})$\n"
            "Curve A is ten times more potent than B\n"
            "(same $E_{\\max}$, $\\mathrm{EC}_{50}$ lower).\n"
            "Going from 10 % to 90 % effect needs a\n"
            "concentration ratio of 81 for $n = 1$ and 9 for $n = 2$.",
            size=12,
        ).at(700, 140, anchor="top_left")
        diag.caption(
            "**Figure 5:** Dose-response (Hill) curves on a log concentration axis. $\\mathrm{EC}_{50}$ sets potency (left-right position);\n"
            "the Hill coefficient $n$ sets steepness",
            small_caps=True,
        )
    return diag


def build_diagram(output_dir: Path | str = "examples/medical") -> Path:
    return render_all(diagram(), output_dir, "05_dose_response")["svg"]


if __name__ == "__main__":
    build_diagram(Path(sys.argv[1]) if len(sys.argv) > 1 else Path("examples/medical"))
