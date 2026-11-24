"""A centrifugal pump curve against the system curve: the operating point.

Pump: H = 48 - 4.0e-4 Q^2 (Q in m3/h, H in m of water) with efficiency
eta = 0.78 (1 - ((Q - 240)/240)^2), best efficiency at 240 m3/h. System:
H = 15 + 3.0e-4 Q^2, a 15 m static lift plus friction. The operating point is
where the two heads are equal; closing the discharge valve raises the system
friction coefficient, which slides the point left along the pump curve. Shaft
power follows from P = rho g Q H / eta. Every number on the figure is computed
from these constants.
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

from diagrams_as_code import Diagram, Style
from diagrams_as_code.output import render_all
from diagrams_as_code.plot import Plot

H0, A_P = 48.0, 4.0e-4  # pump shutoff head (m) and curvature
H_ST, K_S = 15.0, 3.0e-4  # system static head (m) and friction coefficient
Q_BEP, ETA_MAX = 240.0, 0.78
Q_THR = 150.0  # throttled flow, m3/h
BLUE, RED, GREEN, GREY, INK = "#1F4E8C", "#A33A3A", "#2E6B3F", "#777777", "#111111"


def pump_head(q: float) -> float:
    return H0 - A_P * q * q


def eta(q: float) -> float:
    return ETA_MAX * (1.0 - ((q - Q_BEP) / Q_BEP) ** 2)


def diagram() -> Diagram:
    q_op = math.sqrt((H0 - H_ST) / (A_P + K_S))
    h_op = pump_head(q_op)
    power = 1000.0 * 9.81 * (q_op / 3600.0) * h_op / eta(q_op) / 1000.0  # kW shaft
    k_thr = (pump_head(Q_THR) - H_ST) / Q_THR ** 2
    h_thr = pump_head(Q_THR)
    eta_scale = 60.0 / 0.9  # efficiency 0.9 maps to the top of the head axis

    with Diagram("Pump Curve against System Curve", theme="paper") as diag:
        p = Plot(diag, x=(0, 300), y=(0, 60), origin=(110.0, 500.0), size=(600.0, 380.0))
        p.grid(xstep=50, ystep=10)
        p.axes(xlabel="flow $Q$ (m$^3$/h)", ylabel="head $H$ (m)", xstep=50, ystep=10, through_zero=False)
        # Efficiency on a secondary scale drawn on the right.
        p.function(lambda q: eta(q) * eta_scale, 0, 300, stroke=GREEN, width=1.8, dash="6,4")
        for e in (20, 40, 60, 80):
            p.label(300, e / 100.0 * eta_scale, f"{e}", dx=8, size=11, color=GREEN)
        p.label(300, 60, "$\\eta$ (%)", dx=8, dy=-14, anchor="left_center", size=12, color=GREEN)
        # Curves.
        p.function(pump_head, 0, 300, stroke=BLUE, width=2.8)
        p.function(lambda q: H_ST + K_S * q * q, 0, 300, stroke=RED, width=2.8)
        p.function(lambda q: H_ST + k_thr * q * q, 0, 300, stroke=RED, width=1.8, dash="6,4")
        p.label(10, pump_head(10), "pump curve", dx=10, dy=-16, anchor="bottom_left", size=13, color=BLUE)
        p.label(280, H_ST + K_S * 280 ** 2, "system curve", dx=-4, dy=-10, anchor="bottom_right", size=13, color=RED)
        p.label(192, 56.5, "valve throttled", dx=-4, dy=0, anchor="right_center", size=12, color=RED)
        # Operating points.
        p.vline(q_op, stroke=GREY, dash="3,3", width=0.8)
        p.hline(h_op, stroke=GREY, dash="3,3", width=0.8)
        p.dot(q_op, h_op, radius=5, label="A", dx=10, dy=-6, anchor="bottom_left", size=14)
        p.label(222, 9, f"A: operating point\n$Q$ = {q_op:.0f} m$^3$/h, $H$ = {h_op:.1f} m", anchor="left_center", size=12)
        p.dot(Q_THR, h_thr, radius=4, fill="#FFFFFF", stroke=RED)
        p.label(Q_THR, h_thr, "B", dx=-8, dy=-6, anchor="bottom_right", size=14, color=RED)
        p.dot(Q_BEP, eta(Q_BEP) * eta_scale, radius=4, fill="#FFFFFF", stroke=GREEN)
        p.label(Q_BEP, eta(Q_BEP) * eta_scale, f"BEP, $\\eta$ = {ETA_MAX:.0%}", dy=14, anchor="top_center",
                size=12, color=GREEN)
        p.label(0, H_ST, "static head", dx=8, dy=-8, anchor="bottom_left", size=11, color=RED)
        diag.text(
            f"Pump $H = {H0:g} - {A_P * 1e4:g}\\times 10^{{-4}}\\,Q^2$     System $H = {H_ST:g} + {K_S * 1e4:g}\\times 10^{{-4}}\\,Q^2$     "
            f"Throttled $k = {k_thr * 1e4:.1f}\\times 10^{{-4}}$",
            size=13).at(110, 570, anchor="top_left")
        diag.text(
            f"At A $\\eta$ = {eta(q_op):.1%}; hydraulic power $\\rho g Q H$ = {power * eta(q_op):.1f} kW, "
            f"shaft power = {power:.1f} kW.   Throttling to B ({Q_THR:g} m$^3$/h, {h_thr:.1f} m) burns "
            f"{h_thr - (H_ST + K_S * Q_THR ** 2):.1f} m of head across the valve.",
            size=12, font="serif", italic=True).at(110, 600, anchor="top_left")
        diag.caption("**Figure 8:** Pump characteristic and system curve with the operating point and the effect of throttling",
                     small_caps=True)
    return diag


def build_diagram(output_dir: Path | str = "examples/chemical_engineering") -> Path:
    return render_all(diagram(), output_dir, "08_pump_system_curve")["svg"]


if __name__ == "__main__":
    dest = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("examples/chemical_engineering")
    build_diagram(dest)
