"""Reaction energy profiles: an exothermic and an endothermic step, each with a catalysed path.

Energies are in kJ/mol. Each profile is built from two smoothsteps (reactants up to
the transition state, then down to the products), so the heights read off the figure
are exactly the numbers in the script. The activation energy is
$E_a = E_{TS} - E_{reactants}$ and the reaction enthalpy is
$\\Delta H = E_{products} - E_{reactants}$. A catalyst lowers $E_a$ for both
directions but leaves $\\Delta H$ unchanged.
"""
from __future__ import annotations

import sys
from pathlib import Path

from diagrams_as_code import Diagram
from diagrams_as_code.output import render_all
from diagrams_as_code.plot import Plot

INK, RED, BLUE, GREEN = "#111111", "#9C2F2F", "#1F2F57", "#2E6B3F"
# name, reactants, transition state, products, catalysed transition state (kJ/mol)
PANELS = [
    ("Exothermic", 60.0, 120.0, 20.0, 85.0),
    ("Endothermic", 20.0, 100.0, 70.0, 88.0),
]
XT = 0.5     # reaction coordinate of the transition state


def smooth(t: float) -> float:
    t = min(max(t, 0.0), 1.0)
    return t * t * (3 - 2 * t)


def profile(er: float, et: float, ep: float):
    def f(x: float) -> float:
        if x <= XT:
            return er + (et - er) * smooth(x / XT)
        return et + (ep - et) * smooth((x - XT) / (1 - XT))
    return f


def diagram() -> Diagram:
    with Diagram("Reaction energy profiles", theme="paper") as diag:
        for k, (name, er, et, ep, ecat) in enumerate(PANELS):
            p = Plot(diag, x=(0, 1), y=(0, 140), origin=(100 + k * 440, 440), size=(330, 330))
            p.axes(ylabel="energy", labels=False, through_zero=False, xstep=10, ystep=1000)
            diag.text("reaction coordinate", size=12).at(p.px(0.5, 0)[0], 458, anchor="top_center")
            p.function(profile(er, et, ep), 0, 1, stroke=INK, width=2.6)
            p.function(profile(er, ecat, ep), 0, 1, stroke=GREEN, width=2.2, dash="6,4")
            ea, ea_cat, dh = et - er, ecat - er, ep - er

            p.line((0.0, er), (0.97, er), stroke="#888888", width=0.8, dash="3,3")
            p.line((0.04, et), (XT, et), stroke="#888888", width=0.8, dash="3,3")
            p.label(0.02, er, "reactants", size=12, anchor="top_left", dy=5)
            p.label(0.92, ep, "products", size=12, anchor="top_right", dy=5)
            p.label(XT, et, "transition state", size=12, anchor="bottom_center", dy=-8)

            a0, a1 = p.px(0.04, er), p.px(0.04, et)
            diag.connect(a0, a1, routing="direct", two_way=True, width=1.1, arrow_size=0.7, color=RED)
            diag.text(f"$E_a = {ea:g}$", size=13, color=RED).at(a0[0] + 7, a1[1] + 18, anchor="left_center")
            c0, c1 = p.px(XT, er), p.px(XT, ecat)
            diag.connect(c0, c1, routing="direct", two_way=True, width=1.1, arrow_size=0.7, color=GREEN)
            y_c = er + 0.2 * (ecat - er)
            diag.text(f"$E_a' = {ea_cat:g}$", size=12, color=GREEN).at(c0[0] - 7, p.px(XT, y_c)[1], anchor="right_center")
            d0, d1 = p.px(0.97, er), p.px(0.97, ep)
            diag.connect(d0, d1, routing="direct", width=1.4, arrow_size=0.8, color=BLUE)
            sign = "+" if dh > 0 else "−"
            diag.text(f"$\\Delta H = {sign}{abs(dh):g}$", size=13, color=BLUE).at(
                d0[0] + 8, (d0[1] + d1[1]) / 2, anchor="left_center")
            p.legend([("uncatalysed", INK, ""), ("catalysed", GREEN, "6,4")], at=(p.ox + 215, 118), size=12)

            diag.text(f"**{name}**: $\\Delta H {'<' if dh < 0 else '>'} 0$", size=15).at(
                p.px(0.5, 0)[0], 90, anchor="center")
        diag.text("Energies in kJ/mol. A catalyst lowers $E_a$ for the forward and the reverse step alike,\n"
                  "so it changes how fast equilibrium is reached, not where it lies ($\\Delta H$ is unchanged).",
                  size=13).at(480, 495, anchor="top_center")
        diag.caption("**Figure 1:** Reaction energy profiles: activation energy $E_a$, reaction enthalpy $\\Delta H$ and a catalysed pathway",
                     small_caps=True)
    return diag


def build_diagram(output_dir: Path | str = "examples/chemistry") -> Path:
    return render_all(diagram(), output_dir, "01_reaction_energy_profile")["svg"]


if __name__ == "__main__":
    build_diagram(Path(sys.argv[1]) if len(sys.argv) > 1 else Path("examples/chemistry"))
