"""Superposition of two tones of nearby frequency, and the beats they make.

Two unit-amplitude waves $y_1 = \\sin 2\\pi f_1 t$ and $y_2 = \\sin 2\\pi f_2 t$ are
drawn on a shared time axis, with their sum below. The sum is a wave at the mean
frequency inside the envelope $2\\cos(\\pi \\Delta f\\, t)$, so its loudness pulses
$|f_1 - f_2|$ times a second; the beat period is marked on the plot.
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

from diagrams_as_code import Diagram, Style
from diagrams_as_code.output import render_all
from diagrams_as_code.plot import Plot

F1, F2 = 10.0, 12.0
BLUE, RED, INK = "#1F2F57", "#9C2F2F", "#111111"
WIDTH = 720.0
UNIT = 38.0  # px per unit of displacement, same in all three panels


def diagram() -> Diagram:
    df = abs(F2 - F1)
    fm = (F1 + F2) / 2
    beat = 1.0 / df
    with Diagram("Superposition and beats", theme="paper") as diag:
        small, big = 1.3, 2.7
        top = 60.0
        panels = []
        y_bottom = top + 2 * small * UNIT
        specs = [(small, "$y_1$", BLUE, lambda t: math.sin(2 * math.pi * F1 * t)),
                 (small, "$y_2$", RED, lambda t: math.sin(2 * math.pi * F2 * t))]
        for half, label, color, f in specs:
            p = Plot(diag, x=(0, 1), y=(-half, half), origin=(90, y_bottom), size=(WIDTH, 2 * half * UNIT))
            p.grid(xstep=0.1, ystep=1)
            p.axes(xlabel="$t$ (s)", ylabel=label, xstep=0.1, ystep=1, through_zero=False)
            p.function(f, stroke=color, width=1.8, n=600)
            panels.append(p)
            y_bottom += 2 * half * UNIT + 64
        p3 = Plot(diag, x=(0, 1), y=(-big, big), origin=(90, y_bottom + 2 * (big - small) * UNIT), size=(WIDTH, 2 * big * UNIT))
        p3.grid(xstep=0.1, ystep=1)
        p3.axes(xlabel="$t$ (s)", ylabel="$y_1 + y_2$", xstep=0.1, ystep=1, through_zero=False)
        env = lambda t: 2 * abs(math.cos(math.pi * df * t))
        p3.function(env, stroke="#8A5A00", width=1.2, dash="6,4", n=600)
        p3.function(lambda t: -env(t), stroke="#8A5A00", width=1.2, dash="6,4", n=600)
        p3.function(lambda t: math.sin(2 * math.pi * F1 * t) + math.sin(2 * math.pi * F2 * t), stroke="#2E6B3F", width=1.8, n=1200)

        # Beat period between two envelope peaks.
        a, b = p3.px(0, 2.45), p3.px(beat, 2.45)
        diag.connect(a, b, routing="direct", two_way=True, width=0.9, arrow_size=0.6)
        diag.text(f"beat period $T_b = 1/|f_2 - f_1| = {beat:g}$ s", size=12).at((a[0] + b[0]) / 2, a[1] - 6, anchor="bottom_center")
        diag.text("envelope $\\pm 2\\cos(\\pi\\,\\Delta f\\,t)$", size=12, color="#8A5A00").at(
            *p3.px(0.75, -2.0), anchor="top_center")
        diag.text(f"$f_1 = {F1:g}$ Hz", size=12, color=BLUE).at(*panels[0].px(1, 1.1), anchor="bottom_right")
        diag.text(f"$f_2 = {F2:g}$ Hz", size=12, color=RED).at(*panels[1].px(1, 1.1), anchor="bottom_right")
        diag.text(
            f"$y_1 + y_2 = 2\\cos(\\pi\\,\\Delta f\\,t)\\,\\sin(2\\pi f_m t)$ with $f_m = {fm:g}$ Hz, $\\Delta f = {df:g}$ Hz",
            size=13,
        ).at(p3.px(0.5, -big)[0], p3.px(0.5, -big)[1] + 44, anchor="top_center")
        diag.caption("**Figure 7:** Two tones 2 Hz apart add to a wave at the mean frequency whose amplitude beats twice per second",
                     small_caps=True)
    return diag


def build_diagram(output_dir: Path | str = "examples/physics") -> Path:
    return render_all(diagram(), output_dir, "07_superposition_beats")["svg"]


if __name__ == "__main__":
    dest = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("examples/physics")
    build_diagram(dest)
