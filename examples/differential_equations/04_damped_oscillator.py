"""Damped spring-mass oscillator: x'' + 2 zeta w0 x' + w0^2 x = 0.

Three RK4 solutions of the same system from x(0) = 1, x'(0) = 0 with damping
ratio zeta = 0.2 (underdamped), 1 (critically damped) and 2 (overdamped). The
underdamped curve rings inside the envelope e^{-zeta w0 t}; the other two
return to rest without crossing zero. The script checks the underdamped curve
against its closed form.
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

from diagrams_as_code import Diagram
from diagrams_as_code.output import render_all
from diagrams_as_code.plot import Plot

NAME = "04_damped_oscillator"
W0 = 3.0
INK, BLUE, RED, AMBER = "#1F2F57", "#2E6F9E", "#9C2B2B", "#8A5A00"


def solve(zeta: float, t_end: float, steps: int = 1200) -> list[tuple[float, float]]:
    """RK4 for x' = v, v' = -2 zeta w0 v - w0^2 x from (1, 0)."""
    def g(x: float, v: float) -> tuple[float, float]:
        return v, -2 * zeta * W0 * v - W0 * W0 * x

    h = t_end / steps
    x, v = 1.0, 0.0
    out = [(0.0, x)]
    for i in range(steps):
        k1 = g(x, v)
        k2 = g(x + h / 2 * k1[0], v + h / 2 * k1[1])
        k3 = g(x + h / 2 * k2[0], v + h / 2 * k2[1])
        k4 = g(x + h * k3[0], v + h * k3[1])
        x += h / 6 * (k1[0] + 2 * k2[0] + 2 * k3[0] + k4[0])
        v += h / 6 * (k1[1] + 2 * k2[1] + 2 * k3[1] + k4[1])
        out.append(((i + 1) * h, x))
    return out


def diagram() -> Diagram:
    t_end = 4.0
    with Diagram("Damped spring-mass oscillator", theme="paper") as diag:
        p = Plot(diag, x=(0, t_end), y=(-0.6, 1.1), origin=(90, 360), size=(600, 300))
        p.grid(xstep=1, ystep=0.5)
        p.axes(xlabel="$t$", ylabel="$x$", xstep=1, ystep=0.5)
        zeta = 0.2
        wd = W0 * math.sqrt(1 - zeta**2)
        under = solve(zeta, t_end)
        closed = lambda t: math.exp(-zeta * W0 * t) * (math.cos(wd * t) + zeta * W0 / wd * math.sin(wd * t))
        assert max(abs(x - closed(t)) for t, x in under) < 1e-6
        env = lambda t: math.exp(-zeta * W0 * t)
        p.function(env, stroke="#7C8AA8", dash="5,4", width=1.1)
        p.function(lambda t: -env(t), stroke="#7C8AA8", dash="5,4", width=1.1)
        p.polyline(under, stroke=INK, width=2.0)
        p.polyline(solve(1.0, t_end), stroke=RED, width=2.0)
        p.polyline(solve(2.0, t_end), stroke=BLUE, width=2.0)
        # A legend in the empty upper right of the window.
        entries = [
            (INK, "", "$\\zeta = 0.2$  underdamped"),
            (RED, "", "$\\zeta = 1$  critically damped"),
            (BLUE, "", "$\\zeta = 2$  overdamped"),
            ("#7C8AA8", "5,4", "envelope $\\pm e^{-\\zeta \\omega_0 t}$"),
        ]
        for i, (colour, dash, text) in enumerate(entries):
            y = 1.0 - 0.15 * i
            p.line((2.0, y), (2.35, y), stroke=colour, width=2.0, dash=dash)
            p.label(2.35, y, text, size=12, anchor="left_center", dx=8)
        # The model, to the right of the plot.
        diag.text("**Model**", size=14, align="left").at(760, 130, anchor="top_left")
        diag.text("$m x'' + c x' + k x = 0$", size=13).at(760, 165, anchor="top_left")
        diag.text("$\\omega_0^2 = k / m,\\quad \\zeta = c / (2 m \\omega_0)$", size=13).at(760, 198, anchor="top_left")
        diag.text(r"$\omega_0 = 3,\; x(0) = 1,\; x'(0) = 0$", size=13).at(760, 231, anchor="top_left")
        diag.text("$\\zeta < 1$: rings at $\\omega_d = \\omega_0 (1 - \\zeta^2)^{1/2}$", size=12).at(760, 280, anchor="top_left")
        diag.text("$\\zeta = 1$: fastest return without overshoot", size=12).at(760, 308, anchor="top_left")
        diag.text("$\\zeta > 1$: slow creep back to rest", size=12).at(760, 336, anchor="top_left")
        diag.caption(
            "**Figure 4:** Spring-mass oscillator with damping ratio $\\zeta = 0.2$, $1$ and $2$: "
            "the underdamped solution rings inside its exponential envelope",
            small_caps=True,
        )
    return diag


def build_diagram(output_dir: Path | str = "examples/differential_equations") -> Path:
    return render_all(diagram(), output_dir, NAME)["svg"]


if __name__ == "__main__":
    dest = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("examples/differential_equations")
    build_diagram(dest)
