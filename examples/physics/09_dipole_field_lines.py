"""Electric field lines of a dipole, traced numerically.

Charges $+q$ and $-q$ sit at $(\\mp d/2, 0)$. A line starts on a small circle
around the positive charge and is advanced in steps of fixed length along the
local field direction $\\mathbf{E} = \\sum_i q_i (\\mathbf{r} - \\mathbf{r}_i) / |\\mathbf{r} - \\mathbf{r}_i|^3$
with fourth-order Runge-Kutta, until it reaches the negative charge or leaves
the window. Equal angles at the start give a line density that follows the
field strength near each charge.
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

from diagrams_as_code import Diagram, Style
from diagrams_as_code.output import render_all
from diagrams_as_code.plot import Plot

HALF_D = 1.0
CHARGES = [((-HALF_D, 0.0), +1.0), ((HALF_D, 0.0), -1.0)]
XR, YR = 4.4, 3.0
LINES = 24
STEP, START_R, CAPTURE_R = 0.02, 0.16, 0.14
RED, BLUE, INK = "#9C2F2F", "#1F2F57", "#111111"


def field(x: float, y: float):
    ex = ey = 0.0
    for (cx, cy), q in CHARGES:
        dx, dy = x - cx, y - cy
        r3 = (dx * dx + dy * dy) ** 1.5
        ex += q * dx / r3
        ey += q * dy / r3
    return ex, ey


def direction(x: float, y: float):
    ex, ey = field(x, y)
    n = math.hypot(ex, ey)
    return ex / n, ey / n


def trace(start, max_steps: int = 4000):
    """Follow the field from ``start`` until a charge captures the line or it leaves the window."""
    x, y = start
    pts = [(x, y)]
    (nx, ny), _ = CHARGES[1]
    for _ in range(max_steps):
        k1 = direction(x, y)
        k2 = direction(x + STEP / 2 * k1[0], y + STEP / 2 * k1[1])
        k3 = direction(x + STEP / 2 * k2[0], y + STEP / 2 * k2[1])
        k4 = direction(x + STEP * k3[0], y + STEP * k3[1])
        x += STEP / 6 * (k1[0] + 2 * k2[0] + 2 * k3[0] + k4[0])
        y += STEP / 6 * (k1[1] + 2 * k2[1] + 2 * k3[1] + k4[1])
        pts.append((x, y))
        if math.hypot(x - nx, y - ny) < CAPTURE_R or abs(x) > XR or abs(y) > YR:
            break
    return pts


def clip(pts):
    """Cut a traced line at the window edge (linear interpolation on the last step)."""
    out = [pts[0]]
    for a, b in zip(pts, pts[1:]):
        if abs(b[0]) <= XR and abs(b[1]) <= YR:
            out.append(b)
            continue
        t = 1.0
        for lim, p, q in ((XR, a[0], b[0]), (YR, a[1], b[1])):
            if abs(q) > lim:
                t = min(t, (math.copysign(lim, q) - p) / (q - p))
        out.append((a[0] + t * (b[0] - a[0]), a[1] + t * (b[1] - a[1])))
        break
    return out


def diagram() -> Diagram:
    (px_, _), _ = CHARGES[0]
    with Diagram("Electric field lines of a dipole", theme="paper") as diag:
        p = Plot(diag, x=(-XR, XR), y=(-YR, YR), origin=(60, 70 + 2 * YR * 80), size=(2 * XR * 80, 2 * YR * 80))
        p.frame()
        ends_on_neg = 0
        for k in range(LINES):
            a = 2 * math.pi * (k + 0.5) / LINES
            line = clip(trace((px_ + START_R * math.cos(a), START_R * math.sin(a))))
            last = line[-1]
            if math.hypot(last[0] - HALF_D, last[1]) < 2 * CAPTURE_R:
                ends_on_neg += 1
            pix = [p.px(*q) for q in line]
            diag.polyline(pix, style=Style(stroke=INK, stroke_width=1.3))
            # An arrowhead about a third of the way along, pointing downstream.
            i = max(2, len(pix) // 3)
            diag.connect(pix[i - 1], pix[i], routing="direct", width=1.3, head="stealth", arrow_size=0.9, color=INK)

        # Charges and the dipole moment.
        for (cx, cy), q in CHARGES:
            c = p.px(cx, cy)
            r = 13.0
            color = RED if q > 0 else BLUE
            diag.path(f"M {c[0] - r} {c[1]} A {r} {r} 0 1 0 {c[0] + r} {c[1]} A {r} {r} 0 1 0 {c[0] - r} {c[1]} Z",
                      style=Style(fill="#FFFFFF", stroke=color, stroke_width=2.0), z=2)
            sign = f"M {c[0] - 6} {c[1]} h 12" + (f" M {c[0]} {c[1] - 6} v 12" if q > 0 else "")
            diag.path(sign, style=Style(fill="none", stroke=color, stroke_width=2.0), z=3)

        a, b = p.px(2.2, -1.9), p.px(0.8, -1.9)
        diag.connect(a, b, routing="direct", width=2.0, color="#2E6B3F", head="stealth")
        diag.text("$\\mathbf{p}$ points from $-q$ to $+q$", size=12, color="#2E6B3F").at(
            (a[0] + b[0]) / 2, a[1] + 8, anchor="top_center")
        diag.text("$+q$ at $x = -d/2$ (red),  $-q$ at $x = +d/2$ (blue)", size=12).at(*p.px(XR - 0.15, YR - 0.15), anchor="top_right")
        diag.text(
            f"{LINES} lines, equally spaced in angle at the positive charge; {ends_on_neg} end on the negative charge "
            f"inside the window and {LINES - ends_on_neg} leave it (they too return to $-q$, far away).",
            size=12, font="serif", italic=True,
        ).at(p.px(0, -YR)[0], p.px(0, -YR)[1] + 14, anchor="top_center")
        diag.caption("**Figure 9:** Field lines of an electric dipole, traced by integrating the field of two point charges",
                     small_caps=True)
    return diag


def build_diagram(output_dir: Path | str = "examples/physics") -> Path:
    return render_all(diagram(), output_dir, "09_dipole_field_lines")["svg"]


if __name__ == "__main__":
    dest = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("examples/physics")
    build_diagram(dest)
