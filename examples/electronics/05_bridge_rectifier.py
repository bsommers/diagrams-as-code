"""A full-wave bridge rectifier with a smoothing capacitor and its ripple waveform.

The schematic is built from path symbols. The output waveform comes from a
time-stepped simulation of the diode bridge into the R and C load (two forward
drops, exponential discharge between peaks), and the ripple is read from the
last cycles of that simulation and compared with the V_pk / (2 f R C) estimate.
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



VRMS, FMAINS, VF = 12.0, 60.0, 0.7     # volt rms, hertz, diode drop in volt
R_LOAD, C_F = 100.0, 2200e-6           # ohm, farad
BLUE, RED = "#1F2F57", "#9C2F2F"


def diode(a, b, half: float = 10.0) -> str:
    """Anode at ``a``, cathode (the bar) toward ``b``."""
    n, T = frame(a, b)
    m = n / 2
    return " ".join([seg(T(0, 0), T(m - half, 0)), seg(T(m - half, -half), T(m - half, half), T(m + half, 0), T(m - half, -half)),
                     seg(T(m + half, -half), T(m + half, half)), seg(T(m + half, 0), T(n, 0))])


def simulate(cycles: int = 12, dt: float = 20e-6):
    """Output voltage of the bridge into R || C; returns (times, v_s, v_out)."""
    vpk = VRMS * math.sqrt(2)
    decay = math.exp(-dt / (R_LOAD * C_F))
    t, vc, ts, vs, vo = 0.0, 0.0, [], [], []
    while t < cycles / FMAINS:
        v = vpk * math.sin(2 * math.pi * FMAINS * t)
        vc = max(abs(v) - 2 * VF, vc * decay)
        ts.append(t), vs.append(v), vo.append(vc)
        t += dt
    return ts, vs, vo


def diagram() -> Diagram:
    vpk = VRMS * math.sqrt(2)
    v_peak_out = vpk - 2 * VF
    ts, vs, vo = simulate()
    span = 3 / FMAINS
    t0 = ts[-1] - span
    last = [v for t, v in zip(ts, vo) if t >= ts[-1] - 1 / FMAINS]
    v_hi, v_lo = max(last), min(last)
    ripple = v_hi - v_lo
    estimate = v_peak_out / (2 * FMAINS * R_LOAD * C_F)
    vdc = (v_hi + v_lo) / 2
    r_rms = ripple / (2 * math.sqrt(3) * vdc)
    top, bot, lft, rgt = (300.0, 130.0), (300.0, 270.0), (200.0, 200.0), (400.0, 200.0)
    with Diagram("Full-wave bridge rectifier with ripple", theme="paper") as diag:
        def text(s, x, yy, anchor="center", size=14, **kw):
            diag.text(s, size=size, **kw).at(x, yy, anchor=anchor)

        diag.path(" ".join([
            seg((80, 178), (80, top[1]), top), seg((80, 222), (80, bot[1]), bot),
            seg(lft, (170, lft[1])), seg(rgt, (580, rgt[1])),
            seg((460, rgt[1]), (460, rgt[1] + 24)), seg((460, rgt[1] + 100), (460, rgt[1] + 110)),
            seg((580, rgt[1]), (580, rgt[1] + 24)),
        ]), style=WIRE)
        for a, b in ((lft, top), (lft, bot), (top, rgt), (bot, rgt)):
            diag.path(diode(a, b), style=WIRE)
        diag.path(capacitor((460, rgt[1] + 24), (460, rgt[1] + 100)), style=WIRE)
        diag.path(resistor((580, rgt[1] + 24), (580, rgt[1] + 110)), style=WIRE)
        for gx, gy in ((170, lft[1]), (460, rgt[1] + 110), (580, rgt[1] + 110)):
            diag.path(ground(gx, gy), style=WIRE)
        diag.path(circle(80, 200, 22), style=WHITE, z=1)
        diag.path(seg(*[(67 + 26 * i / 40, 200 - 8 * math.sin(2 * math.pi * i / 40)) for i in range(41)]),
                  style=Style(fill="none", stroke=INK, stroke_width=1.6), z=2)
        for p in (top, bot, lft, rgt, (460, rgt[1]), (580, rgt[1])):
            diag.point(*p, dot=True, radius=4)
        text(f"$v_s$ = {VRMS:g} V rms\n{FMAINS:g} Hz", 54, 200, anchor="right_center")
        text("$D_1$", 238, 148, anchor="bottom_right")
        text("$D_2$", 238, 252, anchor="top_right")
        text("$D_3$", 362, 148, anchor="bottom_left")
        text("$D_4$", 362, 252, anchor="top_left")
        text("+", 418, 186, size=15, anchor="bottom_left")
        text(f"$C = {C_F * 1e6:,.0f}\\,\\mu\\mathrm{{F}}$", 484, 262, anchor="left_center")
        text(f"$R = {R_LOAD:g}\\,\\Omega$", 596, 262, anchor="left_center")
        text("$v_{out}$", 520, 184, anchor="bottom_center", size=15)

        text(
            f"$V_{{pk}} = \\sqrt{{2}} \\times {VRMS:g} = {vpk:.2f}$ V\n"
            f"two diodes conduct: $V_{{out,pk}} = V_{{pk}} - 2V_F = {v_peak_out:.2f}$ V\n"
            f"ripple frequency $2f = {2 * FMAINS:g}$ Hz ($T = {1e3 / (2 * FMAINS):.2f}$ ms)\n"
            f"$I_{{load}} \\approx V_{{out,pk}} / R = {v_peak_out / R_LOAD * 1e3:.0f}$ mA\n"
            f"estimate $\\Delta V \\approx V_{{out,pk}} / (2 f R C) = {estimate:.2f}$ V\n"
            f"simulated: {v_lo:.2f} to {v_hi:.2f} V, $\\Delta V = {ripple:.2f}$ V p-p\n"
            f"$V_{{dc}} \\approx {vdc:.2f}$ V, ripple factor $\\approx {r_rms * 100:.1f}\\%$ rms\n"
            f"diode peak inverse voltage $= V_{{pk}} = {vpk:.2f}$ V",
            650, 70, anchor="top_left", size=13)

        p = Plot(diag, x=(0, span * 1e3), y=(14, 18), origin=(100, 690), size=(520, 220))
        p.grid(10, 1)
        p.axes(xlabel="$t$ (ms)", ylabel="$v$ (V)", xstep=10, ystep=1, through_zero=False)
        p.function(lambda t: abs(vpk * math.sin(2 * math.pi * FMAINS * (t * 1e-3 + t0))), stroke="#8A8F9C", width=1.3, dash="5,4", n=400)
        p.polyline([((t - t0) * 1e3, v) for t, v in zip(ts, vo) if t >= t0], stroke=BLUE, width=2.2)
        p.hline(v_peak_out, stroke=RED, dash="3,3")
        p.hline(v_lo, stroke=RED, dash="3,3")
        p.label(span * 1e3, v_peak_out, f"{v_hi:.2f} V", size=12, anchor="left_center", dx=8, color=RED)
        p.label(span * 1e3, v_lo, f"{v_lo:.2f} V", size=12, anchor="left_center", dx=8, color=RED)
        p.label(6, 17.8, "$|v_s|$ (dashed): rectified mains, peaks only", size=12, anchor="left_center", color="#555555")
        p.label(6, 17.5, "$v_{out}$ (solid): across the capacitor", size=12, anchor="left_center", color=BLUE)
        diag.caption("**Figure 5:** A bridge rectifier charges the capacitor twice per mains cycle, leaving a sawtooth ripple",
                     small_caps=True)
    return diag


def build_diagram(output_dir: Path | str = "examples/electronics") -> Path:
    return render_all(diagram(), output_dir, "05_bridge_rectifier")["svg"]


if __name__ == "__main__":
    dest = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("examples/electronics")
    build_diagram(dest)
