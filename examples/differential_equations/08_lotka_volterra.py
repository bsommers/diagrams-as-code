"""Lotka-Volterra predator-prey: x' = x (a - b y), y' = y (-c + d x).

Prey x and predators y. The nullclines (x' = 0 on x = 0 and y = a/b; y' = 0 on
y = 0 and x = c/d) cut the plane into four quadrants of different flow
direction and cross at the coexistence equilibrium (c/d, a/b). The orbits are
closed curves around it (RK4, each checked to close within a period-length run),
and the right panel shows the lagged oscillation of both populations.
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

from diagrams_as_code import Diagram
from diagrams_as_code.output import render_all
from diagrams_as_code.plot import Plot

NAME = "08_lotka_volterra"
a, b, c, d = 1.0, 0.5, 1.5, 0.5
EQ = (c / d, a / b)  # (3, 2)
INK, BLUE, RED, AMBER = "#1F2F57", "#2E6F9E", "#9C2B2B", "#8A5A00"


def field(x: float, y: float) -> tuple[float, float]:
    return x * (a - b * y), y * (-c + d * x)


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



def period(start, dt=0.002) -> float:
    """Time for the orbit from ``start`` to return to its starting point's ray, by sampling."""
    x, y = start
    t, prev_side = 0.0, None
    # Second upward crossing of y = a/b.
    crossings = []
    pts = orbit(field, start, t_end=40.0, steps=40000)
    for i in range(1, len(pts)):
        if pts[i - 1][1] < EQ[1] <= pts[i][1] and pts[i][0] > EQ[0] - 1e-9:
            f = (EQ[1] - pts[i - 1][1]) / (pts[i][1] - pts[i - 1][1])
            crossings.append((i - 1 + f) * 40.0 / 40000)
    return crossings[1] - crossings[0] if len(crossings) > 1 else 0.0


def diagram() -> Diagram:
    with Diagram("Lotka-Volterra phase plane", theme="paper") as diag:
        p = Plot(diag, x=(0, 8), y=(0, 6), origin=(80, 470), size=(440, 330))
        p.vector_field(field, nx=11, ny=8, length=13, stroke="#B8C0D2", head=3.0)
        p.axes(xlabel="prey $x$", ylabel="predators $y$", xstep=1, ystep=1)
        # Nullclines: x' = 0 on y = a/b, y' = 0 on x = c/d.
        p.hline(EQ[1], stroke=RED, dash="6,4", width=1.3)
        p.vline(EQ[0], stroke=BLUE, dash="6,4", width=1.3)
        p.label(8, EQ[1], "$x' = 0$", size=12, color=RED, anchor="bottom_right", dx=-6, dy=-4)
        p.label(EQ[0], 6, "$y' = 0$", size=12, color=BLUE, anchor="top_left", dx=6, dy=8)
        for start, colour in (((3.0, 1.2), BLUE), ((3.0, 0.8), INK), ((3.0, 0.5), BLUE)):
            T = period(start)
            pts = orbit(field, start, t_end=T, steps=4000, bound=50.0)
            assert math.hypot(pts[-1][0] - start[0], pts[-1][1] - start[1]) < 2e-2
            p.polyline(pts, stroke=colour, width=1.8)
            arrow_on(p, pts, 0.1, colour)
            arrow_on(p, pts, 0.6, colour)
        p.dot(*EQ, radius=4.5)
        p.label(EQ[0], EQ[1], "$E$", size=12, anchor="bottom_right", dx=-5, dy=-4)
        diag.text("Phase plane", size=14).at(300, 50, anchor="bottom_center")

        # Populations against time for one orbit.
        start = (3.0, 0.8)
        T = period(start)
        q = Plot(diag, x=(0, 2 * T), y=(0, 7), origin=(640, 470), size=(380, 330))
        q.grid(xstep=2, ystep=1)
        q.axes(xlabel="$t$", ylabel="$x, y$", xstep=2, ystep=1)
        n = 3000
        pts = orbit(field, start, t_end=2 * T, steps=n, bound=50.0)
        h = 2 * T / n
        q.polyline([(i * h, pt[0]) for i, pt in enumerate(pts)], stroke=BLUE, width=1.9)
        q.polyline([(i * h, pt[1]) for i, pt in enumerate(pts)], stroke=RED, width=1.9)
        q.label(2 * T, pts[-1][0], "prey", size=12, color=BLUE, anchor="left_center", dx=10, dy=-10)
        q.label(2 * T, pts[-1][1], "predators", size=12, color=RED, anchor="left_center", dx=10, dy=10)
        diag.text("Populations", size=14).at(830, 50, anchor="bottom_center")
        diag.caption(
            "**Figure 8:** Lotka-Volterra predator-prey model: nullclines divide the phase plane, orbits "
            "circle the equilibrium $E = (c/d, a/b)$, and the predators lag the prey",
            small_caps=True,
        )
    return diag


def build_diagram(output_dir: Path | str = "examples/differential_equations") -> Path:
    return render_all(diagram(), output_dir, NAME)["svg"]


if __name__ == "__main__":
    dest = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("examples/differential_equations")
    build_diagram(dest)
