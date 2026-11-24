"""An NMOS common-source amplifier with a divider bias network and a bypassed source resistor.

The schematic is built from path symbols. The bias point is solved from the
square-law model (the quadratic for I_D is solved in closed form), and the
small-signal gain, input and output resistance follow from it. The output
characteristics carry the DC load line and the quiescent point.
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

from diagrams_as_code import Diagram, Style
from diagrams_as_code.output import render_all
from diagrams_as_code.plot import Plot

INK = "#111111"
WIRE = Style(fill="none", stroke=INK, stroke_width=2.0)
WHITE = Style(fill="#FFFFFF", stroke=INK, stroke_width=2.0)


def seg(*pts) -> str:
    return "M " + " L ".join(f"{x:.2f} {y:.2f}" for x, y in pts)


def frame(a, b):
    """Length of a->b and a map from local (along, across) to canvas points."""
    (x0, y0), (x1, y1) = a, b
    n = math.hypot(x1 - x0, y1 - y0)
    ux, uy = (x1 - x0) / n, (y1 - y0) / n
    return n, lambda u, v: (x0 + u * ux - v * uy, y0 + u * uy + v * ux)


def resistor(a, b, peaks: int = 6, amp: float = 9.0, lead: float = 14.0) -> str:
    n, T = frame(a, b)
    step = (n - 2 * lead) / peaks
    pts = [T(0, 0), T(lead, 0)]
    pts += [T(lead + step * (k + 0.5), amp if k % 2 else -amp) for k in range(peaks)]
    return seg(*pts, T(n - lead, 0), T(n, 0))


def capacitor(a, b, gap: float = 12.0, plate: float = 34.0) -> str:
    n, T = frame(a, b)
    m = n / 2
    return " ".join([seg(T(0, 0), T(m - gap / 2, 0)), seg(T(m - gap / 2, -plate / 2), T(m - gap / 2, plate / 2)),
                     seg(T(m + gap / 2, -plate / 2), T(m + gap / 2, plate / 2)), seg(T(m + gap / 2, 0), T(n, 0))])


def ground(x: float, y: float) -> str:
    return " ".join([seg((x, y), (x, y + 10)), seg((x - 14, y + 10), (x + 14, y + 10)),
                     seg((x - 9, y + 16), (x + 9, y + 16)), seg((x - 4, y + 22), (x + 4, y + 22))])


def circle(cx: float, cy: float, r: float) -> str:
    return f"M {cx - r} {cy} A {r} {r} 0 1 0 {cx + r} {cy} A {r} {r} 0 1 0 {cx - r} {cy} Z"



VDD, VT, K = 12.0, 2.0, 2e-3      # volt, volt, A/V^2 (K = mu*Cox*W/L)
R1, R2, RD, RS, RL = 470e3, 220e3, 5.6e3, 1e3, 10e3
BLUE, RED, GREY = "#1F2F57", "#9C2F2F", "#8A8F9C"


def bias():
    """Solve I_D = (K/2)(V_G - I_D R_S - V_T)^2 for the saturation branch."""
    vg = VDD * R2 / (R1 + R2)
    # (K/2)(x - I R_S)^2 = I with x = V_G - V_T  ->  (K/2) R_S^2 I^2 - (1 + K x R_S) I + (K/2) x^2 = 0
    x = vg - VT
    qa, qb, qc = (K / 2) * RS ** 2, -(1 + K * x * RS), (K / 2) * x ** 2
    i_d = (-qb - math.sqrt(qb ** 2 - 4 * qa * qc)) / (2 * qa)
    return vg, i_d


def drain_current(vgs: float, vds: float) -> float:
    vov = vgs - VT
    if vov <= 0:
        return 0.0
    return K * (vov * vds - vds ** 2 / 2) if vds < vov else K / 2 * vov ** 2


def diagram() -> Diagram:
    vg, i_d = bias()
    vgs = vg - i_d * RS
    vov = vgs - VT
    gm = K * vov
    vd, vs = VDD - i_d * RD, i_d * RS
    r_par = RD * RL / (RD + RL)
    av = -gm * r_par
    r_in = R1 * R2 / (R1 + R2)
    gy, rail = 220.0, 60.0                       # gate level and supply rail
    mx, dx_ = 300.0, 340.0                       # gate-plate x and drain/source column x
    with Diagram("NMOS common-source amplifier", theme="paper") as diag:
        def text(s, x, yy, anchor="center", size=14, **kw):
            diag.text(s, size=size, **kw).at(x, yy, anchor=anchor)

        wires = [
            seg((120, rail), (dx_ + 60, rail)),
            seg((150, rail + 80), (150, gy)), seg((150, gy), (mx, gy)),
            seg((dx_, rail + 70), (dx_, gy - 54)),
            seg((dx_, gy + 54), (dx_, gy + 80), (dx_ + 70, gy + 80)),
            seg((dx_, gy - 74), (dx_ + 60, gy - 74)), seg((dx_ + 110, gy - 74), (dx_ + 170, gy - 74)),
            seg((dx_ + 140, gy - 74), (dx_ + 140, gy - 74 + 24)),
            seg((30 + 5, gy), (60, gy)), seg((110, gy), (150, gy)),
        ]
        diag.path(" ".join(wires), style=WIRE)
        diag.path(resistor((150, rail), (150, rail + 80)), style=WIRE)               # R1
        diag.path(resistor((150, gy), (150, gy + 80)), style=WIRE)                   # R2
        diag.path(ground(150, gy + 80), style=WIRE)
        diag.path(resistor((dx_, rail), (dx_, rail + 70)), style=WIRE)               # RD
        diag.path(capacitor((60, gy), (110, gy)), style=WIRE)                        # C_in
        diag.path(capacitor((dx_ + 60, gy - 74), (dx_ + 110, gy - 74)), style=WIRE)  # C_out
        diag.path(resistor((dx_ + 140, gy - 74 + 24), (dx_ + 140, gy + 56)), style=WIRE)  # R_L
        diag.path(ground(dx_ + 140, gy + 56), style=WIRE)
        # transistor: gate plate, channel in three pieces, drain and source leads
        diag.path(" ".join([
            seg((mx, gy - 28), (mx, gy + 28)),
            seg((mx + 12, gy - 30), (mx + 12, gy - 18)), seg((mx + 12, gy - 8), (mx + 12, gy + 8)),
            seg((mx + 12, gy + 18), (mx + 12, gy + 30)),
            seg((mx + 12, gy - 24), (dx_, gy - 24), (dx_, gy - 54)),
            seg((mx + 12, gy + 24), (dx_, gy + 24), (dx_, gy + 54)),
            seg((mx + 12, gy), (dx_, gy), (dx_, gy + 24)),
        ]), style=WIRE)
        diag.path(f"M {mx + 13} {gy} L {mx + 24} {gy - 6} L {mx + 24} {gy + 6} Z",
                  style=Style(fill=INK, stroke=INK, stroke_width=1.0))
        # source network: R_S in parallel with the bypass capacitor
        diag.path(resistor((dx_, gy + 80), (dx_, gy + 150)), style=WIRE)
        diag.path(capacitor((dx_ + 70, gy + 80), (dx_ + 70, gy + 150)), style=WIRE)
        diag.path(seg((dx_, gy + 150), (dx_ + 70, gy + 150)), style=WIRE)
        diag.path(ground(dx_ + 35, gy + 150), style=WIRE)
        diag.path(" ".join([circle(30, gy, 5), circle(dx_ + 170, gy - 74, 5)]), style=WHITE, z=1)
        for jx, jy in ((150, gy), (dx_, gy - 74), (dx_ + 140, gy - 74), (dx_, gy + 80)):
            diag.point(jx, jy, dot=True, radius=4)
        text("$v_{in}$", 30, gy - 14, anchor="bottom_center", size=15)
        text("$v_{out}$", dx_ + 170, gy - 90, anchor="bottom_center", size=15)
        text(f"$V_{{DD}} = {VDD:g}$ V", 124, rail - 8, anchor="bottom_left")
        text(f"$R_1 = {R1 / 1e3:g}\\,\\mathrm{{k}}\\Omega$", 136, rail + 40, anchor="right_center")
        text(f"$R_2 = {R2 / 1e3:g}\\,\\mathrm{{k}}\\Omega$", 136, gy + 40, anchor="right_center")
        text(f"$R_D = {RD / 1e3:g}\\,\\mathrm{{k}}\\Omega$", dx_ - 14, rail + 35, anchor="right_center")
        text(f"$R_S = {RS / 1e3:g}\\,\\mathrm{{k}}\\Omega$", dx_ - 14, gy + 115, anchor="right_center")
        text("$C_S$", dx_ + 96, gy + 115, anchor="left_center")
        text("$C_{in}$", 85, gy - 24, anchor="bottom_center")
        text("$C_{out}$", dx_ + 85, gy - 100, anchor="bottom_center")
        text(f"$R_L = {RL / 1e3:g}\\,\\mathrm{{k}}\\Omega$", dx_ + 154, gy - 8, anchor="left_center")
        text("$V_G$", 205, gy - 14, anchor="bottom_center", color=RED)
        text("$V_D$", dx_ + 12, gy - 90, anchor="bottom_left", color=RED)
        text("$V_S$", dx_ + 12, gy + 66, anchor="bottom_left", color=RED)

        text(
            "**DC bias** (square law, $V_T = 2$ V, $K = 2$ mA/V$^2$)\n"
            f"$V_G = V_{{DD}} R_2 / (R_1 + R_2) = {vg:.2f}$ V\n"
            f"$I_D = (K/2)(V_G - I_D R_S - V_T)^2 = {i_d * 1e3:.3f}$ mA\n"
            f"$V_{{GS}} = {vgs:.2f}$ V, $V_{{ov}} = {vov:.2f}$ V\n"
            f"$V_S = {vs:.2f}$ V, $V_D = V_{{DD}} - I_D R_D = {vd:.2f}$ V\n"
            f"$V_{{DS}} = {vd - vs:.2f}$ V $> V_{{ov}}$: saturation",
            600, 70, anchor="top_left", size=13)
        text(
            "**Small signal** ($C_S$ bypasses $R_S$)\n"
            f"$g_m = K V_{{ov}} = {gm * 1e3:.2f}$ mS\n"
            f"$A_v = -g_m (R_D \\parallel R_L) = -{gm * 1e3:.2f}\\,\\mathrm{{mS}} \\times {r_par / 1e3:.2f}\\,\\mathrm{{k}}\\Omega = {av:.2f}$\n"
            f"$R_{{in}} = R_1 \\parallel R_2 = {r_in / 1e3:.0f}\\,\\mathrm{{k}}\\Omega$,  $R_{{out}} = R_D = {RD / 1e3:g}\\,\\mathrm{{k}}\\Omega$",
            600, 230, anchor="top_left", size=13)

        p = Plot(diag, x=(0, VDD), y=(0, 3.0), origin=(110, 690), size=(420, 230))
        p.grid(2, 0.5)
        p.axes(xlabel="$V_{DS}$ (V)", ylabel="$I_D$ (mA)", xstep=2, ystep=0.5, through_zero=False)
        for v, colour in ((2.5, GREY), (3.5, GREY), (vgs, BLUE)):
            p.function(lambda x, v=v: drain_current(v, x) * 1e3, stroke=colour, width=2.0 if v == vgs else 1.3, n=240)
            p.label(VDD, drain_current(v, VDD) * 1e3, f"$V_{{GS}} = {v:.2f}$ V" if v == vgs else f"{v:g} V",
                    size=11, anchor="left_center", dx=6, color=BLUE if v == vgs else "#555555")
        p.line((0, VDD / (RD + RS) * 1e3), (VDD, 0), stroke=RED, dash="6,4", width=1.5)
        p.label(1.2, VDD / (RD + RS) * 1e3, f"load line, slope $-1/(R_D + R_S)$", size=11, color=RED, anchor="left_center", dx=6, dy=-12)
        p.dot(vd - vs, i_d * 1e3, radius=4.5, label=f"Q ({vd - vs:.2f} V, {i_d * 1e3:.3f} mA)", dx=10, dy=-10, anchor="bottom_left")
        diag.text("**Output characteristics**", size=14).at(320, 460, anchor="bottom_center")
        diag.caption("**Figure 3:** Bias network, quiescent point and small-signal gain of a bypassed common-source stage",
                     small_caps=True)
    return diag


def build_diagram(output_dir: Path | str = "examples/electronics") -> Path:
    return render_all(diagram(), output_dir, "03_mosfet_common_source")["svg"]


if __name__ == "__main__":
    dest = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("examples/electronics")
    build_diagram(dest)
