"""Oxygen-haemoglobin dissociation curves from the Hill equation.

S = P^n / (P50^n + P^n) with Hill coefficient n = 2.7 and, for adult haemoglobin at pH 7.4
and 37 C, P50 = 26.8 mmHg. Right shift (raised CO2, H+, temperature, 2,3-BPG) is drawn
with P50 = 35 mmHg and left shift (fetal Hb, low temperature, alkalosis) with P50 = 20 mmHg.
"""
import sys
from pathlib import Path

from diagrams_as_code import Diagram
from diagrams_as_code.output import render_all
from diagrams_as_code.plot import Plot

INK = "#1F2F57"
BLUE, RED, GREEN, AMBER = "#2F5FA8", "#B03A3A", "#2E6B3F", "#8A5A00"
N_HILL = 2.7
P50 = 26.8
P_ART, P_VEN = 100.0, 40.0


def sat(p: float, p50: float = P50, n: float = N_HILL) -> float:
    """Haemoglobin saturation in percent at oxygen partial pressure p (mmHg)."""
    return 100.0 * p ** n / (p50 ** n + p ** n)


def diagram() -> Diagram:
    s_art, s_ven = sat(P_ART), sat(P_VEN)
    with Diagram("Oxygen-haemoglobin dissociation curve", theme="paper") as diag:
        pl = Plot(diag, x=(0, 110), y=(0, 100), origin=(110, 430), size=(560, 340))
        pl.grid(xstep=20, ystep=25)
        pl.axes(xlabel="$P_{\\mathrm{O}_2}$ (mmHg)", ylabel="Hb saturation (%)", xstep=20, ystep=25, through_zero=False, arrows=False)
        pl.function(lambda p: sat(p), lo=0, hi=110, stroke=BLUE, width=2.6)
        pl.function(lambda p: sat(p, 35.0), lo=0, hi=110, stroke=RED, width=2.0, dash="6,3")
        pl.function(lambda p: sat(p, 20.0), lo=0, hi=110, stroke=GREEN, width=2.0, dash="6,3")
        pl.hline(50, stroke="#8890A8")
        pl.dot(P50, 50, radius=4.0)
        pl.vline(P50, stroke="#8890A8")
        pl.label(0, 50, "$P_{50}$", size=12, anchor="bottom_left", dx=8, dy=-4)
        # Arterial and mixed-venous points.
        for p, s, name, dy in ((P_ART, s_art, "Arterial", 18), (P_VEN, s_ven, "Mixed venous", -4)):
            pl.vline(p, stroke=AMBER)
            pl.dot(p, s, radius=4.2)
        pl.label(P_ART, s_art, f"arterial, {P_ART:g} mmHg: {s_art:.0f} %", size=12, anchor="top_right", dx=-8, dy=-30)
        pl.label(P_VEN, s_ven, f"venous, {P_VEN:g} mmHg: {s_ven:.0f} %", size=12, anchor="left_center", dx=14, dy=34)
        # Unloaded oxygen between the two points.
        pl.line((P_VEN, 12), (P_ART, 12), stroke=AMBER, width=1.4)
        pl.label((P_VEN + P_ART) / 2, 12, f"unloaded to tissue: {s_art - s_ven:.0f} % of Hb", size=12, anchor="bottom_center", dy=-6, color=AMBER)
        pl.legend([("Normal ($P_{50} = 26.8$ mmHg)", BLUE, ""), ("Right shift ($P_{50} = 35$): $\\uparrow$ CO$_2$, $\\uparrow$ H$^+$, $\\uparrow$ temp, $\\uparrow$ 2,3-BPG", RED, "6,3"),
                   ("Left shift ($P_{50} = 20$): fetal Hb, $\\downarrow$ temp, alkalosis", GREEN, "6,3")], at=(690, 120), size=12)
        diag.text(
            f"$S = P^{{n}} / (P_{{50}}^{{\\,n}} + P^{{n}})$, $n = {N_HILL}$\n"
            "A right shift lowers Hb affinity,\n"
            "so more $\\mathrm{O}_2$ is released at the same $P_{\\mathrm{O}_2}$.",
            size=12,
        ).at(690, 230, anchor="top_left")
        diag.caption(
            "**Figure 9:** Oxygen-haemoglobin dissociation curve. The sigmoid shape reflects cooperative binding of four $\\mathrm{O}_2$ molecules;\n"
            "the steep part lies between venous and tissue $P_{\\mathrm{O}_2}$, so small pressure falls release much oxygen",
            small_caps=True,
        )
    return diag


def build_diagram(output_dir: Path | str = "examples/medical") -> Path:
    return render_all(diagram(), output_dir, "09_oxygen_dissociation")["svg"]


if __name__ == "__main__":
    build_diagram(Path(sys.argv[1]) if len(sys.argv) > 1 else Path("examples/medical"))
