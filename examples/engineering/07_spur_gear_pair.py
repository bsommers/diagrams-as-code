"""A spur gear pair: pitch circles, tooth counts, speed ratio and centre distance.

Module $m = 4$ mm, $N_1 = 20$ and $N_2 = 40$ teeth. Pitch diameter $d = mN$,
addendum $m$, dedendum $1.25m$, centre distance $C = (d_1 + d_2)/2 = 120$ mm and
speed ratio $\\omega_1/\\omega_2 = N_2/N_1$. Drawn at 2 px per mm; teeth are
trapezoids and the two gears are phased so a tooth of one meets a gap of the other.
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

from diagrams_as_code import Diagram, Style
from diagrams_as_code.draft import Draft
from diagrams_as_code.output import render_all

MOD, N1, N2, K = 4.0, 20, 40, 2.0
INK, BLUE, RED = "#1F2F57", "#1F2F57", "#9C2F2F"


def gear_outline(cx, cy, n, mod, phase):
    """Closed polygon of a trapezoidal-tooth gear; a tooth is centred at angle ``phase``."""
    rp = mod * n / 2 * K
    ra, rf = rp + mod * K, rp - 1.25 * mod * K
    step = 2 * math.pi / n
    pts = []
    for i in range(n):
        t = phase + i * step
        for frac, rad in ((-0.50, rf), (-0.26, rf), (-0.14, ra), (0.14, ra), (0.26, rf), (0.50, rf)):
            a = t + frac * step
            pts.append((cx + rad * math.cos(a), cy - rad * math.sin(a)))
    return pts


def circle(cx, cy, r, n=72):
    return [(cx + r * math.cos(2 * math.pi * i / n), cy - r * math.sin(2 * math.pi * i / n)) for i in range(n)]


def diagram() -> Diagram:
    c = (MOD * N1 / 2 + MOD * N2 / 2)           # centre distance, mm
    r1, r2 = MOD * N1 / 2 * K, MOD * N2 / 2 * K
    c1 = (190.0, 360.0)
    c2 = (c1[0] + c * K, c1[1])
    ratio = N2 / N1
    with Diagram("Spur gear pair", theme="paper") as diag:
        k = Draft(diag, size=13)
        # Gear 1 has a tooth at angle 0 (toward gear 2); gear 2 has a gap at angle pi.
        g1 = gear_outline(*c1, N1, MOD, 0.0)
        g2 = gear_outline(*c2, N2, MOD, math.pi + math.pi / N2)
        diag.polygon(g1, style=Style(fill="#DCE6F2", stroke=INK, stroke_width=1.6), z=0)
        diag.polygon(g2, style=Style(fill="#F0E4D6", stroke=INK, stroke_width=1.6), z=0)
        for cc, dia in ((c1, 24.0), (c2, 32.0)):
            diag.polygon(circle(*cc, dia, 36), style=Style(fill="#FFFFFF", stroke=INK, stroke_width=1.4), z=2)
        # Pitch circles (dashed), tangent at the pitch point.
        for cc, r in ((c1, r1), (c2, r2)):
            diag.polygon(circle(*cc, r, 120), style=Style(fill="none", stroke=RED, stroke_width=1.1, dash="6,3"), z=3)
        for cc, r in ((c1, r1), (c2, r2)):
            k.centerline((cc[0] - r - 40, cc[1]), (cc[0] + r + 40, cc[1]) if cc is c1 else (cc[0] + r + 40, cc[1]))
            k.centerline((cc[0], cc[1] - r - 40), (cc[0], cc[1] + r + 40))
        pp = (c1[0] + r1, c1[1])
        diag.polygon(circle(*pp, 3.5, 12), style=Style(fill=RED, stroke=RED, stroke_width=1.0), z=4)
        k.leader(pp, (pp[0], c1[1] - r1 - 52), "pitch point", anchor="bottom_center", dot=False)

        # Rotation arrows: an arc outside each gear with an arrowhead.
        def spin(cc, r, ccw):
            a0, a1 = (math.radians(60), math.radians(125)) if ccw else (math.radians(120), math.radians(55))
            pts = [(cc[0] + r * math.cos(a0 + (a1 - a0) * i / 20), cc[1] - r * math.sin(a0 + (a1 - a0) * i / 20))
                   for i in range(21)]
            diag.polyline(pts, style=Style(fill="none", stroke=BLUE, stroke_width=2.0), z=3)
            tx, ty = pts[-1]
            ux, uy = tx - pts[-4][0], ty - pts[-4][1]
            n = math.hypot(ux, uy)
            ux, uy = ux / n, uy / n
            head = [(tx + ux * 9, ty + uy * 9), (tx - uy * 5, ty + ux * 5), (tx + uy * 5, ty - ux * 5)]
            diag.polygon(head, style=Style(fill=BLUE, stroke=BLUE, stroke_width=1.0), z=3)
        spin(c1, r1 + 26, True)
        spin(c2, r2 + 26, False)
        diag.text("$\\omega_1$", size=15, color=BLUE).at(c1[0] + 4, c1[1] - r1 - 44, anchor="bottom_center")
        diag.text("$\\omega_2$", size=15, color=BLUE).at(c2[0] + 4, c2[1] - r2 - 44, anchor="bottom_center")
        diag.text(f"**Pinion**, $N_1 = {N1}$, $d_1 = mN_1 = {MOD * N1:g}$ mm", size=13).at(
            c1[0], c1[1] + r1 + 56, anchor="top_center")
        diag.text(f"**Gear**, $N_2 = {N2}$, $d_2 = mN_2 = {MOD * N2:g}$ mm", size=13).at(
            c2[0] + 18, c2[1] + r2 + 60, anchor="top_left")
        # Centre distance, with its extension lines drawn through both centres.
        yd = c1[1] + r2 + 100
        for cc in (c1, c2):
            diag.path(f"M {cc[0]:.1f} {cc[1] + r2 + 46:.1f} L {cc[0]:.1f} {yd + 4:.1f}",
                      style=Style(fill="none", stroke=INK, stroke_width=0.7))
        k.dimension((c1[0], yd), (c2[0], yd), f"$C = (d_1 + d_2)/2 = {c:g}$ mm", offset=0)
        diag.text(f"Speed ratio $\\omega_1/\\omega_2 = N_2/N_1 = {ratio:g}$:1\n"
                  f"Module $m = {MOD:g}$ mm; addendum $m$, dedendum $1.25\\,m$", size=14).at(
                      c2[0] + r2 + 30, c1[1] - 150, anchor="top_left")
        diag.caption(
            "**Figure 7:** Spur gear pair with pitch circles, centre distance and a 2:1 speed reduction",
            small_caps=True,
        )
    return diag


def build_diagram(output_dir: Path | str = "examples/engineering") -> Path:
    return render_all(diagram(), output_dir, "07_spur_gear_pair")["svg"]


if __name__ == "__main__":
    dest = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("examples/engineering")
    build_diagram(dest)
