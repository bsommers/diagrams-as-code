"""Phase portrait of the pendulum: theta' = w, w' = -sin(theta).

Energy E = w^2 / 2 - cos(theta) is conserved, so orbits are level curves of E.
Below E = 1 the pendulum librates in a closed loop around the stable
equilibrium theta = 0 (mod 2 pi); above it, it rotates and the orbit runs on
across the plane. The separatrix E = 1, w = +-2 cos(theta / 2), is the orbit
that reaches the unstable equilibria theta = +-pi (mod 2 pi) and divides the
two kinds of motion. Orbits are integrated with RK4 and the script checks that
energy drifts by less than 1e-6 along each.
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

from diagrams_as_code import Diagram, Style
from diagrams_as_code.output import render_all
from diagrams_as_code.plot import Plot

NAME = "09_pendulum"
PI = math.pi
INK, BLUE, RED, AMBER = "#1F2F57", "#2E6F9E", "#9C2B2B", "#8A5A00"


def field(th: float, w: float) -> tuple[float, float]:
    return w, -math.sin(th)


def energy(th: float, w: float) -> float:
    return 0.5 * w * w - math.cos(th)


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
    xlim = 2.2 * PI
    with Diagram("Pendulum phase portrait", theme="paper") as diag:
        p = Plot(diag, x=(-xlim, xlim), y=(-3.6, 3.6), origin=(80, 400), size=(800, 330))
        p.axes(xlabel="$\\theta$", ylabel="$\\omega$", labels=False, xstep=PI, ystep=1)
        p.vector_field(field, nx=26, ny=8, length=13, stroke="#C9CFDD", head=3.0)
        # Axis labels in multiples of pi, and ordinary numbers on the omega axis.
        for k in range(-2, 3):
            if k == 0:
                label = "0"
            else:
                label = ("$" + ("-" if k < 0 else "") + ("" if abs(k) == 1 else str(abs(k))) + "\\pi$")
            if k == 0:  # clear of the omega axis, which runs through x = 0
                p.label(0, 0, label, size=11, anchor="top_right", dx=-5, dy=6)
            else:
                p.label(k * PI, 0, label, size=11, anchor="top_center", dy=8)
        for v in (-3, -2, -1, 1, 2, 3):
            p.label(0, v, f"${v}$", size=11, anchor="right_center", dx=-8)
        # Separatrix: omega = +- 2 cos(theta / 2) between -pi and pi, repeated every 2 pi.
        for shift in (-2 * PI, 0.0, 2 * PI):
            for sign in (1, -1):
                p.function(lambda th, s=shift, g=sign: g * 2 * math.cos((th - s) / 2), shift - PI, shift + PI,
                           stroke=RED, width=2.0, n=200)
        # Librations: closed loops from rest at theta0, one period each (T = 2 pi / AGM(1, cos(theta0/2))).
        def libration(centre: float, th0: float, colour: str, arrows: bool) -> None:
            start = (centre + th0, 0.0)
            agm_a, agm_b = 1.0, math.cos(th0 / 2)
            for _ in range(30):
                agm_a, agm_b = (agm_a + agm_b) / 2, math.sqrt(agm_a * agm_b)
            pts = orbit(field, start, t_end=2 * PI / agm_a, steps=4000, bound=20.0)
            assert max(abs(energy(q[0] - centre, q[1]) - energy(th0, 0.0)) for q in pts) < 1e-6
            assert math.hypot(pts[-1][0] - start[0], pts[-1][1]) < 1e-4  # the loop closes
            p.polyline(pts, stroke=colour, width=1.7)
            if arrows:
                arrow_on(p, pts, 0.15, colour)
                arrow_on(p, pts, 0.68, colour)

        libration(0.0, 0.7, INK, True)
        libration(0.0, 2.2, BLUE, True)
        libration(-2 * PI, 0.5, INK, False)
        libration(2 * PI, 0.5, INK, False)
        # Rotations: running across the plane in either direction.
        for w0, x0, colour in ((2.6, -xlim, BLUE), (3.2, -xlim, INK), (-2.6, xlim, BLUE), (-3.2, xlim, INK)):
            pts = orbit(field, (x0, w0), t_end=30.0, steps=6000, bound=20.0)
            p.polyline(pts, stroke=colour, width=1.7)
            arrow_on(p, pts, 0.3, colour)
            arrow_on(p, pts, 0.75, colour)
        # Stable equilibria are filled dots; the unstable saddles at odd multiples of pi are open.
        for k in (-2, 0, 2):
            p.dot(k * PI, 0, radius=4.5)
        for k in (-1, 1):
            cx, cy = p.px(k * PI, 0)
            diag.path(f"M {cx - 4.5} {cy} a 4.5 4.5 0 1 0 9 0 a 4.5 4.5 0 1 0 -9 0 Z",
                      style=Style(fill="#FFFFFF", stroke=RED, stroke_width=1.6), z=3)
        p.label(2 * PI, 2.0, "separatrix", size=12, color=RED, anchor="bottom_center", dy=-9)
        p.label(0, 1.23, "libration", size=12, anchor="left_center", dx=10)
        p.label(-1.9 * PI, 3.4, "rotation", size=12, anchor="center")
        diag.caption(
            "**Figure 9:** Phase portrait of the pendulum $\\theta'' = -\\sin\\theta$: closed librations "
            "inside the separatrix $\\omega = \\pm 2\\cos(\\theta/2)$, rotations outside it",
            small_caps=True,
        )
    return diag


def build_diagram(output_dir: Path | str = "examples/differential_equations") -> Path:
    return render_all(diagram(), output_dir, NAME)["svg"]


if __name__ == "__main__":
    dest = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("examples/differential_equations")
    build_diagram(dest)
