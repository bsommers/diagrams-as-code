"""Pressure-temperature phase diagram of water on a logarithmic pressure axis.

The three phase boundaries are computed, not traced. Vaporisation uses the IAPWS
saturation-pressure (Wagner) equation from the triple point to the critical point;
sublimation uses a Clausius-Clapeyron line from the triple point with
$\\Delta H_{sub} = 51.1$ kJ/mol; melting uses the IAPWS ice Ih melting-pressure
equation, which runs up to the ice Ih / ice III / liquid point near 251 K and 210 MPa
(other ice phases lie beyond it and are not drawn). The melting line leans to
lower temperature as pressure rises, which is why ice floats on, and pressure melts,
into water.
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

from diagrams_as_code import Diagram, Style
from diagrams_as_code.output import render_all
from diagrams_as_code.plot import Plot

TT, PT = 273.16, 611.657            # triple point: K, Pa
TC, PC = 647.096, 22.064e6          # critical point: K, Pa
ATM = 101325.0
R, H_SUB = 8.314, 51100.0           # J/(mol K), J/mol
INK, BLUE, RED, GREEN = "#111111", "#1F2F57", "#9C2F2F", "#2E6B3F"
WAGNER = (-7.85951783, 1.84408259, -11.7866497, 22.6807411, -15.9618719, 1.80122502)


def p_vap(t: float) -> float:
    """Saturation pressure (Pa), IAPWS-IF97 Wagner form."""
    th = 1 - t / TC
    a1, a2, a3, a4, a5, a6 = WAGNER
    s = a1 * th + a2 * th ** 1.5 + a3 * th ** 3 + a4 * th ** 3.5 + a5 * th ** 4 + a6 * th ** 7.5
    return PC * math.exp(TC / t * s)


def p_sub(t: float) -> float:
    return PT * math.exp(-H_SUB / R * (1 / t - 1 / TT))


def p_melt(t: float) -> float:
    """Ice Ih melting pressure (Pa), IAPWS R14."""
    th = t / TT
    return PT * (1 + 1.19539337e6 * (1 - th ** 3) + 8.08183159e4 * (1 - th ** 25.75)
                 + 3.33826860e3 * (1 - th ** 103.75))


def t_boil(p: float) -> float:
    lo, hi = TT, TC
    for _ in range(60):
        mid = (lo + hi) / 2
        lo, hi = (mid, hi) if p_vap(mid) < p else (lo, mid)
    return (lo + hi) / 2


def diagram() -> Diagram:
    t_b = t_boil(ATM)
    t_ih3 = 251.165                       # ice Ih / III / liquid triple point
    with Diagram("Water phase diagram", theme="paper") as diag:
        p = Plot(diag, x=(190, 800), y=(1e-1, 1e9), origin=(90, 440), size=(560, 350), yscale="log")
        for dec in range(0, 10, 1):
            p.line((190, 10.0 ** dec), (800, 10.0 ** dec), stroke="#E3E6EE", width=0.8)
        p.axes(xlabel="temperature $T$ (K)", ylabel="pressure $P$ (Pa)", xstep=100, through_zero=False)

        # Supercritical region, shaded.
        d = diag
        corner = [p.px(TC, PC), p.px(800, PC), p.px(800, 1e9), p.px(TC, 1e9)]
        d.polygon(corner, style=Style(fill="#F3E6D3", stroke="none", opacity=0.8), z=-3)
        p.label(725, 3e8, "supercritical\nfluid", size=12, anchor="center", color="#8A5A00")
        p.vline(TC, stroke="#8A5A00", width=0.9)
        p.line((TC, PC), (800, PC), stroke="#8A5A00", width=0.9, dash="5,4")

        p.function(p_sub, 190, TT, stroke=GREEN, width=2.6, n=200)
        p.function(p_vap, TT, TC, stroke=BLUE, width=2.6, n=300)
        p.parametric(lambda th: th * TT, lambda th: p_melt(th * TT), 0.9195, 1.0, stroke=RED, width=2.6, n=200)

        p.line((190, ATM), (800, ATM), stroke="#888888", width=0.9, dash="3,3")
        p.label(795, ATM, "1 atm", size=11, anchor="bottom_right", dy=-3, color="#555555")
        p.dot(TT, PT, radius=4.5)
        p.dot(TC, PC, radius=4.5)
        p.dot(t_b, ATM, radius=4.0)
        p.dot(t_ih3, p_melt(t_ih3), radius=3.5)

        p.label(228, 5e5, "**solid**\n(ice $I_h$)", size=13, anchor="center")
        p.label(335, 3e6, "**liquid**", size=13, anchor="center")
        p.label(470, 1e1, "**gas**\n(vapour)", size=13, anchor="center")
        p.label(TT, PT, "triple point", size=12, anchor="top_left", dx=8, dy=10)
        p.label(TC, PC, "critical point", size=12, anchor="right_center", dx=-9, dy=-14)
        p.label(t_b, ATM, "normal boiling point", size=12, anchor="top_left", dx=8, dy=8)
        p.label(215, 3e0, "sublimation", size=11, anchor="bottom_left", color=GREEN, dx=40, dy=-8)
        p.label(t_ih3, p_melt(t_ih3), "melting", size=11, anchor="right_center", dx=-9, color=RED)
        p.label(520, 8e5, "vaporisation", size=11, anchor="center", color=BLUE)

        x0 = 700
        diag.text(
            "**Special points**\n"
            f"Triple point: {TT} K ({TT - 273.15:.2f} $^{{\\circ}}$C),\n{PT} Pa\n"
            f"Critical point: {TC} K ({TC - 273.15:.1f} $^{{\\circ}}$C),\n{PC / 1e6:.3f} MPa\n"
            f"Normal boiling point: {t_b:.2f} K\n({t_b - 273.15:.2f} $^{{\\circ}}$C) at 101.325 kPa",
            size=13,
        ).at(x0, 110, anchor="top_left")
        diag.text(
            "Below 611.657 Pa liquid water cannot exist:\n"
            "ice sublimes straight to vapour.\n"
            "Above the critical point there is no boiling,\n"
            "only a continuous change to a dense fluid.",
            size=13,
        ).at(x0, 290, anchor="top_left")
        diag.caption("**Figure 5:** Water phase diagram on a log pressure axis, with the triple point, critical point and normal boiling point marked",
                     small_caps=True)
    return diag


def build_diagram(output_dir: Path | str = "examples/chemistry") -> Path:
    return render_all(diagram(), output_dir, "05_water_phase_diagram")["svg"]


if __name__ == "__main__":
    build_diagram(Path(sys.argv[1]) if len(sys.argv) > 1 else Path("examples/chemistry"))
