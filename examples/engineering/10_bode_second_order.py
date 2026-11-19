"""Bode magnitude and phase of a second-order low-pass system.

$H(j\\omega) = \\omega_n^2 / (\\omega_n^2 - \\omega^2 + 2j\\zeta\\omega_n\\omega)$ with
$\\omega_n = 10$ rad/s and four damping ratios. Magnitude is
$20\\log_{10}|H|$ in dB and phase is $-\\mathrm{atan2}(2\\zeta\\omega_n\\omega, \\omega_n^2 - \\omega^2)$.
The resonant peak is $M_r = 1/(2\\zeta\\sqrt{1-\\zeta^2})$ at
$\\omega_r = \\omega_n\\sqrt{1-2\\zeta^2}$ for $\\zeta < 1/\\sqrt{2}$. The high-frequency
asymptote falls at 40 dB per decade.
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

from diagrams_as_code import Diagram, Style
from diagrams_as_code.output import render_all
from diagrams_as_code.plot import Plot

WN = 10.0
ZETAS = [(0.1, "#9C2F2F"), (0.3, "#8A5A00"), (0.7, "#2E6B3F"), (1.0, "#1F2F57")]


def mag_db(w: float, z: float) -> float:
    re, im = WN ** 2 - w ** 2, 2 * z * WN * w
    return 20 * math.log10(WN ** 2 / math.hypot(re, im))


def phase_deg(w: float, z: float) -> float:
    return -math.degrees(math.atan2(2 * z * WN * w, WN ** 2 - w ** 2))


def diagram() -> Diagram:
    with Diagram("Bode plot", theme="paper") as diag:
        m = Plot(diag, x=(0.1, 100.0), y=(-60, 30), origin=(120.0, 330.0), size=(560.0, 240.0), xscale="log")
        m.grid(ystep=20)
        m.axes(xlabel="$\\omega$ (rad/s)", ylabel="$|H|$ (dB)", ystep=20, through_zero=False, xlabels=False)
        m.hline(0.0, stroke="#8A8A8A", dash="3,3", width=0.8)
        m.vline(WN, stroke="#8A8A8A", dash="3,3", width=0.8)
        # Asymptotes: 0 dB, then -40 dB/decade beyond the corner.
        m.polyline([(0.1, 0.0), (WN, 0.0), (100.0, -80.0)], stroke="#555555", dash="6,3", width=1.0)
        for z, col in ZETAS:
            m.function(lambda w, z=z: mag_db(w, z), 0.1, 100.0, stroke=col, width=2.2)
        z0 = ZETAS[0][0]
        wr = WN * math.sqrt(1 - 2 * z0 ** 2)
        mr = 1 / (2 * z0 * math.sqrt(1 - z0 ** 2))
        m.dot(wr, 20 * math.log10(mr), radius=3.5, label=f"$M_r = {20 * math.log10(mr):.1f}$ dB at $\\omega_r = {wr:.1f}$",
              dx=10, dy=-2, anchor="bottom_left", size=12)
        m.label(25.0, -50.0, "$-40$ dB/dec", size=12, anchor="right_center", color="#555555")

        p = Plot(diag, x=(0.1, 100.0), y=(-200, 10), origin=(120.0, 640.0), size=(560.0, 240.0), xscale="log")
        p.grid(ystep=45)
        p.axes(xlabel="$\\omega$ (rad/s)", ylabel="$\\angle H$ ($^\\circ$)", ystep=45, through_zero=False)
        p.hline(-90.0, stroke="#8A8A8A", dash="3,3", width=0.8)
        p.vline(WN, stroke="#8A8A8A", dash="3,3", width=0.8)
        for z, col in ZETAS:
            p.function(lambda w, z=z: phase_deg(w, z), 0.1, 100.0, stroke=col, width=2.2)
        p.label(WN, -90.0, "$-90^\\circ$ at $\\omega_n$", size=12, anchor="left_center", dx=8, dy=-14)
        m.legend([(f"$\\zeta = {z:g}$", col, "") for z, col in ZETAS], at=(730.0, 120.0), size=13)
        diag.text(f"$\\omega_n = {WN:g}$ rad/s\n$M_r = 1/(2\\zeta\\sqrt{{1-\\zeta^2}})$\n"
                  f"$\\omega_r = \\omega_n\\sqrt{{1-2\\zeta^2}}$", size=13).at(730.0, 230.0, anchor="top_left")
        diag.caption(
            "**Figure 10:** Bode magnitude and phase of a second-order system for four damping ratios",
            small_caps=True,
        )
    return diag


def build_diagram(output_dir: Path | str = "examples/engineering") -> Path:
    return render_all(diagram(), output_dir, "10_bode_second_order")["svg"]


if __name__ == "__main__":
    dest = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("examples/engineering")
    build_diagram(dest)
