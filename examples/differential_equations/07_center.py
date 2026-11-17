"""Phase portrait of a center: the undamped oscillator x' = v, v' = -w^2 x.

With w = 1.5 every orbit is a closed ellipse w^2 x^2 + v^2 = 2E; energy is
conserved, so a neighbouring orbit neither spirals in nor out. Left, RK4
orbits for five energies (each closes after one period 2 pi / w, which the
script checks). Right, x(t) for the middle orbit with its period marked.
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

from diagrams_as_code import Diagram
from diagrams_as_code.output import render_all
from diagrams_as_code.plot import Plot

NAME = "07_center"
W = 1.5
PERIOD = 2 * math.pi / W
INK, BLUE, RED, AMBER = "#1F2F57", "#2E6F9E", "#9C2B2B", "#8A5A00"


def field(x: float, v: float) -> tuple[float, float]:
    return v, -W * W * x


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
    with Diagram("Center phase portrait", theme="paper") as diag:
        p = Plot(diag, x=(-2.5, 2.5), y=(-4, 4), origin=(80, 470), size=(380, 380))
        p.vector_field(field, nx=10, ny=10, length=13, stroke="#B8C0D2", head=3.0)
        p.axes(xlabel="$x$", ylabel="$v$", xstep=1, ystep=1)
        for r, colour in ((0.5, INK), (1.0, BLUE), (1.5, INK), (2.0, BLUE), (2.3, INK)):
            pts = orbit(field, (r, 0.0), t_end=PERIOD, steps=1200)
            assert math.hypot(pts[-1][0] - r, pts[-1][1]) < 1e-5  # closed orbit
            p.polyline(pts, stroke=colour, width=1.8)
            arrow_on(p, pts, 0.07, colour)
            arrow_on(p, pts, 0.57, colour)
        p.dot(0, 0, radius=4.5)
        diag.text("Phase plane  $(x, v)$", size=14).at(270, 50, anchor="bottom_center")

        q = Plot(diag, x=(0, 2 * PERIOD), y=(-2.5, 2.5), origin=(560, 470), size=(400, 380))
        q.grid(xstep=2, ystep=1)
        q.axes(xlabel="$t$", ylabel="$x$", xstep=2, ystep=1)
        pts = orbit(field, (1.5, 0.0), t_end=2 * PERIOD, steps=2400)
        h = 2 * PERIOD / 2400
        series = [(i * h, pt[0]) for i, pt in enumerate(pts)]
        assert max(abs(x - 1.5 * math.cos(W * t)) for t, x in series) < 1e-5
        q.polyline(series, stroke=INK, width=1.9)
        q.vline(PERIOD, stroke=AMBER)
        q.label(PERIOD, -2.5, f"$T = 2\\pi / \\omega = {PERIOD:.2f}$", size=12, color=AMBER,
                anchor="bottom_left", dx=6, dy=-4)
        q.label(0, 1.5, "$x_0$", size=12, anchor="bottom_left", dx=8, dy=-4)
        diag.text("Time series", size=14).at(760, 50, anchor="bottom_center")
        diag.caption(
            "**Figure 7:** A center: the undamped oscillator $x'' = -\\omega^2 x$ conserves energy, so orbits "
            "are closed ellipses (left) and $x(t)$ is periodic (right)",
            small_caps=True,
        )
    return diag


def build_diagram(output_dir: Path | str = "output/differential_equations") -> Path:
    return render_all(diagram(), output_dir, NAME)["svg"]


if __name__ == "__main__":
    dest = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("output/differential_equations")
    build_diagram(dest)
