"""Free-body diagram of a block at rest on a rough incline.

Every vector is computed from the incline angle $\\theta$ and the mass $m$:
weight $mg$, its components along and normal to the plane, the normal force
and the static friction that balances the downslope component. Arrow lengths
are proportional to force (3 px per newton).
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

from diagrams_as_code import Diagram, Style
from diagrams_as_code.output import render_all

THETA = math.radians(30.0)
MASS, G = 5.0, 9.81
SCALE = 3.0  # px per newton
INK = "#111111"
BLUE = "#1F2F57"
RED = "#9C2F2F"
GREEN = "#2E6B3F"
FINE = Style(fill="none", stroke="#222222", stroke_width=0.9)


def vec(angle_from_x: float, length: float):
    """Pixel vector (y down) of a given length at an angle measured counter-clockwise from +x."""
    return (length * math.cos(angle_from_x), -length * math.sin(angle_from_x))


def add(p, v, k=1.0):
    return (p[0] + k * v[0], p[1] + k * v[1])


def arrow(diag, p, q, color, width=2.2, dash=False, head="stealth"):
    opts = dict(routing="direct", width=width, color=color, head=head)
    if dash:
        opts["style"] = "dashed"
    diag.connect(p, q, **opts)


def diagram() -> Diagram:
    w = MASS * G
    n = w * math.cos(THETA)
    f = w * math.sin(THETA)  # static friction balances the downslope component
    mu_min = math.tan(THETA)

    foot = (70.0, 420.0)
    run = 560.0
    top = (foot[0] + run, foot[1] - run * math.tan(THETA))
    corner = (top[0], foot[1])
    up = (math.cos(THETA), -math.sin(THETA))      # up the slope (pixels)
    nrm = (-math.sin(THETA), -math.cos(THETA))    # outward normal (pixels)

    side = 90.0
    s0 = 330.0
    base = add(foot, up, s0)
    centre = add(add(base, nrm, side / 2), up, 0)
    corners = [add(base, up, -side / 2), add(base, up, side / 2)]
    block = [corners[0], corners[1], add(corners[1], nrm, side), add(corners[0], nrm, side)]

    with Diagram("Free-body diagram on an incline", theme="paper") as diag:
        # Hatched ground under the plane and the wedge itself.
        diag.polygon([foot, corner, top], style=Style(fill="#EEF0F4", stroke=INK, stroke_width=1.6), z=-2)
        marks = []
        length = math.dist(foot, top)
        for i in range(1, int(length // 14)):
            p = add(foot, up, i * 14.0)
            marks.append(f"M {p[0]:.2f} {p[1]:.2f} L {p[0] - 7:.2f} {p[1] + 9:.2f}")
        diag.path(" ".join(marks), style=FINE)
        diag.polygon(block, style=Style(fill="#DCE6F2", stroke=INK, stroke_width=1.8), z=0)
        diag.point(*centre, dot=True, radius=3)

        # Forces from the block's centre of mass.
        arrow(diag, centre, add(centre, (0, 1), w * SCALE), RED)                       # weight
        arrow(diag, centre, add(centre, nrm, n * SCALE), BLUE)                          # normal
        arrow(diag, centre, add(centre, up, f * SCALE), GREEN)                          # friction
        # Components of the weight, dashed.
        wperp = add(centre, nrm, -n * SCALE)
        wpar = add(centre, up, -f * SCALE)
        arrow(diag, centre, wperp, RED, width=1.2, dash=True)
        arrow(diag, centre, wpar, RED, width=1.2, dash=True)
        w_tip = add(centre, (0, 1), w * SCALE)
        diag.polyline([wperp, w_tip], style=Style(stroke="#888888", stroke_width=0.8, dash="3,3"))
        diag.polyline([wpar, w_tip], style=Style(stroke="#888888", stroke_width=0.8, dash="3,3"))

        def lab(text, p, anchor, size=14, color=INK):
            diag.text(text, size=size, color=color).at(*p, anchor=anchor)

        lab(f"$mg = {w:.1f}\\,\\mathrm{{N}}$", add(w_tip, (1, 0), 12), "left_center", color=RED)
        lab(f"$N = mg\\cos\\theta = {n:.1f}\\,\\mathrm{{N}}$", add(centre, nrm, n * SCALE + 6),
            "bottom_right", color=BLUE)
        lab(f"$f = mg\\sin\\theta = {f:.1f}\\,\\mathrm{{N}}$", add(add(centre, up, f * SCALE + 12), nrm, 22),
            "bottom_left", color=GREEN)
        lab("$mg\\cos\\theta$", add(wperp, nrm, -4), "top_right", size=12, color=RED)
        lab("$mg\\sin\\theta$", add(wpar, up, -4), "top_right", size=12, color=RED)

        # Angle arc at the foot of the incline.
        r = 90.0
        a0 = (foot[0] + r, foot[1])
        a1 = add(foot, up, r)
        diag.path(f"M {a0[0]:.2f} {a0[1]:.2f} A {r} {r} 0 0 0 {a1[0]:.2f} {a1[1]:.2f}", style=FINE)
        lab("$\\theta$", (foot[0] + r + 14, foot[1] - 14), "center", size=15)
        # Axes tilted with the plane.

        diag.text(
            f"$m = {MASS:g}\\,\\mathrm{{kg}}$, $\\theta = {math.degrees(THETA):g}^\\circ$, $g = {G}$ m/s$^2$\n"
            f"At rest: $N = mg\\cos\\theta$ and $f = mg\\sin\\theta$,\n"
            f"so $\\mu_s \\geq \\tan\\theta = {mu_min:.2f}$.",
            size=13,
        ).at(corner[0] + 30, 230, anchor="top_left")
        diag.caption(
            "**Figure 1:** Forces on a block at rest on a rough incline; the weight is resolved along and normal to the plane",
            small_caps=True,
        )
    return diag


def build_diagram(output_dir: Path | str = "output/physics") -> Path:
    return render_all(diagram(), output_dir, "01_free_body_incline")["svg"]


if __name__ == "__main__":
    dest = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("output/physics")
    build_diagram(dest)
