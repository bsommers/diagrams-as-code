"""A power delivery network: VRM, bulk and decoupling capacitors, and impedance versus frequency.

Each capacitor group is a series R-L-C branch (ESR, ESL, capacitance) in parallel with
the others and with the VRM's closed-loop output impedance. The target impedance is
dV / dI, and the curves, anti-resonance peaks and worst-case margin are computed from
the branch values over 1 kHz to 100 MHz.
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


def capacitor(a, b, gap: float = 12.0, plate: float = 34.0) -> str:
    n, T = frame(a, b)
    m = n / 2
    return " ".join([seg(T(0, 0), T(m - gap / 2, 0)), seg(T(m - gap / 2, -plate / 2), T(m - gap / 2, plate / 2)),
                     seg(T(m + gap / 2, -plate / 2), T(m + gap / 2, plate / 2)), seg(T(m + gap / 2, 0), T(n, 0))])


def ground(x: float, y: float) -> str:
    return " ".join([seg((x, y), (x, y + 10)), seg((x - 14, y + 10), (x + 14, y + 10)),
                     seg((x - 9, y + 16), (x + 9, y + 16)), seg((x - 4, y + 22), (x + 4, y + 22))])


V_NOM, RIPPLE, DI = 1.0, 0.05, 10.0          # volt, fraction allowed, ampere load step
R_VRM, F_VRM = 2e-3, 1e5                      # VRM output resistance (ohm) and loop bandwidth (Hz)
F_LO, F_HI = 500.0, 1e8
# (name, count, C farad, ESR ohm, ESL henry, colour)
GROUPS = [
    ("bulk", 2, 470e-6, 8e-3, 4e-9, "#1F2F57"),
    ("mid", 8, 22e-6, 3e-3, 1.2e-9, "#2B7A78"),
    ("low", 16, 2.2e-6, 4e-3, 0.8e-9, "#7A4B9C"),
    ("fine", 16, 0.47e-6, 8e-3, 0.5e-9, "#C26A1B"),
    ("hf", 40, 100e-9, 25e-3, 0.5e-9, "#2F6B3A"),
]
RED, GREY = "#9C2F2F", "#8A8F9C"


def vrm_z(f: float) -> complex:
    return R_VRM * complex(1, f / F_VRM)


def group_z(f: float, n: int, c: float, esr: float, esl: float) -> complex:
    w = 2 * math.pi * f
    return complex(esr, w * esl - 1 / (w * c)) / n


def total_z(f: float) -> complex:
    y = 1 / vrm_z(f)
    for _, n, c, esr, esl, _ in GROUPS:
        y += 1 / group_z(f, n, c, esr, esl)
    return 1 / y


def unit(v: float) -> str:
    return f"{v * 1e6:g} $\\mu$F" if v >= 1e-6 else f"{v * 1e9:g} nF"


def diagram() -> Diagram:
    z_target = RIPPLE * V_NOM / DI
    fs = [F_LO * (F_HI / F_LO) ** (i / 800) for i in range(801)]
    zs = [abs(total_z(f)) for f in fs]
    peaks = [(fs[i], zs[i]) for i in range(1, 800) if zs[i] > zs[i - 1] and zs[i] > zs[i + 1]]
    worst = max(range(len(fs)), key=lambda i: zs[i])
    rail, gnd = 120.0, 250.0
    xs = [215.0 + 105.0 * k for k in range(len(GROUPS))]
    with Diagram("Power delivery network impedance", theme="paper") as diag:
        def text(s, x, yy, anchor="center", size=13, **kw):
            diag.text(s, size=size, **kw).at(x, yy, anchor=anchor)

        x_die = xs[-1] + 80
        wires = [seg((150, rail), (x_die, rail)), seg((105, rail + 40), (105, gnd), (x_die + 55, gnd), (x_die + 55, rail + 60))]
        for x in xs:
            wires += [seg((x, rail), (x, rail + 30)), seg((x, rail + 90), (x, gnd))]
        diag.path(" ".join(wires), style=WIRE)
        for x in xs:
            diag.path(capacitor((x, rail + 30), (x, rail + 90)), style=WIRE)
            diag.point(x, rail, dot=True, radius=4)
            diag.point(x, gnd, dot=True, radius=4)
        diag.path(ground(170, gnd), style=WIRE)
        for x0, y0, x1, y1 in ((60, rail - 20, 150, rail + 40), (x_die, rail - 30, x_die + 110, rail + 60)):
            diag.polygon([(x0, y0), (x1, y0), (x1, y1), (x0, y1)], style=WHITE)
        text("**VRM**", 105, rail - 6, size=14)
        text(f"{R_VRM * 1e3:g} m$\\Omega$", 105, rail + 14, size=12)
        text("**Die**", x_die + 55, rail - 8, size=14)
        text(f"$\\Delta I$ = {DI:g} A", x_die + 55, rail + 14, size=12)
        text(f"{V_NOM:g} V rail", 200, rail - 10, anchor="bottom_center", size=12, color="#555555")
        for x, (name, n, c, esr, esl, colour) in zip(xs, GROUPS):
            text(f"**{name}**", x + 24, rail + 60, anchor="left_center", size=12, color=colour)
            text(f"{n} × {unit(c)}\nESR {esr * 1e3:g} m$\\Omega$\nESL {esl * 1e9:g} nH", x, gnd + 14, anchor="top_center", size=11)

        p = Plot(diag, x=(F_LO, F_HI), y=(0.1, 1000.0), origin=(100, 740), size=(560, 300), xscale="log", yscale="log")
        p.grid()
        p.axes(xlabel="$f$ (Hz)", ylabel="$|Z|$ (m$\\Omega$)", through_zero=False)
        p.function(lambda f: abs(vrm_z(f)) * 1e3, stroke=GREY, width=1.3, dash="5,4", n=300)
        for name, n, c, esr, esl, colour in GROUPS:
            p.function(lambda f, a=(n, c, esr, esl): abs(group_z(f, *a)) * 1e3, stroke=colour, width=1.2, n=300)
        p.function(lambda f: abs(total_z(f)) * 1e3, stroke="#111111", width=2.8, n=600)
        p.hline(z_target * 1e3, stroke=RED, dash="6,4", width=1.5)
        p.label(F_LO, z_target * 1e3, f"$Z_{{target}}$ = {z_target * 1e3:g} m$\\Omega$", size=12, anchor="bottom_left", dx=8, dy=-4, color=RED)
        for f, z in peaks:
            p.dot(f, z * 1e3, radius=3.2)
        entries = [("total $|Z|$ seen by the die", "#111111", ""), ("VRM (loop bandwidth 100 kHz)", GREY, "5,4")]
        for name, n, c, esr, esl, colour in GROUPS:
            srf = 1 / (2 * math.pi * math.sqrt(esl / n * c * n))
            entries.append((f"{name}: SRF {srf / 1e6:.2g} MHz", colour, ""))
        p.legend(entries, at=(740, 420), size=11)
        text(
            f"**Target** $Z_{{target}} = \\Delta V / \\Delta I = ({RIPPLE * 100:g}\\% \\times {V_NOM:g}\\,\\mathrm{{V}}) / {DI:g}\\,\\mathrm{{A}} = {z_target * 1e3:g}$ m$\\Omega$\n"
            f"Worst case from {F_LO:g} Hz to {F_HI / 1e6:g} MHz: {zs[worst] * 1e3:.2f} m$\\Omega$ at {fs[worst] / 1e6:.0f} MHz\n"
            f"(margin {(1 - zs[worst] / z_target) * 100:.0f}%), set by the ESL of the last group\n"
            f"Anti-resonance peaks (dots): " + ", ".join(f"{f / 1e6:.2g} MHz ({z * 1e3:.1f})" for f, z in peaks) + " m$\\Omega$\n"
            f"Branch $|Z| = \\sqrt{{ESR^2 + (\\omega\\,ESL - 1/\\omega C)^2}} / n$, in parallel with the VRM",
            740, 580, anchor="top_left", size=12)
        diag.caption("**Figure 10:** Capacitor groups hand off to one another to keep the PDN impedance under the target from DC to 100 MHz",
                     small_caps=True)
    return diag


def build_diagram(output_dir: Path | str = "examples/electronics") -> Path:
    return render_all(diagram(), output_dir, "10_pdn_impedance")["svg"]


if __name__ == "__main__":
    dest = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("examples/electronics")
    build_diagram(dest)
