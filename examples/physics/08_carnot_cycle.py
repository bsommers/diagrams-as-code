"""The Carnot cycle of an ideal gas on a pressure-volume diagram.

Two isotherms (at $T_h$ and $T_c$) are joined by two adiabats. The isotherms are
$P = nRT/V$ and the adiabats $P V^\\gamma = \\mathrm{const}$; the corner volumes
$V_C$ and $V_D$ are solved from $T V^{\\gamma - 1} = \\mathrm{const}$, and the heat
exchanged, the work and the efficiency are computed from the same numbers.
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

from diagrams_as_code import Diagram, Style
from diagrams_as_code.output import render_all
from diagrams_as_code.plot import Plot

N_MOL, R_GAS, GAMMA = 0.1, 8.314, 5 / 3   # a monatomic ideal gas
TH, TC = 600.0, 300.0
VA, VB = 2.0, 5.0                    # litres
RED, BLUE, INK = "#9C2F2F", "#1F2F57", "#111111"


def pressure(T: float, V: float) -> float:
    """kPa for N_MOL moles at T kelvin in V litres (n R T / V, with R in J/(mol K))."""
    return N_MOL * R_GAS * T / V


def diagram() -> Diagram:
    k = (TH / TC) ** (1 / (GAMMA - 1))
    VC, VD = VB * k, VA * k
    pts = {"A": (VA, pressure(TH, VA)), "B": (VB, pressure(TH, VB)),
           "C": (VC, pressure(TC, VC)), "D": (VD, pressure(TC, VD))}
    qh = N_MOL * R_GAS * TH * math.log(VB / VA)
    qc = N_MOL * R_GAS * TC * math.log(VC / VD)
    work = qh - qc
    eff = work / qh

    def iso(T):
        return lambda V: pressure(T, V)

    def adiabat(point):
        v0, p0 = point
        return lambda V: p0 * (v0 / V) ** GAMMA

    with Diagram("Carnot cycle", theme="paper") as diag:
        p = Plot(diag, x=(0, 16), y=(0, 260), origin=(90, 440), size=(560, 380))
        p.grid(xstep=2, ystep=40)
        p.axes(xlabel="$V$ (L)", ylabel="$P$ (kPa)", xstep=2, ystep=40, through_zero=False)

        # Shade the enclosed region from the four sampled branches.
        def branch(f, a, b, n=60):
            return [p.px(a + (b - a) * i / n, f(a + (b - a) * i / n)) for i in range(n + 1)]
        loop = (branch(iso(TH), VA, VB) + branch(adiabat(pts["B"]), VB, VC)
                + branch(iso(TC), VC, VD) + branch(adiabat(pts["D"]), VD, VA))
        diag.polygon(loop, style=Style(fill="#DCE6F2", fill_opacity=0.75, stroke="none"), z=-2)

        # Faint extensions of the isotherms, then the four branches of the cycle.
        p.function(iso(TH), 1.0, 16, stroke="#C9A9A9", width=0.9, dash="4,3")
        p.function(iso(TC), 1.0, 16, stroke="#A9B4C9", width=0.9, dash="4,3")
        p.function(iso(TH), VA, VB, stroke=RED, width=2.4)
        p.function(iso(TC), VC, VD, stroke=BLUE, width=2.4)
        p.function(adiabat(pts["B"]), VB, VC, stroke=INK, width=2.4)
        p.function(adiabat(pts["D"]), VD, VA, stroke=INK, width=2.4)

        def arrow_on(f, a, b, color):
            xm = (a + b) / 2
            h = 0.05 * (b - a)
            u, v = p.px(xm - h, f(xm - h)), p.px(xm + h, f(xm + h))
            diag.connect(u, v, routing="direct", width=2.4, color=color, head="stealth")

        arrow_on(iso(TH), VA, VB, RED)
        arrow_on(adiabat(pts["B"]), VB, VC, INK)
        # The cooling isotherm is traversed from C to D, so run the arrow that way.
        xm = (VC + VD) / 2
        h = 0.05 * (VC - VD)
        diag.connect(p.px(xm + h, iso(TC)(xm + h)), p.px(xm - h, iso(TC)(xm - h)), routing="direct", width=2.4,
                     color=BLUE, head="stealth")
        xm = (VD + VA) / 2
        diag.connect(p.px(xm + 0.03 * (VD - VA), adiabat(pts["D"])(xm + 0.03 * (VD - VA))),
                     p.px(xm - 0.03 * (VD - VA), adiabat(pts["D"])(xm - 0.03 * (VD - VA))),
                     routing="direct", width=2.4, color=INK, head="stealth")

        offsets = {"A": (-10, -6, "bottom_right"), "B": (8, -8, "bottom_left"),
                   "C": (8, -8, "bottom_left"), "D": (8, -8, "bottom_left")}
        for name, (v, pr) in pts.items():
            dx, dy, anc = offsets[name]
            p.dot(v, pr, radius=4, label=f"**{name}**", size=14, dx=dx, dy=dy, anchor=anc)

        p.label(9.0, pressure(TH, 9.0), f"isotherm $T_h = {TH:g}$ K", dy=-10, anchor="bottom_left", color=RED, size=13)
        p.label(11.0, pressure(TC, 11.0), f"isotherm $T_c = {TC:g}$ K", dy=-16, anchor="bottom_left", color=BLUE, size=13)
        xm = (VD + VA) / 2
        p.label(xm, adiabat(pts["D"])(xm), "adiabat", dx=-14, anchor="right_center", size=12)
        xq = (VA + VB) / 2
        p.label(xq, iso(TH)(xq), f"$Q_h = {qh:.0f}$ J in", dx=14, dy=-6, anchor="bottom_left", size=13, color=RED)
        xc = (VD + VC) / 2
        p.label(xc, iso(TC)(xc), f"$Q_c = {qc:.0f}$ J out", dy=12, anchor="top_center", size=13, color=BLUE)
        p.label(3.6, 117, "$W$", anchor="center", size=16)

        x0 = 90 + 560 + 50
        diag.text(
            "**State points**\n"
            + "\n".join(f"{n}:  $V = {v:.1f}$ L,  $P = {pr:.1f}$ kPa" for n, (v, pr) in pts.items()),
            size=13,
        ).at(x0, 80, anchor="top_left")
        diag.text(
            "**Four steps**\n"
            "A to B: isothermal expansion, heat $Q_h$ taken in\n"
            "B to C: adiabatic expansion, gas cools to $T_c$\n"
            "C to D: isothermal compression, heat $Q_c$ given out\n"
            "D to A: adiabatic compression, gas warms to $T_h$",
            size=13,
        ).at(x0, 190, anchor="top_left")
        diag.text(
            f"$V_C = V_B (T_h / T_c)^{{1/(\\gamma - 1)}} = {VC:.1f}$ L,  $V_D = {VD:.1f}$ L\n"
            f"$W = Q_h - Q_c = {work:.0f}$ J\n$\\eta = W / Q_h = 1 - T_c / T_h = {100 * eff:.0f}$ percent",
            size=13,
        ).at(x0, 330, anchor="top_left")
        diag.caption("**Figure 8:** The Carnot cycle of an ideal gas: two isotherms and two adiabats enclose the work done per cycle",
                     small_caps=True)
    return diag


def build_diagram(output_dir: Path | str = "examples/physics") -> Path:
    return render_all(diagram(), output_dir, "08_carnot_cycle")["svg"]


if __name__ == "__main__":
    dest = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("examples/physics")
    build_diagram(dest)
