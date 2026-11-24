"""Titration of a weak acid: 25.00 mL of 0.100 M acetic acid with 0.100 M NaOH.

Acetic acid has $\\mathrm{p}K_a = 4.76$ ($K_a = 1.74 \\times 10^{-5}$). At every volume
the pH is the root of the charge balance
$[\\mathrm{Na^+}] + [\\mathrm{H^+}] = [\\mathrm{OH^-}] + C_a K_a / (K_a + [\\mathrm{H^+}])$
(concentrations after dilution), found by bisection. The flat middle of the curve is
the buffer region, $\\mathrm{pH} = \\mathrm{p}K_a + \\log([\\mathrm{A^-}]/[\\mathrm{HA}])$,
and at half equivalence the two forms are equal so $\\mathrm{pH} = \\mathrm{p}K_a$.
The equivalence point lies above 7 because the acetate ion is a weak base.
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

from diagrams_as_code import Diagram
from diagrams_as_code.output import render_all
from diagrams_as_code.plot import Plot

CA, VA, CB = 0.100, 25.00, 0.100
KA = 1.74e-5
PKA = -math.log10(KA)
KW = 1.0e-14
INK, RED, BLUE, GREEN, GREY = "#111111", "#9C2F2F", "#1F2F57", "#2E6B3F", "#888888"


def ph(vb: float) -> float:
    vt = VA + vb
    ca, cb = CA * VA / vt, CB * vb / vt

    def f(p: float) -> float:
        h = 10.0 ** (-p)
        return cb + h - KW / h - ca * KA / (KA + h)

    lo, hi = 0.0, 14.0           # f > 0 at low pH, f < 0 at high pH
    for _ in range(80):
        mid = (lo + hi) / 2
        if f(mid) > 0:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


def strong(vb: float) -> float:
    x = (CA * VA - CB * vb) / (VA + vb)
    return -math.log10((x + math.sqrt(x * x + 4 * KW)) / 2)


def diagram() -> Diagram:
    v_eq, v_half = CA * VA / CB, CA * VA / CB / 2
    with Diagram("Weak acid titration with buffer region", theme="paper") as diag:
        p = Plot(diag, x=(0, 50), y=(0, 14), origin=(90, 440), size=(560, 350))
        p.grid(xstep=10, ystep=2)
        p.axes(xlabel="volume of NaOH added (mL)", ylabel="pH", xstep=10, ystep=2, through_zero=False)

        # Buffer region: 10 % to 90 % neutralised, i.e. pH = pKa +/- 1.
        vb_lo, vb_hi = 0.1 * v_eq, 0.9 * v_eq
        p.area(lambda v: 14, vb_lo, vb_hi, g=lambda v: 0, fill="#E3EDDC", opacity=0.8)
        p.label((vb_lo + vb_hi) / 2, 13.2, "buffer region", size=13, anchor="center", color=GREEN)
        p.label((vb_lo + vb_hi) / 2, 12.3, "pH within 1 of $\\mathrm{p}K_a$", size=11, anchor="center", color=GREEN)

        p.function(strong, 0, 50, stroke="#9AA6C4", width=1.5, dash="5,4", n=1000)
        p.function(ph, 0, 50, stroke=BLUE, width=2.6, n=800)
        p.legend([("acetic acid (weak)", BLUE, ""), ("strong acid, same concentration", "#9AA6C4", "5,4")],
                 at=(400, 330), size=12)

        p.hline(PKA, stroke=GREY, width=0.9)
        p.vline(v_half, stroke=GREY, width=0.9)
        p.vline(v_eq, stroke=GREY, width=0.9)
        p.dot(v_half, PKA, radius=4.5)
        p.label(v_half + 0.5, 9.0, f"**half equivalence**\n$V = {v_half:g}$ mL\npH = $\\mathrm{{p}}K_a$ = {PKA:.2f}",
                size=12, anchor="top_left")
        p.dot(v_eq, ph(v_eq), radius=4.5, label=f"equivalence point\n$V = {v_eq:g}$ mL, pH {ph(v_eq):.2f}",
              size=12, dx=10, dy=18, anchor="top_left")
        p.dot(0, ph(0), radius=3.5)

        x0 = 700
        diag.text(
            "**Why the shape**\n"
            f"Start: $[\\ce{{H+}}] \\approx \\sqrt{{K_a C_a}}$,\npH {ph(0):.2f} (weak acid, not pH 1)\n"
            f"Buffer: $V = {vb_lo:g}$ to ${vb_hi:g}$ mL,\n"
            f"pH {ph(vb_lo):.2f} to {ph(vb_hi):.2f}\n"
            f"Equivalence: only $\\ce{{A-}}$ left, with\n"
            f"$K_b = K_w / K_a = {KW / KA * 1e10:.2f} \\times 10^{{-10}}$,\npH {ph(v_eq):.2f}",
            size=13,
        ).at(x0, 110, anchor="top_left")
        diag.text(
            "$\\mathrm{pH} = \\mathrm{p}K_a + \\log\\dfrac{[\\ce{A-}]}{[\\ce{HA}]}$\n"
            "$\\ce{CH3COOH + OH- -> CH3COO- + H2O}$",
            size=13,
        ).at(x0, 270, anchor="top_left")
        diag.text("Phenolphthalein (8.2 to 10.0) suits this end\npoint; methyl orange (3.1 to 4.4) would\nchange colour long before it.",
                  size=12).at(x0, 340, anchor="top_left")
        diag.caption("**Figure 3:** Titration of 0.100 M acetic acid with NaOH: buffer region, half-equivalence point at pH = $\\mathrm{p}K_a$, and an equivalence point above 7",
                     small_caps=True)
    return diag


def build_diagram(output_dir: Path | str = "examples/chemistry") -> Path:
    return render_all(diagram(), output_dir, "03_weak_acid_buffer_titration")["svg"]


if __name__ == "__main__":
    build_diagram(Path(sys.argv[1]) if len(sys.argv) > 1 else Path("examples/chemistry"))
