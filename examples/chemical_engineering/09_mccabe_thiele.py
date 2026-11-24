"""McCabe-Thiele diagram for the benzene-toluene column of figure 2.

Equilibrium for constant relative volatility alpha = 2.5 is
y = alpha x / (1 + (alpha - 1) x). With reflux ratio R = 2 the rectifying line
is y = R x/(R+1) + xD/(R+1); the feed is saturated liquid, so the q-line is the
vertical x = zF; and the stripping line joins (xB, xB) to the point where the
rectifying line meets the q-line. Stages are stepped from the top, switching to
the stripping line at the feed intersection. The minimum reflux ratio comes
from the equilibrium point on the q-line.
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

from diagrams_as_code import Diagram, Style
from diagrams_as_code.output import render_all
from diagrams_as_code.plot import Plot

ALPHA, R = 2.5, 2.0
XD, ZF, XB = 0.95, 0.50, 0.05
BLUE, RED, GREEN, GREY, INK = "#1F4E8C", "#A33A3A", "#2E6B3F", "#777777", "#111111"


def eq(x: float) -> float:
    return ALPHA * x / (1 + (ALPHA - 1) * x)


def eq_inv(y: float) -> float:
    return y / (ALPHA - (ALPHA - 1) * y)


def rect(x: float) -> float:
    return R / (R + 1) * x + XD / (R + 1)


def strip_line(x: float) -> float:
    yq = rect(ZF)
    slope = (yq - XB) / (ZF - XB)
    return XB + slope * (x - XB)


def op(x: float) -> float:
    return rect(x) if x >= ZF else strip_line(x)


def steps():
    """Staircase vertices from (xD, xD) and the number of stages to reach xB."""
    pts, x, y, n, feed = [(XD, XD)], XD, XD, 0, None
    while x > XB and n < 60:
        x_new = eq_inv(y)
        pts.append((x_new, y))
        n += 1
        if feed is None and x_new < ZF:
            feed = n
        y = op(x_new)
        x = x_new
        pts.append((x, max(y, XB)))
    return pts, n, feed


def diagram() -> Diagram:
    pts, n_stages, feed = steps()
    yq = rect(ZF)
    slope_min = (XD - eq(ZF)) / (XD - ZF)  # rectifying slope at the pinch on the q-line
    r_min = slope_min / (1 - slope_min)
    with Diagram("McCabe-Thiele Diagram, Benzene / Toluene", theme="paper") as d:
        p = Plot(d, x=(0, 1), y=(0, 1), origin=(100.0, 560.0), size=(500.0, 500.0))
        p.grid(xstep=0.1, ystep=0.1)
        p.axes(xlabel="liquid mole fraction benzene $x$", ylabel="vapour mole fraction $y$",
               xstep=0.1, ystep=0.1, through_zero=False)
        p.line((0, 0), (1, 1), stroke=GREY, width=1.2, dash="6,4")
        p.function(eq, 0, 1, stroke=BLUE, width=2.8)
        p.line((XD, rect(XD)), (ZF, yq), stroke=RED, width=2.0)
        p.line((ZF, yq), (XB, XB), stroke=GREEN, width=2.0)
        p.line((ZF, ZF), (ZF, yq), stroke=GREY, width=1.4, dash="3,3")
        p.polyline(pts, stroke=INK, width=1.3)
        # Stage numbers beside the horizontal step of each stage.
        for k in range(n_stages):
            xa, ya = pts[2 * k]
            xb, _ = pts[2 * k + 1]
            if k < n_stages - 1:
                p.label(xb, ya, str(k + 1), dx=-8, dy=-4, anchor="bottom_right", size=11)
            else:  # the last step hugs the axes, so its number goes just below the diagonal
                p.label(xa + 0.02, ya - 0.03, str(k + 1), anchor="left_center", size=11)
        for x, name in ((XB, "$x_B$"), (ZF, "$z_F$"), (XD, "$x_D$")):
            p.vline(x, stroke=GREY, dash="2,3", width=0.8)
            p.label(x, 1.0 if x != XB else 0.95, name, dx=0 if x != XB else 5, dy=-6 if x != XB else 0, anchor="bottom_center" if x != XB else "left_center", size=13)
        p.dot(ZF, yq, radius=4, fill="#FFFFFF", stroke=INK)
        p.label(0.05, 0.78, "equilibrium curve\n$\\alpha$ = 2.5", anchor="left_center", size=13, color=BLUE)
        p.label(0.72, 0.55, "rectifying line\nslope $R/(R+1)$", dx=0, anchor="left_center", size=12, color=RED)
        p.label(0.30, 0.14, "stripping line", dx=-4, dy=34, anchor="left_center", size=12, color=GREEN)
        p.label(ZF, 0.43, "q-line", dx=6, anchor="left_center", size=12, color=GREY)
        p.label(0.62, 0.50, "$y = x$", dx=0, dy=0, anchor="left_center", size=12, color=GREY)
        # Data panel.
        x0 = 650
        d.text(
            "**Design basis**\n"
            f"$x_D$ = {XD:.2f}, $z_F$ = {ZF:.2f}, $x_B$ = {XB:.2f}\n"
            "saturated liquid feed, $q = 1$\n"
            f"reflux ratio $R = {R:g}$\n"
            f"$R_{{\\mathrm{{min}}}} = {r_min:.2f}$, so $R/R_{{\\mathrm{{min}}}} = {R / r_min:.2f}$\n"
            f"rectifying line meets the q-line at $y = {yq:.3f}$\n\n"
            f"**Theoretical stages: {n_stages}**\n"
            f"feed on stage {feed} from the top\n"
            f"(includes the reboiler)",
            size=13, line_height=1.5).at(x0, 110, anchor="top_left")
        d.text(
            "Stage efficiency of about 55 % turns\n"
            f"{n_stages} stages into {math.ceil(n_stages / 0.55)} real trays.",
            size=12, italic=True, font="serif").at(x0, 360, anchor="top_left")
        d.caption("**Figure 9:** McCabe-Thiele construction with stage steps between the equilibrium curve and the operating lines",
                  small_caps=True)
    return d


def build_diagram(output_dir: Path | str = "examples/chemical_engineering") -> Path:
    return render_all(diagram(), output_dir, "09_mccabe_thiele")["svg"]


if __name__ == "__main__":
    dest = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("examples/chemical_engineering")
    build_diagram(dest)
