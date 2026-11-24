"""The SN2 mechanism: hydroxide attacking bromomethane, drawn schematically.

The atoms are placed by hand (this gallery has no molecule layout) and the bonds are
shortened to stop at the atom labels. Curved arrows follow the electrons: arrow 1
runs from a lone pair on oxygen to carbon, arrow 2 from the C-Br bond to bromine.
The reaction is concerted: the nucleophile enters opposite the leaving group, the
three hydrogens flip through the planar transition state like an umbrella in the
wind (inversion), and nothing is left over between the steps. The small profile
underneath has a single barrier and no intermediate, and the rate law
$\\mathrm{rate} = k[\\mathrm{CH_3Br}][\\mathrm{OH^-}]$ is first order in each
reactant.
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

from diagrams_as_code import Diagram, Style
from diagrams_as_code.output import render_all
from diagrams_as_code.plot import Plot

INK, RED, BLUE, GREY = "#111111", "#9C2F2F", "#1F2F57", "#777777"
Y = 215.0
L = 80.0                         # bond length along the axis, px
H_OFFSETS = [(0, -58), (-33, 42), (33, 42)]     # three hydrogens seen along the C-X axis


def shorten(a, b, ra, rb):
    dx, dy = b[0] - a[0], b[1] - a[1]
    n = math.hypot(dx, dy)
    return (a[0] + dx / n * ra, a[1] + dy / n * ra), (b[0] - dx / n * rb, b[1] - dy / n * rb)


def bond(diag, a, b, ra=11, rb=11, dash="", width=2.0):
    p, q = shorten(a, b, ra, rb)
    diag.polyline([p, q], style=Style(stroke=INK, stroke_width=width, dash=dash))


def dots(diag, x, y, radius=2.2):
    diag.polygon([(x + radius * math.cos(k * math.pi / 6), y + radius * math.sin(k * math.pi / 6)) for k in range(12)],
                 style=Style(fill=INK, stroke=INK, stroke_width=0.5), z=2)


def curved(diag, a, via, b, color):
    diag.connect(a, b, routing="spline", via=[via], width=1.8, color=color, head="stealth", arrow_size=0.9)


def stage(diag, cx, nu, lg, shift, nu_label, lg_label, nu_r, lg_r, partial=False, lg_bond=True):
    """One snapshot: carbon at (cx, Y), nucleophile and leaving group on the axis."""
    c = (cx, Y)
    n_pos, l_pos = (cx + nu, Y), (cx + lg, Y)
    diag.text("C", size=22).at(*c, anchor="center")
    diag.text(nu_label, size=20).at(*n_pos, anchor="center")
    diag.text(lg_label, size=20).at(*l_pos, anchor="center")
    bond(diag, c, n_pos, 11, nu_r, dash="5,4" if partial else "")
    if lg_bond:
        bond(diag, c, l_pos, 11, lg_r, dash="5,4" if partial else "")
    for dx, dy in H_OFFSETS:
        h = (cx + dx + shift, Y + dy)
        diag.text("H", size=18).at(*h, anchor="center")
        bond(diag, c, h, 11, 10, width=1.8)
    return c, n_pos, l_pos


def smooth(t):
    t = min(max(t, 0.0), 1.0)
    return t * t * (3 - 2 * t)


def diagram() -> Diagram:
    with Diagram("SN2 mechanism", theme="paper") as diag:
        diag.text("$\\ce{HO- + CH3Br -> HOCH3 + Br-}$", size=20).at(520, 52, anchor="center")

        # 1. Reactants: the hydrogens lean towards the nucleophile's side.
        cx1 = 205
        c, n, l = stage(diag, cx1, -L - 20, L, -16, "$\\ce{HO-}$", "Br", 26, 17)
        dots(diag, n[0] - 7, n[1] - 21)
        dots(diag, n[0] + 1, n[1] - 21)
        curved(diag, (n[0] - 3, n[1] - 29), (cx1 - 55, Y - 104), (cx1 - 14, Y - 14), RED)
        curved(diag, (cx1 + L * 0.5, Y - 6), (cx1 + L * 0.95, Y - 78), (l[0] + 4, Y - 24), BLUE)
        diag.text("**1**", size=15, color=RED).at(cx1 - 72, Y - 100, anchor="right_center")
        diag.text("**2**", size=15, color=BLUE).at(cx1 + L * 0.95 + 16, Y - 78, anchor="left_center")

        # 2. Transition state: planar CH3, both partial bonds dashed, charge shared.
        cx2 = 560
        c, n, l = stage(diag, cx2, -L - 12, L + 12, 0, "HO", "Br", 18, 17, partial=True)
        diag.text("$\\delta^-$", size=15).at(n[0], n[1] - 30, anchor="center")
        diag.text("$\\delta^-$", size=15).at(l[0], l[1] - 30, anchor="center")
        top, bot = Y - 100, Y + 78
        x0, x1 = cx2 - L - 62, cx2 + L + 62
        diag.polyline([(x0 + 14, top), (x0, top), (x0, bot), (x0 + 14, bot)], style=Style(stroke=INK, stroke_width=1.8))
        diag.polyline([(x1 - 14, top), (x1, top), (x1, bot), (x1 - 14, bot)], style=Style(stroke=INK, stroke_width=1.8))
        diag.text("transition state", size=13).at(cx2, top - 12, anchor="bottom_center")

        # 3. Products: inverted, hydrogens lean the other way.
        cx3 = 880
        c, n, l = stage(diag, cx3, -L + 10, L + 30, 16, "HO", "$\\ce{Br-}$", 18, 26, lg_bond=False)
        diag.text("+", size=22).at(cx3 + 62, Y, anchor="center")

        # Arrows between the snapshots.
        for xa, xb in ((365, 415), (715, 765)):
            diag.connect((xa, Y), (xb, Y), routing="direct", width=2.0, head="stealth", color=INK)
        for x, text in ((cx1 + 10, "Reactants:\nbackside attack"), (cx2, "Concerted:\nbonds form and break together"),
                        (cx3, "Products:\nconfiguration inverted")):
            diag.text(text, size=13).at(x, Y + 105, anchor="top_center")

        # Energy profile with a single barrier.
        p = Plot(diag, x=(0, 1), y=(0, 1.25), origin=(60, 600), size=(330, 170))
        p.axes(xlabel="", ylabel="energy", labels=False, through_zero=False, xstep=10, ystep=1000)

        def energy(x):
            return 0.55 + 0.7 * smooth(x / 0.5) if x <= 0.5 else 1.25 - 1.0 * smooth((x - 0.5) / 0.5)
        p.function(energy, 0, 1, stroke=BLUE, width=2.4)
        p.dot(0.5, 1.25, radius=3.5)
        p.label(0.5, 1.25, "single barrier, no intermediate", size=12, anchor="bottom_center", dy=-8)
        p.label(0.02, 0.55, "$\\ce{HO- + CH3Br}$", size=12, anchor="top_left", dy=6)
        p.label(0.98, 0.25, "$\\ce{HOCH3 + Br-}$", size=12, anchor="top_right", dy=6)
        diag.text("reaction coordinate", size=12).at(225, 612, anchor="top_center")

        x = 470
        diag.text(
            "**What the arrows show**\n"
            "1  lone pair on O becomes the new O-C bond\n"
            "2  the C-Br bond pair leaves with bromine as $\\ce{Br-}$",
            size=13,
        ).at(x, 405, anchor="top_left")
        diag.text(
            "**Kinetics and stereochemistry**\n"
            "$\\mathrm{rate} = k\\,[\\ce{CH3Br}]\\,[\\ce{OH-}]$: second order overall\n"
            "attack is from the side opposite Br (about 180 degrees),\n"
            "so a chiral carbon would invert (Walden inversion)",
            size=13,
        ).at(x, 475, anchor="top_left")
        diag.text("Primary and methyl halides react fastest;\nbulky substrates hinder the backside approach.",
                  size=13).at(x, 575, anchor="top_left")
        diag.caption("**Figure 6:** The SN2 mechanism for hydroxide and bromomethane: curved arrows, a planar transition state and inversion",
                     small_caps=True)
    return diag


def build_diagram(output_dir: Path | str = "examples/chemistry") -> Path:
    return render_all(diagram(), output_dir, "06_sn2_mechanism")["svg"]


if __name__ == "__main__":
    build_diagram(Path(sys.argv[1]) if len(sys.argv) > 1 else Path("examples/chemistry"))
