"""Engineering stress-strain curve of a ductile alloy with the 0.2 % offset yield.

Model: $\\sigma_a(\\varepsilon) = E\\varepsilon / (1 + (E\\varepsilon/\\sigma_s)^m)^{1/m}$ up
to the uniform-elongation strain, then a quadratic necking drop to fracture. The
0.2 % offset yield strength is found by bisection on
$\\sigma(\\varepsilon) = E(\\varepsilon - 0.002)$; the ultimate tensile strength is the
curve maximum. An inset enlarges the first 0.8 % strain to show the construction.
"""
from __future__ import annotations

import sys
from pathlib import Path

from diagrams_as_code import Diagram, Style
from diagrams_as_code.output import render_all
from diagrams_as_code.plot import Plot

E, SIG_S, M = 70_000.0, 330.0, 1.5        # MPa, MPa, curve sharpness
EPS_U, EPS_F, DROP = 0.12, 0.17, 0.15     # uniform strain, fracture strain, fractional drop
RED, BLUE, GREEN, INK = "#9C2F2F", "#1F2F57", "#2E6B3F", "#111111"


def stress(eps: float) -> float:
    r = E * eps
    sa = r / (1.0 + (r / SIG_S) ** M) ** (1.0 / M)
    if eps <= EPS_U:
        return sa
    s_u = stress(EPS_U)
    return s_u - DROP * s_u * ((eps - EPS_U) / (EPS_F - EPS_U)) ** 2


def offset_yield() -> tuple[float, float]:
    lo, hi = 0.002, EPS_U
    for _ in range(80):
        mid = (lo + hi) / 2
        if stress(mid) > E * (mid - 0.002):
            lo = mid
        else:
            hi = mid
    return lo, stress(lo)


def diagram() -> Diagram:
    ey, sy = offset_yield()
    eu = max((i / 2000 * EPS_F for i in range(2001)), key=stress)
    su = stress(eu)
    sf = stress(EPS_F)
    pct = lambda e: 100 * e
    with Diagram("Stress-strain curve", theme="paper") as diag:
        p = Plot(diag, x=(0, 20), y=(0, 400), origin=(100.0, 480.0), size=(560.0, 360.0))
        p.grid(xstep=2, ystep=100)
        p.axes(xlabel="$\\varepsilon$ (%)", ylabel="$\\sigma$ (MPa)", xstep=2, ystep=100, through_zero=False)
        p.polyline([(pct(i / 600 * EPS_F), stress(i / 600 * EPS_F)) for i in range(601)], stroke=BLUE, width=2.6)
        p.dot(pct(ey), sy, radius=4, label=f"yield $\\sigma_y = {sy:.0f}$ MPa", dx=14, dy=22, anchor="top_left", size=13)
        p.dot(pct(eu), su, radius=4, label=f"UTS $\\sigma_u = {su:.0f}$ MPa", dx=-6, dy=-12, anchor="bottom_right", size=13)
        p.dot(pct(EPS_F), sf, radius=4, label="fracture", dx=10, dy=-8, anchor="bottom_left", size=13)
        p.hline(su, stroke="#8A8A8A", dash="3,3", width=0.8)
        p.label(1.0, 40, "elastic", size=12, anchor="left_center", color=GREEN)
        p.label(5.5, 120, "strain hardening", size=12, anchor="left_center", color=INK)
        p.label(14.0, 120, "necking", size=12, anchor="left_center", color=INK)
        p.line((pct(EPS_U), 0), (pct(EPS_U), 400), stroke="#8A8A8A", dash="3,3", width=0.8)
        p.label(pct(EPS_U), 395, "uniform elongation ends", size=11, anchor="right_center", dx=-6)

        # Inset: the 0.2 % offset construction.
        q = Plot(diag, x=(0, 0.8), y=(0, 400), origin=(760.0, 480.0), size=(300.0, 360.0))
        q.frame()
        q.grid(xstep=0.2, ystep=100)
        q.axes(xlabel="$\\varepsilon$ (%)", ylabel="$\\sigma$ (MPa)", xstep=0.2, ystep=100, through_zero=False)
        q.polyline([(pct(i / 400 * 0.008), stress(i / 400 * 0.008)) for i in range(401)], stroke=BLUE, width=2.4)
        q.line((0, 0), (pct(0.0057), E * 0.0057), stroke=GREEN, width=1.2, dash="4,3")
        q.line((0.2, 0), (pct(0.002 + 380 / E), 380), stroke=RED, width=1.6, dash="6,3")
        q.dot(pct(ey), sy, radius=4)
        q.label(0.2, 0, "0.2 % offset", size=12, anchor="top_left", dx=4, dy=26, color=RED)
        q.label(0.40, E * 0.004, "slope $E$", size=12, anchor="right_center", dx=-10, color=GREEN)
        q.label(pct(ey), sy, "$\\sigma_y$", size=13, anchor="top_left", dx=12, dy=10)
        diag.text("**Detail: offset yield**", size=13).at(910.0, 78.0, anchor="center")
        diag.text(f"$E = {E / 1000:.0f}$ GPa, strain offset $0.002$: the line of slope $E$ "
                  f"starting at $\\varepsilon = 0.2\\,\\%$ meets the curve at $\\sigma_y$.", size=12).at(
                      100.0, 590.0, anchor="left_center")
        diag.caption(
            "**Figure 5:** Engineering stress-strain curve with proportional range, 0.2 % offset yield, ultimate strength and fracture",
            small_caps=True,
        )
    return diag


def build_diagram(output_dir: Path | str = "output/engineering") -> Path:
    return render_all(diagram(), output_dir, "05_stress_strain_curve")["svg"]


if __name__ == "__main__":
    dest = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("output/engineering")
    build_diagram(dest)
