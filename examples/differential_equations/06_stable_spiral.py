"""Phase portrait of a stable spiral: x' = -0.25 x + y, y' = -x - 0.25 y.

Eigenvalues -0.25 +- i: every orbit winds around the origin while its radius
shrinks like e^{-0.25 t}. Left, five RK4 orbits in the phase plane; right, the
time series x(t) of one of them, decaying inside the envelope r0 e^{-0.25 t}.
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

from diagrams_as_code import Diagram
from diagrams_as_code.output import render_all
from diagrams_as_code.plot import Plot

NAME = "06_stable_spiral"
SIGMA = 0.25
INK, BLUE, RED, AMBER = "#1F2F57", "#2E6F9E", "#9C2B2B", "#8A5A00"


def field(x: float, y: float) -> tuple[float, float]:
    return -SIGMA * x + y, -x - SIGMA * y


def orbit(f, start, t_end=3.0, steps=900, sign=1.0, bound=9.0):
    """RK4 orbit of x' = sign * f(x), stopping once it is far outside the window."""
    h = sign * t_end / steps
    x, y = start
    out = [(x, y)]
    for _ in range(steps):
        k1 = f(x, y)
        k2 = f(x + h / 2 * k1[0], y + h / 2 * k1[1])
        k3 = f(x + h / 2 * k2[0], y + h / 2 * k2[1])
        k4 = f(x + h * k3[0], y + h * k3[1])
        x += h / 6 * (k1[0] + 2 * k2[0] + 2 * k3[0] + k4[0])
        y += h / 6 * (k1[1] + 2 * k2[1] + 2 * k3[1] + k4[1])
        out.append((x, y))
        if abs(x) > bound or abs(y) > bound:
            break
    return out


def arrow_on(p: Plot, pts, frac: float, colour: str, length: float = 12.0, reverse: bool = False) -> None:
    """An arrowhead on the visible part of ``pts``, ``frac`` of the way along it (pixel arc length)."""
    vis = [q for q in pts if p.inside(q)]
    if len(vis) < 3:
        return
    px = [p.px(*q) for q in vis]
    cum = [0.0]
    for a, b in zip(px, px[1:]):
        cum.append(cum[-1] + math.hypot(b[0] - a[0], b[1] - a[1]))
    target = frac * cum[-1]
    i = next(k for k, c in enumerate(cum) if c >= target)
    i = min(max(i, 1), len(px) - 2)
    j = i
    while j < len(px) - 1 and math.hypot(px[j][0] - px[i][0], px[j][1] - px[i][1]) < length:
        j += 1
    a, b = px[i], px[j]
    if reverse:
        a, b = b, a
    p.d.connect(a, b, routing="direct", width=1.8, color=colour, head="stealth", arrow_size=0.9)



def diagram() -> Diagram:
    with Diagram("Stable spiral phase portrait", theme="paper") as diag:
        p = Plot(diag, x=(-3, 3), y=(-3, 3), origin=(80, 470), size=(380, 380))
        p.vector_field(field, nx=11, ny=11, length=13, stroke="#B8C0D2", head=3.0)
        p.axes(xlabel="$x$", ylabel="$y$", xstep=1, ystep=1)
        for start, colour in (((2.6, 0.0), INK), ((-2.0, 1.2), BLUE), ((0.0, -2.8), INK), ((-1.0, -0.8), BLUE)):
            pts = orbit(field, start, t_end=22.0, steps=2200)
            p.polyline(pts, stroke=colour, width=1.8)
            arrow_on(p, pts, 0.12, colour)
            p.dot(*start, radius=3)
        p.dot(0, 0, radius=4.5)
        diag.text("Phase plane", size=14).at(270, 50, anchor="bottom_center")

        # Time series of x for the orbit from (2.6, 0): r0 e^{-sigma t} cos t.
        q = Plot(diag, x=(0, 16), y=(-3, 3), origin=(560, 470), size=(400, 380))
        q.grid(xstep=4, ystep=1)
        q.axes(xlabel="$t$", ylabel="$x$", xstep=4, ystep=1)
        pts = orbit(field, (2.6, 0.0), t_end=16.0, steps=1600)
        h = 16.0 / 1600
        series = [(i * h, pt[0]) for i, pt in enumerate(pts)]
        assert max(abs(x - 2.6 * math.exp(-SIGMA * t) * math.cos(t)) for t, x in series) < 1e-5
        env = lambda t: 2.6 * math.exp(-SIGMA * t)
        q.function(env, stroke="#7C8AA8", dash="5,4", width=1.1)
        q.function(lambda t: -env(t), stroke="#7C8AA8", dash="5,4", width=1.1)
        q.polyline(series, stroke=INK, width=1.9)
        q.label(5.0, env(5.0), "$\\pm r_0 e^{-t/4}$", size=12, color="#5A6A88", anchor="bottom_left", dx=4, dy=-6)
        diag.text("Time series", size=14).at(760, 50, anchor="bottom_center")
        diag.caption(
            "**Figure 6:** Stable spiral, eigenvalues $-0.25 \\pm i$: orbits wind inward to the origin "
            "(left) and $x(t)$ is a decaying oscillation (right)",
            small_caps=True,
        )
    return diag


def build_diagram(output_dir: Path | str = "examples/differential_equations") -> Path:
    return render_all(diagram(), output_dir, NAME)["svg"]


if __name__ == "__main__":
    dest = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("examples/differential_equations")
    build_diagram(dest)
