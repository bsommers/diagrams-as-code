"""Phase portrait of a saddle: x' = x + 2y, y' = 2x + y.

The matrix has eigenvalues 3 and -1 with eigenvectors (1, 1) and (1, -1). Orbits
(RK4, integrated forward and backward in time) come in along the stable
direction, swerve at the origin and leave along the unstable one. Every orbit
but the stable line itself ends up escaping.
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

from diagrams_as_code import Diagram
from diagrams_as_code.output import render_all
from diagrams_as_code.plot import Plot

NAME = "05_saddle"
A = ((1.0, 2.0), (2.0, 1.0))
LIM = 3.0
INK, BLUE, RED, AMBER = "#1F2F57", "#2E6F9E", "#9C2B2B", "#8A5A00"


def field(x: float, y: float) -> tuple[float, float]:
    return A[0][0] * x + A[0][1] * y, A[1][0] * x + A[1][1] * y


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
    with Diagram("Saddle point phase portrait", theme="paper") as diag:
        p = Plot(diag, x=(-LIM, LIM), y=(-LIM, LIM), origin=(190, 440), size=(400, 400))
        p.vector_field(field, nx=11, ny=11, length=13, stroke="#B8C0D2", head=3.0)
        p.axes(xlabel="$x$", ylabel="$y$", xstep=1, ystep=1)
        # Eigen-directions: unstable along (1, 1), stable along (1, -1).
        p.line((-LIM, -LIM), (LIM, LIM), stroke=RED, width=1.6)
        p.line((-LIM, LIM), (LIM, -LIM), stroke=BLUE, width=1.6)
        # Orbits through points on the coordinate axes, followed both ways in time.
        starts = [(k * sx, 0.0) for k in (0.6, 1.3, 2.0) for sx in (1, -1)]
        starts += [(0.0, k * sy) for k in (0.6, 1.3, 2.0) for sy in (1, -1)]
        for st in starts:
            pts = orbit(field, st, t_end=1.6, sign=-1.0)[::-1] + orbit(field, st, t_end=1.6, sign=1.0)
            p.polyline(pts, stroke=INK, width=1.7)
            arrow_on(p, pts, 0.5, INK)
        # Arrowheads on the eigenlines: outward on the unstable, inward on the stable.
        for sgn in (1, -1):
            arrow_on(p, [(sgn * t / 100, sgn * t / 100) for t in range(30, 300)], 0.55, RED)
            arrow_on(p, [(sgn * t / 100, -sgn * t / 100) for t in range(300, 30, -1)], 0.55, BLUE)
        p.dot(0, 0, radius=4.5)
        p.label(LIM, LIM, "$\\lambda = 3$, unstable", size=12, color=RED, anchor="left_center", dx=10)
        p.label(-LIM, LIM, "$\\lambda = -1$, stable", size=12, color=BLUE, anchor="right_center", dx=-10)
        diag.caption(
            "**Figure 5:** Saddle point of $x' = x + 2y$, $y' = 2x + y$; eigenvalues $3$ and $-1$",
            small_caps=True,
        )
    return diag


def build_diagram(output_dir: Path | str = "examples/differential_equations") -> Path:
    return render_all(diagram(), output_dir, NAME)["svg"]


if __name__ == "__main__":
    dest = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("examples/differential_equations")
    build_diagram(dest)
