"""A unity-feedback control loop and its closed-loop step response.

Plant $G(s) = \\omega_n^2 / (s(s + 2\\zeta\\omega_n))$ with $\\omega_n = 4$ rad/s and
$\\zeta = 0.4$ gives the closed loop $T(s) = \\omega_n^2/(s^2 + 2\\zeta\\omega_n s + \\omega_n^2)$.
The step response is the analytic underdamped result
$y(t) = 1 - e^{-\\zeta\\omega_n t}\\sin(\\omega_d t + \\arccos\\zeta)/\\sqrt{1-\\zeta^2}$;
overshoot, peak time and settling time are computed from the same parameters.
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

from diagrams_as_code import Diagram, Style
from diagrams_as_code.output import render_all
from diagrams_as_code.plot import Plot

WN, ZETA = 4.0, 0.4
RED, BLUE, GREEN, INK = "#9C2F2F", "#1F2F57", "#2E6B3F", "#111111"


def step(t: float) -> float:
    wd = WN * math.sqrt(1 - ZETA ** 2)
    return 1 - math.exp(-ZETA * WN * t) / math.sqrt(1 - ZETA ** 2) * math.sin(wd * t + math.acos(ZETA))


def box(diag, x, y, w, h, text, fill="#DCE6F2"):
    diag.polygon([(x, y), (x + w, y), (x + w, y + h), (x, y + h)],
                 style=Style(fill=fill, stroke=INK, stroke_width=1.6), z=1)
    if isinstance(text, tuple):      # numerator / denominator drawn by hand (math markup has no fractions)
        num, den = text
        cx, cy = x + w / 2, y + h / 2
        diag.text(num, size=15, z=3).at(cx, cy - 4, anchor="bottom_center")
        diag.path(f"M {x + 18:.1f} {cy:.1f} L {x + w - 18:.1f} {cy:.1f}", style=Style(fill="none", stroke=INK, stroke_width=1.2), z=3)
        diag.text(den, size=15, z=3).at(cx, cy + 4, anchor="top_center")
        return
    diag.text(text, size=15, z=3).at(x + w / 2, y + h / 2, anchor="center")


def arrow(diag, p, q, color=INK):
    diag.connect(p, q, routing="direct", width=1.8, color=color, head="stealth")


def diagram() -> Diagram:
    wd = WN * math.sqrt(1 - ZETA ** 2)
    mp = math.exp(-math.pi * ZETA / math.sqrt(1 - ZETA ** 2))
    tp = math.pi / wd
    ts = 4 / (ZETA * WN)
    with Diagram("Feedback loop and step response", theme="paper") as diag:
        # Block diagram: R -> (+) -> G(s) -> Y, unity feedback.
        cy = 150.0
        sx, sr = 190.0, 16.0
        diag.polygon([(sx + sr * math.cos(2 * math.pi * i / 24), cy + sr * math.sin(2 * math.pi * i / 24)) for i in range(24)],
                     style=Style(fill="#FFFFFF", stroke=INK, stroke_width=1.6), z=1)
        diag.path(f"M {sx - 8:.1f} {cy - 8:.1f} L {sx + 8:.1f} {cy + 8:.1f} M {sx - 8:.1f} {cy + 8:.1f} L {sx + 8:.1f} {cy - 8:.1f}",
                  style=Style(fill="none", stroke=INK, stroke_width=1.0), z=2)
        diag.text("$+$", size=12).at(sx - 24, cy - 14, anchor="center")
        diag.text("$-$", size=14).at(sx - 8, cy + 30, anchor="center")
        gx, gw, gh = 300.0, 190.0, 60.0
        box(diag, gx, cy - gh / 2, gw, gh, ("$\\omega_n^2$", "$s\\,(s + 2\\zeta\\omega_n)$"))
        arrow(diag, (90, cy), (sx - sr, cy))
        diag.text("$R(s)$", size=15).at(70, cy, anchor="right_center")
        diag.text("$E(s)$", size=14).at((sx + sr + gx) / 2, cy - 14, anchor="bottom_center")
        arrow(diag, (sx + sr, cy), (gx, cy))
        arrow(diag, (gx + gw, cy), (gx + gw + 90, cy))
        diag.text("$Y(s)$", size=15).at(gx + gw + 98, cy, anchor="left_center")
        # Feedback path.
        fx = gx + gw + 45
        fy = cy + 70
        diag.polyline([(fx, cy), (fx, fy), (sx, fy)], style=Style(fill="none", stroke=INK, stroke_width=1.8), z=0)
        arrow(diag, (sx, fy), (sx, cy + sr))
        diag.polygon([(fx - 3.5, cy - 3.5), (fx + 3.5, cy - 3.5), (fx + 3.5, cy + 3.5), (fx - 3.5, cy + 3.5)],
                     style=Style(fill=INK, stroke=INK, stroke_width=1.0), z=2)
        diag.text("unity feedback", size=12).at((sx + fx) / 2, fy + 12, anchor="top_center")

        # Step response.
        p = Plot(diag, x=(0, 4), y=(0, 1.5), origin=(140.0, 560.0), size=(560.0, 280.0))
        p.grid(xstep=0.5, ystep=0.25)
        p.axes(xlabel="$t$ (s)", ylabel="$y(t)$", xstep=0.5, ystep=0.25, through_zero=False)
        p.area(lambda t: 1.02, 0, 4, g=lambda t: 0.98, fill="#E3EDE3", opacity=0.9)
        p.hline(1.0, stroke="#8A8A8A", dash="5,4", width=1.0)
        p.function(step, 0, 4, stroke=BLUE, width=2.6)
        ymax = step(tp)
        p.dot(tp, ymax, radius=4, label=f"$M_p = {mp * 100:.1f}\\,\\%$ at $t_p = {tp:.2f}$ s", dx=12, dy=-6,
              anchor="bottom_left", size=13)
        p.vline(tp, stroke="#8A8A8A", dash="3,3", width=0.8)
        p.dot(ts, step(ts), radius=3.5, fill="#FFFFFF", stroke=GREEN)
        p.label(ts, 0.98, f"$t_s \\approx 4/\\zeta\\omega_n = {ts:.2f}$ s (2 %)", dx=10, dy=40, anchor="top_left", size=12, color=GREEN)
        p.vline(ts, stroke=GREEN, dash="3,3", width=0.8)
        p.label(0.02, 1.05, "$y_{ss} = 1$", dx=6, dy=-8, anchor="bottom_left", size=12)
        diag.text(f"$\\omega_n = {WN:g}$ rad/s, $\\zeta = {ZETA:g}$, $\\omega_d = \\omega_n\\sqrt{{1-\\zeta^2}} = {wd:.2f}$ rad/s",
                  size=13).at(140.0, 640.0, anchor="left_center")
        diag.caption(
            "**Figure 9:** Unity-feedback loop and its underdamped closed-loop step response with overshoot and settling time",
            small_caps=True,
        )
    return diag


def build_diagram(output_dir: Path | str = "output/engineering") -> Path:
    return render_all(diagram(), output_dir, "09_feedback_step_response")["svg"]


if __name__ == "__main__":
    dest = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("output/engineering")
    build_diagram(dest)
