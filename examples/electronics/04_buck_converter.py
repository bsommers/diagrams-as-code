"""A buck converter schematic with its switch-node voltage and inductor current waveforms.

The duty cycle, the inductor ripple current, the slopes of the two ramps, the
continuous-conduction check and the output ripple are computed from V_in, V_out,
L, f_sw and C, and the plotted waveforms use those same numbers (ideal switch and
diode, lossless).
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



VIN, VOUT, IOUT = 12.0, 5.0, 2.0       # volt, volt, ampere
L_H, FSW, C_F = 22e-6, 500e3, 47e-6    # henry, hertz, farad
BLUE, RED, GREEN = "#1F2F57", "#9C2F2F", "#2F6B3A"


def inductor(a, b, loops: int = 4, lead: float = 14.0) -> str:
    n, T = frame(a, b)
    r = (n - 2 * lead) / loops / 2
    pts = [T(0, 0), T(lead, 0)]
    for i in range(loops):
        pts += [T(lead + 2 * r * i + r - r * math.cos(math.pi * k / 16), -r * math.sin(math.pi * k / 16)) for k in range(1, 17)]
    return seg(*pts, T(n, 0))


def diode(a, b, half: float = 11.0) -> str:
    """Anode at ``a``, cathode (the bar) toward ``b``."""
    n, T = frame(a, b)
    m = n / 2
    return " ".join([seg(T(0, 0), T(m - half, 0)), seg(T(m - half, -half), T(m - half, half), T(m + half, 0), T(m - half, -half)),
                     seg(T(m + half, -half), T(m + half, half)), seg(T(m + half, 0), T(n, 0))])


def diagram() -> Diagram:
    duty = VOUT / VIN
    period_us = 1e6 / FSW
    ton = duty * period_us
    d_il = (VIN - VOUT) * duty / (L_H * FSW)
    i_min, i_max = IOUT - d_il / 2, IOUT + d_il / 2
    up, down = (VIN - VOUT) / L_H / 1e6, VOUT / L_H / 1e6   # A per microsecond
    d_v = d_il / (8 * FSW * C_F)
    r_load = VOUT / IOUT
    rail, gnd = 100.0, 270.0
    with Diagram("Buck converter and its inductor current", theme="paper") as diag:
        def text(s, x, yy, anchor="center", size=14, **kw):
            diag.text(s, size=size, **kw).at(x, yy, anchor=anchor)

        diag.path(" ".join([
            seg((80, rail), (140, rail)), seg((80, rail), (80, rail + 28)), seg((80, rail + 72), (80, gnd), (540, gnd)),
            seg((220, rail), (270, rail)), seg((390, rail), (555, rail)),
            seg((440, rail), (440, rail + 24)), seg((440, rail + 100), (440, gnd)),
            seg((530, rail), (530, rail + 24)), seg((530, rail + 110), (530, gnd)),
        ]), style=WIRE)
        diag.path(circle(80, rail + 50, 22), style=WHITE, z=1)                       # V_in source
        diag.path(seg((154, rail), (196, rail - 20)) + " " + seg((206, rail), (220, rail)), style=WIRE)                                                       # switch Q1 (shown open)
        diag.path(circle(154, rail, 3) + " " + circle(206, rail, 3), style=WHITE, z=1)
        diag.path(diode((270, gnd), (270, rail)), style=WIRE)                       # freewheel diode
        diag.path(inductor((270, rail), (390, rail)), style=WIRE)
        diag.path(capacitor((440, rail + 24), (440, rail + 100)), style=WIRE)
        diag.path(resistor((530, rail + 24), (530, rail + 110)), style=WIRE)
        diag.path(ground(300, gnd), style=WIRE)
        diag.path(circle(560, rail, 5), style=WHITE, z=1)
        for jx, jy in ((270, rail), (440, rail), (530, rail)):
            diag.point(jx, jy, dot=True, radius=4)
        text("+", 80, rail + 33, size=15)
        text("−", 80, rail + 69, size=15)
        text(f"$V_{{in}} = {VIN:g}$ V", 54, rail + 50, anchor="right_center")
        text("$Q_1$", 180, rail - 30, anchor="bottom_center")
        text("$D_1$", 288, (rail + gnd) / 2, anchor="left_center")
        text(f"$L = {L_H * 1e6:g}\\,\\mu\\mathrm{{H}}$", 330, rail - 22, anchor="bottom_center")
        text(f"$C = {C_F * 1e6:g}\\,\\mu\\mathrm{{F}}$", 418, rail + 62, anchor="right_center")
        text(f"$R = {r_load:g}\\,\\Omega$", 546, rail + 67, anchor="left_center")
        text("$v_{sw}$", 270, rail - 14, anchor="bottom_right", color=RED)
        text("$i_L$", 405, rail + 16, anchor="top_center", color=GREEN)
        text("$V_{out}$", 560, rail - 14, anchor="bottom_center", size=15)

        text(
            f"**Ideal CCM relations** (f$_{{sw}}$ = {FSW / 1e3:g} kHz, T = {period_us:g} $\\mu$s)\n"
            f"$D = V_{{out}} / V_{{in}} = {duty:.3f}$, so $t_{{on}} = {ton:.3f}\\,\\mu\\mathrm{{s}}$\n"
            f"on-ramp $(V_{{in}} - V_{{out}}) / L = +{up:.3f}$ A/$\\mu$s\n"
            f"off-ramp $-V_{{out}} / L = -{down:.3f}$ A/$\\mu$s\n"
            f"$\\Delta I_L = (V_{{in}} - V_{{out}}) D / (L f_{{sw}}) = {d_il:.3f}$ A p-p\n"
            f"$I_L$ runs {i_min:.3f} to {i_max:.3f} A about $I_{{out}} = {IOUT:g}$ A\n"
            f"CCM holds: $I_{{out}} > \\Delta I_L / 2 = {d_il / 2:.3f}$ A\n"
            f"$\\Delta V_{{out}} = \\Delta I_L / (8 f_{{sw}} C) = {d_v * 1e3:.2f}$ mV p-p (ESR ignored)",
            650, 60, anchor="top_left", size=13)

        for k, (oy, h, ylo, yhi, ystep, ylab, name) in enumerate((
            (470.0, 100.0, 0.0, 14.0, 6, "$v_{sw}$ (V)", "Switch node"),
            (680.0, 140.0, 1.8, 2.2, 0.1, "$i_L$ (A)", "Inductor current"),
        )):
            p = Plot(diag, x=(0, 2 * period_us), y=(ylo, yhi), origin=(100, oy), size=(440, h))
            p.grid(0.5, ystep)
            p.axes(xlabel="$t$ ($\\mu$s)" if k else "", ylabel=ylab, xstep=0.5, ystep=ystep, through_zero=False,
                   xlabels=bool(k))
            text(f"**{name}**", 320, oy - h - 22, size=14)
            for n_ in range(2):
                p.vline(n_ * period_us + ton, stroke="#8A8F9C", dash="3,3")
            if k == 0:
                pts = []
                for n_ in range(2):
                    t0 = n_ * period_us
                    pts += [(t0, 0), (t0, VIN), (t0 + ton, VIN), (t0 + ton, 0), (t0 + period_us, 0)]
                p.polyline(pts, stroke=RED, width=2.2)
                p.label(ton / 2, VIN, "$t_{on}$", size=12, anchor="bottom_center", dy=-6)
                p.label(ton + (period_us - ton) / 2, 0, "$t_{off}$", size=12, anchor="bottom_center", dy=-6)
            else:
                def il(t):
                    tt = t % period_us
                    return i_min + up * tt if tt < ton else i_max - down * (tt - ton)
                p.function(il, stroke=GREEN, width=2.2, n=800)
                p.hline(IOUT, stroke="#8A5A00")
                p.hline(i_max, stroke="#8A8F9C", dash="3,3")
                p.hline(i_min, stroke="#8A8F9C", dash="3,3")
                p.label(2 * period_us, i_max, f"{i_max:.3f} A", size=12, anchor="left_center", dx=8)
                p.label(2 * period_us, i_min, f"{i_min:.3f} A", size=12, anchor="left_center", dx=8)
                p.label(2 * period_us, IOUT, f"$I_{{out}}$ = {IOUT:g} A", size=12, anchor="left_center", dx=8, color="#8A5A00")
                p.label(0.2, 2.17, f"$\\Delta I_L$ = {d_il:.3f} A p-p", size=12, anchor="left_center")
        diag.caption("**Figure 4:** Buck converter in continuous conduction, with the ripple current computed from the circuit values",
                     small_caps=True)
    return diag


def build_diagram(output_dir: Path | str = "examples/electronics") -> Path:
    return render_all(diagram(), output_dir, "04_buck_converter")["svg"]


if __name__ == "__main__":
    dest = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("examples/electronics")
    build_diagram(dest)
