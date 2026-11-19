"""Michaelis-Menten kinetics and its Lineweaver-Burk (double-reciprocal) transform.

v = Vmax [S] / (Km + [S]) and 1/v = (Km / Vmax)(1/[S]) + 1/Vmax. Illustrative enzyme with
Vmax = 100 umol/min and Km = 2 mM; a competitive inhibitor raises the apparent Km to
4 mM (alpha = 2) with Vmax unchanged, and a non-competitive inhibitor halves Vmax
at the same Km.
"""
import sys
from pathlib import Path

from diagrams_as_code import Diagram
from diagrams_as_code.output import render_all
from diagrams_as_code.plot import Plot

INK = "#1F2F57"
BLUE, RED, GREEN, AMBER = "#2F5FA8", "#B03A3A", "#2E6B3F", "#8A5A00"
VMAX, KM = 100.0, 2.0
ALPHA = 2.0


def mm(s, vmax=VMAX, km=KM):
    return vmax * s / (km + s)


def diagram() -> Diagram:
    with Diagram("Michaelis-Menten and Lineweaver-Burk plots", theme="paper") as diag:
        a = Plot(diag, x=(0, 20), y=(0, 110), origin=(100, 420), size=(430, 300))
        a.grid(xstep=5, ystep=25)
        a.axes(xlabel="[S] (mM)", ylabel="Rate $v$ ($\\mu$mol/min)", xstep=5, ystep=25, through_zero=False, arrows=False)
        a.hline(VMAX, stroke=AMBER)
        a.hline(VMAX / 2, stroke="#8890A8")
        a.vline(KM, stroke="#8890A8")
        a.function(lambda s: mm(s), stroke=BLUE, width=2.6)
        a.function(lambda s: mm(s, VMAX, ALPHA * KM), stroke=RED, width=2.0, dash="6,3")
        a.function(lambda s: mm(s, VMAX / 2, KM), stroke=GREEN, width=2.0, dash="6,3")
        a.dot(KM, VMAX / 2, radius=4.0)
        a.label(20, VMAX, "$V_{\\max}$", size=13, anchor="bottom_right", dy=-4, color=AMBER)
        a.label(KM, 0, "$K_m$", size=13, anchor="bottom_left", dx=5, dy=-4)
        a.label(20, VMAX / 2, "$V_{\\max}/2$", size=12, anchor="bottom_right", dy=-4)
        a.legend([("No inhibitor", BLUE, ""), ("Competitive ($K_m^{\\mathrm{app}} = 4$ mM)", RED, "6,3"),
                  ("Non-competitive ($V_{\\max}/2$)", GREEN, "6,3")], at=(250, 330), size=12)

        # Double-reciprocal plot: x = 1/[S] (per mM), y = 1/v (min/umol).
        b = Plot(diag, x=(-0.6, 2.0), y=(0, 0.06), origin=(640, 420), size=(430, 300))
        b.grid(xstep=0.5, ystep=0.02)
        b.axes(xlabel="$1/[S]$ (mM$^{-1}$)", ylabel="$1/v$ (min/$\\mu$mol)", xstep=0.5, ystep=0.02, through_zero=True, arrows=False,
               xtick_labels={0.5: "0.5", 1.0: "1.0", 1.5: "1.5", 2.0: "2.0"})
        lines = [(BLUE, "", VMAX, KM), (RED, "6,3", VMAX, ALPHA * KM), (GREEN, "6,3", VMAX / 2, KM)]
        for colour, dash, vmax, km in lines:
            slope, icpt = km / vmax, 1.0 / vmax
            b.function(lambda x, m=slope, c=icpt: m * x + c, lo=-0.6, hi=2.0, stroke=colour, width=2.4 if not dash else 2.0, dash=dash)
        b.dot(-1 / KM, 0, radius=4.0)
        b.label(-1 / KM, 0, "$-1/K_m = -0.5$", size=12, anchor="top_left", dx=-16, dy=24)
        b.dot(0, 1 / VMAX, radius=4.0)
        b.label(0, 1 / VMAX, "$1/V_{\\max} = 0.01$", size=12, anchor="left_center", dx=10, dy=10)
        b.label(0.95, 0.0125 * 0.95 + 0.01, "slope $K_m/V_{\\max}$", size=12, anchor="top_left", dx=8, dy=20, color=BLUE)
        diag.text(
            "$v = V_{\\max}[S] / (K_m + [S])$\n"
            "$1/v = (K_m/V_{\\max})(1/[S]) + 1/V_{\\max}$\n"
            "Competitive inhibitor: same $y$-intercept,\n"
            "steeper line. Non-competitive: higher\n"
            "$y$-intercept, same $x$-intercept.",
            size=12,
        ).at(100, 470, anchor="top_left")
        diag.caption(
            "**Figure 10:** Michaelis-Menten saturation curve (left) and its Lineweaver-Burk transform (right). The double-reciprocal\n"
            "plot linearises the data: the $y$-intercept gives $1/V_{\\max}$ and the $x$-intercept gives $-1/K_m$",
            small_caps=True,
        )
    return diag


def build_diagram(output_dir: Path | str = "examples/medical") -> Path:
    return render_all(diagram(), output_dir, "10_michaelis_menten")["svg"]


if __name__ == "__main__":
    build_diagram(Path(sys.argv[1]) if len(sys.argv) > 1 else Path("examples/medical"))
