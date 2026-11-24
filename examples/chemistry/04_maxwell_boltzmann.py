"""Maxwell-Boltzmann distribution of molecular kinetic energies at two temperatures.

For translational motion the fraction of molecules per unit energy is
$f(E) = \\dfrac{2}{\\sqrt{\\pi}} (RT)^{-3/2} \\sqrt{E}\\, e^{-E/RT}$ with $E$ in kJ/mol and
$R = 8.314 \\times 10^{-3}$ kJ/(mol K). The area under each curve is 1. The shaded tail
is the fraction of molecules with $E > E_a$, which has a closed form,
$\\mathrm{erfc}(\\sqrt{x}) + 2\\sqrt{x/\\pi}\\, e^{-x}$ with $x = E_a / RT$, and is
what the Arrhenius factor $e^{-E_a/RT}$ approximates. The most probable energy is
$RT/2$ and the mean is $\\tfrac{3}{2} RT$.
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

from diagrams_as_code import Diagram
from diagrams_as_code.output import render_all
from diagrams_as_code.plot import Plot

R = 8.314e-3                  # kJ / (mol K)
EA = 10.0                     # activation energy, kJ/mol
TEMPS = [(300.0, "#1F2F57", "#9FB2DB"), (600.0, "#9C2F2F", "#E3A5A5")]
INK = "#111111"


def f(e: float, t: float) -> float:
    rt = R * t
    return 2 / math.sqrt(math.pi) * rt ** -1.5 * math.sqrt(e) * math.exp(-e / rt)


def tail(t: float, ea: float = EA) -> float:
    """Fraction of molecules with E > ea."""
    x = ea / (R * t)
    return math.erfc(math.sqrt(x)) + 2 * math.sqrt(x / math.pi) * math.exp(-x)


def diagram() -> Diagram:
    with Diagram("Maxwell-Boltzmann distribution", theme="paper") as diag:
        p = Plot(diag, x=(0, 40), y=(0, 0.22), origin=(90, 440), size=(560, 350))
        p.grid(xstep=10, ystep=0.05)
        p.axes(xlabel="kinetic energy $E$ (kJ/mol)", ylabel="fraction per kJ/mol, $f(E)$", xstep=10, ystep=0.05,
               through_zero=False)
        for t, line, fill in reversed(TEMPS):
            p.area(lambda e, t=t: f(e, t), EA, 40, fill=fill, opacity=0.9)
        p.vline(EA, stroke=INK, width=1.3)
        for t, line, fill in TEMPS:
            p.function(lambda e, t=t: f(e, t), 0, 40, stroke=line, width=2.6)
        p.label(EA, 0.21, f"$E_a = {EA:g}$ kJ/mol", size=13, anchor="left_center", dx=8)
        p.label(4.2, 0.17, "300 K", size=13, anchor="left_center", color=TEMPS[0][1])
        p.label(18, 0.035, "600 K", size=13, anchor="bottom_center", color=TEMPS[1][1])

        x0 = 700
        diag.text("**Molecules able to react ($E > E_a$)**", size=13).at(x0, 110, anchor="top_left")
        for k, (t, line, fill) in enumerate(TEMPS):
            y = 140 + 34 * k
            diag.text(f"$T = {t:g}$ K:  {100 * tail(t):.1f} %\n$RT = {R * t:.2f}$ kJ/mol", size=13,
                      color=line).at(x0, y, anchor="top_left")
        diag.text(
            f"Doubling $T$ multiplies the fraction by about {tail(600) / tail(300):.0f}:\n"
            "the tail grows, although the mean energy\n"
            "$\\tfrac{3}{2}RT$ only doubles (3.7 to 7.5 kJ/mol).",
            size=13,
        ).at(x0, 235, anchor="top_left")
        diag.text(
            "Peak at $E = RT/2$, so the hotter curve\n"
            "is lower, broader and shifted right;\n"
            "both enclose an area of 1.",
            size=13,
        ).at(x0, 320, anchor="top_left")
        diag.text("A catalyst that lowers $E_a$ moves the\nvertical line left and shades more area.",
                  size=13).at(x0, 380, anchor="top_left")
        diag.caption("**Figure 4:** Maxwell-Boltzmann energy distributions at 300 K and 600 K; the shaded tails are the molecules with energy above $E_a$",
                     small_caps=True)
    return diag


def build_diagram(output_dir: Path | str = "examples/chemistry") -> Path:
    return render_all(diagram(), output_dir, "04_maxwell_boltzmann")["svg"]


if __name__ == "__main__":
    build_diagram(Path(sys.argv[1]) if len(sys.argv) > 1 else Path("examples/chemistry"))
