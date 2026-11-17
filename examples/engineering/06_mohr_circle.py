"""Mohr's circle for plane stress.

For $\\sigma_x = 80$, $\\sigma_y = -20$, $\\tau_{xy} = 30$ MPa the circle has centre
$\\sigma_c = (\\sigma_x + \\sigma_y)/2$ and radius $R = \\sqrt{((\\sigma_x - \\sigma_y)/2)^2 + \\tau_{xy}^2}$.
Principal stresses are $\\sigma_c \\pm R$, the maximum shear is $R$, and the
principal plane is rotated $\\theta_p = \\tfrac12\\arctan(2\\tau_{xy}/(\\sigma_x - \\sigma_y))$.
Shear is plotted positive downward (clockwise-positive convention).
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

from diagrams_as_code import Diagram, Style
from diagrams_as_code.output import render_all
from diagrams_as_code.plot import Plot

SX, SY, TXY = 80.0, -20.0, 30.0
RED, BLUE, GREEN, INK = "#9C2F2F", "#1F2F57", "#2E6B3F", "#111111"


def diagram() -> Diagram:
    c = (SX + SY) / 2
    r = math.hypot((SX - SY) / 2, TXY)
    s1, s2 = c + r, c - r
    two_tp = math.atan2(TXY, (SX - SY) / 2)      # angle from the X radius to the sigma axis
    with Diagram("Mohr's circle", theme="paper") as diag:
        # Same pixels per MPa on both axes: 3 px/MPa (190 x 160 MPa window).
        p = Plot(diag, x=(-70, 120), y=(-80, 80), origin=(110.0, 540.0), size=(570.0, 480.0))
        p.grid(xstep=20, ystep=20)
        ylab = {float(v): f"${-v:g}$" for v in range(-80, 81, 20)}
        p.axes(xlabel="$\\sigma$ (MPa)", ylabel="$\\tau$ (MPa, + down)", xstep=20, ystep=20,
               ytick_labels=ylab, size=11, through_zero=False)
        p.hline(0.0, stroke=INK, dash="", width=1.1)
        p.vline(0.0, stroke=INK, dash="", width=1.1)
        p.parametric(lambda t: c + r * math.cos(t), lambda t: r * math.sin(t), 0, 2 * math.pi, stroke=BLUE, width=2.4)
        # Plot-y is minus tau, so X(sx, +txy) sits below the axis.
        X, Y = (SX, -TXY), (SY, TXY)
        p.line(X, Y, stroke=INK, width=1.4)
        p.line((c, -r), (c, r), stroke="#8A8A8A", dash="4,3", width=0.9)
        p.dot(c, 0, radius=3.5)
        p.dot(*X, radius=4.5, label=f"$X\\,({SX:g},\\ {TXY:g})$", dx=10, dy=6, anchor="top_left", size=13)
        p.dot(*Y, radius=4.5, label=f"$Y\\,({SY:g},\\ {-TXY:g})$", dx=-10, dy=-6, anchor="bottom_right", size=13)
        p.dot(s1, 0, radius=4.5, fill=GREEN, stroke=GREEN)
        p.dot(s2, 0, radius=4.5, fill=GREEN, stroke=GREEN)
        p.label(s1, 0, f"$\\sigma_1 = {s1:.1f}$", dx=8, dy=-12, anchor="bottom_left", size=13, color=GREEN)
        p.label(s2, 0, f"$\\sigma_2 = {s2:.1f}$", dx=-6, dy=-12, anchor="bottom_right", size=13, color=GREEN)
        p.dot(c, r, radius=4.5, fill=RED, stroke=RED)
        p.label(c, r, f"$\\tau_{{max}} = {r:.1f}$", dx=10, dy=-12, anchor="bottom_left", size=13, color=RED)
        p.label(c, 0, f"$\\sigma_c = {c:g}$", dx=-6, dy=8, anchor="top_right", size=12)
        # Angle 2 theta_p between CX and the sigma axis.
        o = p.px(c, 0)
        rad = 44.0
        a0 = (o[0] + rad, o[1])
        a1 = (o[0] + rad * math.cos(two_tp), o[1] + rad * math.sin(two_tp))
        diag.path(f"M {a0[0]:.2f} {a0[1]:.2f} A {rad} {rad} 0 0 1 {a1[0]:.2f} {a1[1]:.2f}",
                  style=Style(fill="none", stroke=INK, stroke_width=1.0))
        diag.text("$2\\theta_p$", size=13).at(o[0] + rad + 8, o[1] + 14, anchor="left_center")

        res = (f"$\\sigma_c = {c:g}$ MPa,  $R = {r:.1f}$ MPa\n"
               f"$\\sigma_1 = {s1:.1f}$ MPa,  $\\sigma_2 = {s2:.1f}$ MPa\n"
               f"$\\tau_{{max}} = R = {r:.1f}$ MPa\n"
               f"$\\theta_p = {math.degrees(two_tp) / 2:.1f}^\\circ$ from the $x$ face")
        diag.text(res, size=13).at(710.0, 190.0, anchor="top_left")
        diag.text(f"Given: $\\sigma_x = {SX:g}$, $\\sigma_y = {SY:g}$, $\\tau_{{xy}} = {TXY:g}$ MPa", size=13).at(
            710.0, 150.0, anchor="top_left")
        diag.caption(
            "**Figure 6:** Mohr's circle for plane stress with principal stresses, maximum shear and principal angle",
            small_caps=True,
        )
    return diag


def build_diagram(output_dir: Path | str = "output/engineering") -> Path:
    return render_all(diagram(), output_dir, "06_mohr_circle")["svg"]


if __name__ == "__main__":
    dest = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("output/engineering")
    build_diagram(dest)
