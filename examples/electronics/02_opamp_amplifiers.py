"""Inverting and non-inverting op-amp amplifiers with their gain formulas.

Both stages use the same R_f = 10 kOhm and a 1 kOhm input or ground resistor, so
the ideal gains (-10 and +11) and the 0.2 V peak sine response are computed from
the resistors. A 1 MHz gain-bandwidth product sets the closed-loop bandwidth.
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


def ground(x: float, y: float) -> str:
    return " ".join([seg((x, y), (x, y + 10)), seg((x - 14, y + 10), (x + 14, y + 10)),
                     seg((x - 9, y + 16), (x + 9, y + 16)), seg((x - 4, y + 22), (x + 4, y + 22))])


def circle(cx: float, cy: float, r: float) -> str:
    return f"M {cx - r} {cy} A {r} {r} 0 1 0 {cx + r} {cy} A {r} {r} 0 1 0 {cx - r} {cy} Z"



RF, RIN = 10e3, 1e3          # ohm
VIN_PK, F_IN, GBW = 0.2, 1e3, 1e6  # volt, hertz, hertz
INV_GAIN = -RF / RIN
NON_GAIN = 1 + RF / RIN
BLUE, RED, GREEN = "#1F2F57", "#9C2F2F", "#2F6B3A"


def opamp(x: float, y: float) -> str:
    """Triangle with its inputs at y - 20 / y + 20 and its output at (x + 72, y)."""
    return seg((x, y - 40), (x, y + 40), (x + 72, y), (x, y - 40))


def kohm(r: float) -> str:
    return f"{r / 1e3:g}\\,\\mathrm{{k}}\\Omega"


def diagram() -> Diagram:
    bw = GBW / (1 + RF / RIN)
    y = 170.0
    with Diagram("Inverting and non-inverting op-amp amplifiers", theme="paper") as diag:
        def text(s, x, yy, anchor="center", size=14, **kw):
            diag.text(s, size=size, **kw).at(x, yy, anchor=anchor)

        def stage(ox, inverting):
            ax = ox + 130                      # op-amp left edge
            out = (ax + 72, y)
            node_x, fb_x = ox + 105, ax + 100  # feedback node column and output tap
            top_in, bot_in = (ax, y - 20), (ax, y + 20)
            wires, junctions = [], [(fb_x, y)]
            diag.path(opamp(ax, y), style=WHITE)
            text("−" if inverting else "+", ax + 9, y - 20, size=16)
            text("+" if inverting else "−", ax + 9, y + 20, size=16)
            if inverting:
                wires += [seg((ox + 5, y - 20), (ox + 25, y - 20)), seg((ox + 95, y - 20), top_in),
                          seg((node_x, y - 20), (node_x, y - 70), (node_x + 14, y - 70)),
                          seg((fb_x - 14, y - 70), (fb_x, y - 70), (fb_x, y)),
                          seg(bot_in, (node_x, y + 20), (node_x, y + 52))]
                junctions.append((node_x, y - 20))
                diag.path(resistor((ox + 25, y - 20), (ox + 95, y - 20)), style=WIRE)
                diag.path(resistor((fb_x, y - 70), (node_x, y - 70)), style=WIRE)
                diag.path(ground(node_x, y + 52), style=WIRE)
                text(f"$R_{{in}} = {kohm(RIN)}$", ox + 60, y - 42, anchor="bottom_center")
                text(f"$R_f = {kohm(RF)}$", (node_x + fb_x) / 2, y - 94, anchor="bottom_center")
                text("$v_-\\approx 0$ (virtual ground)", ox + 12, y + 74, anchor="top_left", size=12, color=RED)
                in_pt = (ox, y - 20)
            else:
                wires += [seg((ox + 5, y - 20), top_in), seg(bot_in, (node_x, y + 20), (node_x, y + 72)),
                          seg((fb_x, y + 72), (fb_x, y))]
                junctions.append((node_x, y + 72))
                diag.path(resistor((node_x, y + 72), (fb_x, y + 72)), style=WIRE)
                diag.path(resistor((node_x, y + 72), (node_x, y + 142)), style=WIRE)
                diag.path(ground(node_x, y + 142), style=WIRE)
                text(f"$R_g = {kohm(RIN)}$", node_x - 16, y + 107, anchor="right_center")
                text(f"$R_f = {kohm(RF)}$", (node_x + fb_x) / 2, y + 96, anchor="top_center")
                in_pt = (ox, y - 20)
            wires.append(seg(out, (out[0] + 67, y)))
            diag.path(" ".join(wires), style=WIRE)
            diag.path(circle(*in_pt, 5) + " " + circle(out[0] + 72, y, 5), style=WHITE, z=1)
            for jx, jy in junctions:
                diag.point(jx, jy, dot=True, radius=4)
            text("$v_{in}$", in_pt[0], in_pt[1] - 14, anchor="bottom_center", size=15)
            text("$v_{out}$", out[0] + 72, y - 14, anchor="bottom_center", size=15)

        stage(60.0, True)
        stage(500.0, False)
        text("**Inverting**", 200, 30, size=15)
        text("**Non-inverting**", 640, 30, size=15)
        text(
            f"$A_v = v_{{out}} / v_{{in}} = -R_f / R_{{in}} = -{kohm(RF)} / {kohm(RIN)} = {INV_GAIN:g}$\n"
            f"input resistance $R_{{in}} = {RIN / 1e3:g}\\,\\mathrm{{k}}\\Omega$ (virtual ground at $v_-$)\n"
            f"$0.2\\,\\mathrm{{V}}$ peak in gives $v_{{out}} = {VIN_PK * INV_GAIN:g}$ V peak, inverted",
            60, 372, anchor="top_left", size=13)
        text(
            f"$A_v = 1 + R_f / R_g = 1 + {kohm(RF)} / {kohm(RIN)} = {NON_GAIN:g}$\n"
            f"input resistance is the op-amp's own (very high)\n"
            f"$0.2\\,\\mathrm{{V}}$ peak in gives $v_{{out}} = {VIN_PK * NON_GAIN:.1f}$ V peak, in phase",
            500, 372, anchor="top_left", size=13)
        text(
            f"Both stages have noise gain $1 + R_f / R_{{in}} = {1 + RF / RIN:g}$, so with $\\mathrm{{GBW}} = 1$ MHz "
            f"the bandwidth is $\\approx \\mathrm{{GBW}} / {1 + RF / RIN:g} = {bw / 1e3:.0f}$ kHz.",
            60, 452, anchor="top_left", size=13, font="serif", italic=True)

        p = Plot(diag, x=(0, 2e-3), y=(-2.5, 2.5), origin=(100, 712), size=(520, 190))
        p.grid(0.5e-3, 1)
        p.axes(xlabel="$t$ (ms)", ylabel="$v$ (V)", xstep=0.5e-3, ystep=1, size=11, through_zero=False,
               xtick_labels={k * 0.5e-3: f"{k * 0.5:g}" for k in range(0, 5)})
        p.hline(0, stroke="#8A8F9C", dash="")
        for gain, colour in ((1.0, BLUE), (INV_GAIN, RED), (NON_GAIN, GREEN)):
            p.function(lambda t, g=gain: g * VIN_PK * math.sin(2 * math.pi * F_IN * t), stroke=colour, width=2.0, n=300)
        p.legend([("$v_{in}$ (0.2 V peak, 1 kHz)", BLUE, ""),
                  (f"inverting, $v_{{out}}$ ({INV_GAIN:g}×)", RED, ""),
                  (f"non-inverting, $v_{{out}}$ ({NON_GAIN:g}×)", GREEN, "")], at=(680, 612))
        diag.caption("**Figure 2:** The same 10 kΩ feedback resistor gives a gain of −10 or +11 depending on which input is driven",
                     small_caps=True)
    return diag


def build_diagram(output_dir: Path | str = "examples/electronics") -> Path:
    return render_all(diagram(), output_dir, "02_opamp_amplifiers")["svg"]


if __name__ == "__main__":
    dest = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("examples/electronics")
    build_diagram(dest)
