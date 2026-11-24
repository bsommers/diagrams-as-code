"""Titration of a strong acid with a strong base: 25.00 mL of 0.100 M HCl with 0.100 M NaOH.

The pH is computed from the charge balance at every volume, not from the usual
three-region shortcuts: with $x = (C_a V_a - C_b V_b)/(V_a + V_b)$ the excess strong
acid (or minus the excess base), $[\\mathrm{H^+}] = \\tfrac{1}{2}(x + \\sqrt{x^2 + 4K_w})$
with $K_w = 1.0 \\times 10^{-14}$ at 25 C. The equivalence point falls at pH 7.00
because the salt NaCl does not hydrolyse; the curve is nearly vertical there, so
an indicator that changes colour anywhere in pH 4 to 10 marks it within a drop.
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

from diagrams_as_code import Diagram
from diagrams_as_code.output import render_all
from diagrams_as_code.plot import Plot

CA, VA, CB = 0.100, 25.00, 0.100          # mol/L, mL, mol/L
KW = 1.0e-14
INK, RED, BLUE, GREEN = "#111111", "#9C2F2F", "#1F2F57", "#2E6B3F"


def ph(vb: float) -> float:
    """pH after ``vb`` mL of base has been added."""
    x = (CA * VA - CB * vb) / (VA + vb)            # excess [H+] (negative: excess OH-)
    h = (x + math.sqrt(x * x + 4 * KW)) / 2
    return -math.log10(h)


def diagram() -> Diagram:
    v_eq = CA * VA / CB
    with Diagram("Strong acid - strong base titration", theme="paper") as diag:
        p = Plot(diag, x=(0, 50), y=(0, 14), origin=(90, 440), size=(560, 350))
        p.grid(xstep=10, ystep=2)
        p.axes(xlabel="volume of NaOH added (mL)", ylabel="pH", xstep=10, ystep=2, through_zero=False)

        # Indicator transition ranges as horizontal bands.
        p.band(lambda v: 3.1, lambda v: 4.4, fill="#F2DCDC")
        p.band(lambda v: 8.2, lambda v: 10.0, fill="#E7DCF2")
        p.label(50, 3.75, "methyl orange (3.1 to 4.4)", size=11, anchor="right_center", dx=-8, color=RED)
        p.label(50, 9.1, "phenolphthalein (8.2 to 10.0)", size=11, anchor="right_center", dx=-8, color="#5B3A8A")

        p.hline(7, stroke="#888888", width=0.9)
        p.vline(v_eq, stroke="#888888", width=0.9)
        p.function(ph, 0, 50, stroke=BLUE, width=2.6, n=1200)
        p.dot(v_eq, ph(v_eq), radius=4.5, label=f"equivalence point\n$V = {v_eq:g}$ mL, pH {ph(v_eq):.2f}",
              size=12, dx=10, dy=18, anchor="top_left")
        p.dot(0, ph(0), radius=3.5, label=f"start: pH {ph(0):.2f}", size=12, dx=8, dy=-8, anchor="bottom_left")
        p.dot(24.9, ph(24.9), radius=3.0)
        p.dot(25.1, ph(25.1), radius=3.0)

        x0 = 700
        diag.text(
            "**Reading the curve**\n"
            f"Start: $[\\ce{{H+}}] = 0.100$ M, pH {ph(0):.2f}\n"
            f"$V = 24.9$ mL: pH {ph(24.9):.2f}\n"
            f"$V = 25.0$ mL: pH {ph(25.0):.2f}\n"
            f"$V = 25.1$ mL: pH {ph(25.1):.2f}\n"
            f"$V = 50$ mL: pH {ph(50):.2f}",
            size=13,
        ).at(x0, 110, anchor="top_left")
        diag.text(
            "A 0.2 mL change (a few drops) around the\n"
            f"end point moves the pH by {ph(25.1) - ph(24.9):.1f} units, so\n"
            "either indicator band marks it sharply.",
            size=13,
        ).at(x0, 250, anchor="top_left")
        diag.text(
            "$\\ce{HCl + NaOH -> NaCl + H2O}$\n"
            "$C_a V_a = C_b V_b$ at equivalence",
            size=13,
        ).at(x0, 350, anchor="top_left")
        diag.caption("**Figure 2:** Titration curve of 25.00 mL of 0.100 M HCl with 0.100 M NaOH: a steep jump through pH 7 at the equivalence point",
                     small_caps=True)
    return diag


def build_diagram(output_dir: Path | str = "examples/chemistry") -> Path:
    return render_all(diagram(), output_dir, "02_strong_acid_base_titration")["svg"]


if __name__ == "__main__":
    build_diagram(Path(sys.argv[1]) if len(sys.argv) > 1 else Path("examples/chemistry"))
