"""An RC low-pass filter drawn beside its Bode plot.

The schematic is built from path symbols. The corner frequency and the -3 dB and
-45 degree points are computed from R and C, and the magnitude and phase curves
are the exact first-order response, with the asymptotic roll-off dashed.
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



R, C = 10e3, 15.9e-9  # ohm, farad
FC = 1 / (2 * math.pi * R * C)
BLUE, RED = "#1F2F57", "#9C2F2F"


def mag_db(f: float) -> float:
    return -10 * math.log10(1 + (f / FC) ** 2)


def phase_deg(f: float) -> float:
    return -math.degrees(math.atan(f / FC))


def diagram() -> Diagram:
    tau = R * C
    y, x_in, x_r0, x_r1, x_n, x_out = 120.0, 80.0, 120.0, 230.0, 310.0, 400.0
    with Diagram("RC low-pass filter with its Bode plot", theme="paper") as diag:
        diag.path(" ".join([
            seg((x_in + 5, y), (x_r0, y)), seg((x_r1, y), (x_out - 5, y)),
            seg((x_n, y), (x_n, y + 30)),
        ]), style=WIRE)
        diag.path(resistor((x_r0, y), (x_r1, y)), style=WIRE)
        diag.path(capacitor((x_n, y + 30), (x_n, y + 100)), style=WIRE)
        diag.path(ground(x_n, y + 100), style=WIRE)
        diag.path(circle(x_in, y, 5) + " " + circle(x_out, y, 5), style=WHITE, z=1)
        diag.point(x_n, y, dot=True, radius=4)

        def text(s, x, yy, anchor="center", size=14, **kw):
            diag.text(s, size=size, **kw).at(x, yy, anchor=anchor)

        text("$v_{in}$", x_in, y - 14, anchor="bottom_center", size=15)
        text("$v_{out}$", x_out, y - 14, anchor="bottom_center", size=15)
        text(f"$R = {R / 1e3:g}\\,\\mathrm{{k}}\\Omega$", (x_r0 + x_r1) / 2, y - 22, anchor="bottom_center")
        text(f"$C = {C * 1e9:g}\\,\\mathrm{{nF}}$", x_n + 30, y + 65, anchor="left_center")
        text(
            "**Transfer function**\n"
            "$H(j\\omega) = v_{out} / v_{in} = 1 / (1 + j\\omega RC)$\n"
            "$|H| = 1 / \\sqrt{1 + (f / f_c)^2}$,  $\\angle H = -\\arctan(f / f_c)$",
            470, 70, anchor="top_left", size=13)
        text(
            f"$f_c = 1 / (2\\pi RC) = {FC:,.0f}$ Hz\n"
            f"$\\tau = RC = {tau * 1e6:.0f}\\,\\mu\\mathrm{{s}}$\n"
            f"at $f_c$: $|H| = {mag_db(FC):.2f}$ dB, $\\angle H = {phase_deg(FC):.0f}^\\circ$\n"
            f"one decade up ({FC * 10:,.0f} Hz): {mag_db(FC * 10):.1f} dB",
            470, 150, anchor="top_left", size=13)

        for (ox, title, ylo, ystep, fn, ylab) in (
            (90.0, "Magnitude", -40.0, 10, mag_db, "$|H|$ (dB)"),
            (500.0, "Phase", -90.0, 15, phase_deg, "$\\angle H$ (deg)"),
        ):
            p = Plot(diag, x=(5, 1e5), y=(ylo, 0.0), origin=(ox, 480), size=(280, 200), xscale="log")
            p.grid(None, ystep)
            p.axes(xlabel="$f$ (Hz)", ylabel=ylab, ystep=ystep, through_zero=False)
            text(f"**{title}**", ox + 140, 262, anchor="bottom_center", size=14)
            p.function(fn, stroke=BLUE, width=2.2)
            p.vline(FC)
            if fn is mag_db:
                p.line((5, 0), (FC, 0), stroke=RED, dash="5,4")
                p.line((FC, 0), (1e5, -20 * math.log10(1e5 / FC)), stroke=RED, dash="5,4")
                p.dot(FC, mag_db(FC), label="−3 dB at $f_c$", dx=10, dy=-4, anchor="bottom_left")
                p.label(2e4, -20 * math.log10(2e4 / FC), "−20 dB/dec", size=12, color=RED, anchor="left_center", dx=6, dy=-14)
            else:
                p.hline(-45)
                p.dot(FC, -45, label="−45° at $f_c$", dx=10, dy=-6, anchor="bottom_left")
        diag.caption("**Figure 1:** First-order RC low-pass filter and its asymptotic and exact Bode response", small_caps=True)
    return diag


def build_diagram(output_dir: Path | str = "examples/electronics") -> Path:
    return render_all(diagram(), output_dir, "01_rc_low_pass_bode")["svg"]


if __name__ == "__main__":
    dest = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("examples/electronics")
    build_diagram(dest)
