"""A 555 timer astable oscillator with its computed frequency, duty cycle and waveforms.

The timing network (R1, R2, C) charges between the two internal comparator
thresholds, V_CC/3 and 2 V_CC/3. The high and low times, the frequency and the
duty cycle are computed from the component values, and the capacitor and output
waveforms are the exact exponential segments with those times.
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



VCC, R1, R2, C = 9.0, 1e3, 10e3, 100e-9   # volt, ohm, ohm, farad
BLUE, RED, GREEN = "#1F2F57", "#9C2F2F", "#2F6B3A"


def diagram() -> Diagram:
    ln2 = math.log(2)
    t_h, t_l = ln2 * (R1 + R2) * C, ln2 * R2 * C
    period = t_h + t_l
    freq, duty = 1 / period, t_h / period
    lo, hi = VCC / 3, 2 * VCC / 3
    tau_c, tau_d = (R1 + R2) * C, R2 * C

    def v_c(t: float) -> float:
        tt = t % period
        return VCC - (VCC - lo) * math.exp(-tt / tau_c) if tt < t_h else hi * math.exp(-(tt - t_h) / tau_d)

    def v_out(t: float) -> float:
        return VCC if t % period < t_h else 0.0

    rail = 100.0
    bx0, bx1, by0, by1 = 260.0, 390.0, 150.0, 290.0     # the 555 body
    with Diagram("555 timer astable oscillator", theme="paper") as diag:
        def text(s, x, yy, anchor="center", size=14, **kw):
            diag.text(s, size=size, **kw).at(x, yy, anchor=anchor)

        diag.path(" ".join([
            seg((110, rail), (350, rail)),
            seg((150, rail + 60), (150, 180)), seg((150, 180), (bx0, 180)),
            seg((150, 250), (200, 250)), seg((bx0, 220), (200, 220), (200, 260), (bx0, 260)),
            seg((300, by0), (300, rail)), seg((350, by0), (350, rail)),
            seg((150, 250), (150, 262)),
            seg((330, by1), (330, 330)), seg((bx1, 220), (455, 220)),
        ]), style=WIRE)
        diag.path(resistor((150, rail), (150, rail + 60)), style=WIRE)               # R1
        diag.path(resistor((150, 180), (150, 250)), style=WIRE)                      # R2
        diag.path(capacitor((150, 262), (150, 325)), style=WIRE)                     # C
        diag.path(ground(150, 325) + " " + ground(330, 330), style=WIRE)
        diag.path(capacitor((290, by1), (290, 340)) + " " + ground(290, 340), style=WIRE)   # 10 nF on CONTROL
        diag.path(f"M {bx0} {by0} L {bx1} {by0} L {bx1} {by1} L {bx0} {by1} Z", style=WHITE)
        diag.path(circle(460, 220, 5), style=WHITE, z=1)
        for p in ((150, 180), (150, 250), (200, 250), (300, rail), (350, rail)):
            diag.point(*p, dot=True, radius=4)
        text("**555**", 320, 215, size=20)
        for s, x, yy, a in (("DIS", bx0 + 6, 180, "left_center"), ("THR", bx0 + 6, 220, "left_center"),
                            ("TRIG", bx0 + 6, 260, "left_center"), ("OUT", bx1 - 6, 220, "right_center"),
                            ("VCC", 300, by0 + 6, "top_center"), ("RST", 350, by0 + 6, "top_center"),
                            ("GND", 330, by1 - 6, "bottom_center"), ("CTL", 290, by1 - 6, "bottom_center")):
            text(s, x, yy, anchor=a, size=11)
        for s, x, yy, a in (("7", bx0 - 6, 174, "bottom_right"), ("6", bx0 - 6, 214, "bottom_right"), ("2", bx0 - 6, 254, "bottom_right"),
                            ("3", bx1 + 6, 214, "bottom_left"), ("8", 308, by0 - 6, "bottom_left"), ("4", 358, by0 - 6, "bottom_left"),
                            ("1", 338, by1 + 6, "top_left"), ("5", 298, by1 + 6, "top_left")):
            text(s, x, yy, anchor=a, size=11, color="#555555")
        text(f"$V_{{CC}} = +{VCC:g}$ V", 110, rail - 8, anchor="bottom_left")
        text(f"$R_1 = {R1 / 1e3:g}\\,\\mathrm{{k}}\\Omega$", 136, rail + 30, anchor="right_center")
        text(f"$R_2 = {R2 / 1e3:g}\\,\\mathrm{{k}}\\Omega$", 136, 215, anchor="right_center")
        text(f"$C = {C * 1e9:g}\\,\\mathrm{{nF}}$", 126, 294, anchor="right_center")
        text("10 nF", 264, 318, anchor="right_center", size=12)
        text("$v_{out}$", 460, 204, anchor="bottom_center", size=15)
        text("$v_C$", 176, 242, anchor="bottom_center", color=GREEN)

        text(
            f"**Timing** ($V_{{CC}} = {VCC:g}$ V, $R_1 = {R1 / 1e3:g}$ k$\\Omega$, $R_2 = {R2 / 1e3:g}$ k$\\Omega$, $C = {C * 1e9:g}$ nF)\n"
            f"$t_H = \\ln 2\\,(R_1 + R_2)\\,C = {t_h * 1e3:.3f}$ ms (charge through $R_1 + R_2$)\n"
            f"$t_L = \\ln 2\\,R_2\\,C = {t_l * 1e3:.3f}$ ms (discharge through $R_2$ into DIS)\n"
            f"$T = t_H + t_L = {period * 1e3:.3f}$ ms, $f = 1/T = {freq:.1f}$ Hz\n"
            f"(shortcut $1.44 / ((R_1 + 2R_2) C) = {1.44 / ((R1 + 2 * R2) * C):.1f}$ Hz)\n"
            f"duty $= t_H / T = (R_1 + R_2)/(R_1 + 2R_2) = {duty * 100:.1f}\\%$\n"
            f"$v_C$ swings between $V_{{CC}}/3 = {lo:g}$ V and $2V_{{CC}}/3 = {hi:g}$ V,\n"
            "so the timing does not depend on $V_{CC}$",
            540, 70, anchor="top_left", size=13)

        p = Plot(diag, x=(0, 4e-3), y=(0, 10), origin=(100, 670), size=(560, 230))
        p.grid(0.5e-3, 2)
        p.axes(xlabel="$t$ (ms)", ylabel="$v$ (V)", xstep=0.5e-3, ystep=2, through_zero=False,
               xtick_labels={k * 0.5e-3: f"{k * 0.5:g}" for k in range(9)})
        p.hline(hi, stroke="#8A5A00")
        p.hline(lo, stroke="#8A5A00")
        p.label(4e-3, hi, f"$2V_{{CC}}/3$ = {hi:g} V", size=12, anchor="left_center", dx=8, color="#8A5A00")
        p.label(4e-3, lo, f"$V_{{CC}}/3$ = {lo:g} V", size=12, anchor="left_center", dx=8, color="#8A5A00")
        pts, k = [], 0
        while k * period < 4e-3:
            t0 = k * period
            pts += [(t0, 0), (t0, VCC), (t0 + t_h, VCC), (t0 + t_h, 0)]
            k += 1
        pts.append((4e-3, 0))
        p.polyline(pts, stroke=BLUE, width=2.2)
        p.function(v_c, stroke=GREEN, width=2.0, n=1200)
        p.label(t_h / 2, VCC, f"$t_H$ = {t_h * 1e3:.3f} ms", size=12, anchor="bottom_center", dy=-6)
        p.label(t_h + t_l / 2, 0, f"$t_L$ = {t_l * 1e3:.3f} ms", size=12, anchor="bottom_center", dy=-8)
        p.label(4e-3, VCC, "$v_{out}$", size=13, anchor="left_center", dx=8, color=BLUE)
        p.label(4e-3, 4.5, "$v_C$", size=13, anchor="left_center", dx=8, color=GREEN)
        diag.caption(f"**Figure 6:** A 555 astable oscillator running at {freq:.0f} Hz with a {duty * 100:.0f}% duty cycle",
                     small_caps=True)
    return diag


def build_diagram(output_dir: Path | str = "examples/electronics") -> Path:
    return render_all(diagram(), output_dir, "06_timer_555_astable")["svg"]


if __name__ == "__main__":
    dest = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("examples/electronics")
    build_diagram(dest)
