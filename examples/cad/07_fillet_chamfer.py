"""Fillet and chamfer callouts on a hatched section.

The outline is built from the stated radii and chamfer legs: each corner is
replaced by a tangent arc (fillet) or a straight cut (chamfer) computed from
its size, so the callouts match the geometry exactly (millimetres).
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

from diagrams_as_code import Diagram, Style
from diagrams_as_code.draft import Draft
from diagrams_as_code.output import render_all

S = 5.0
OX, OY = 90.0, 360.0
INK = "#1F2F57"
RED = "#9C2F2F"
W, H, BASE, TOWER = 70.0, 50.0, 20.0, 30.0   # overall width, height, base height, tower width
R_OUT, R_TIP, R_IN = 6.0, 2.0, 4.0
C_BASE, C_TOP = 4.0, 3.0


def px(x, y):
    return (OX + x * S, OY - y * S)


def arc(cx, cy, r, a0, a1, n=14):
    return [(cx + r * math.cos(math.radians(a0 + (a1 - a0) * i / n)),
             cy + r * math.sin(math.radians(a0 + (a1 - a0) * i / n))) for i in range(n + 1)]


def profile():
    pts = []
    pts += arc(R_OUT, R_OUT, R_OUT, 180, 270)               # bottom-left fillet
    pts += [(W - C_BASE, 0), (W, C_BASE)]                    # bottom-right chamfer
    pts += arc(W - R_TIP, BASE - R_TIP, R_TIP, 0, 90)        # fillet at the base's top corner
    pts += arc(TOWER + R_IN, BASE + R_IN, R_IN, 270, 180)    # inside fillet at the step
    pts += [(TOWER, H - C_TOP), (TOWER - C_TOP, H), (0, H)]  # tower chamfer, top face
    return pts


def diagram() -> Diagram:
    pts = [px(*p) for p in profile()]
    with Diagram("Fillet and chamfer callouts", theme="paper") as diag:
        k = Draft(diag)
        diag.polygon(pts, style=Style(fill="#DCE6F2", stroke="none"), z=-3)
        k.hatch(pts, angle=45, gap=8)
        k.outline(pts)
        # Tangent points and centres of the fillets.
        for (cx, cy, r, ang) in ((R_OUT, R_OUT, R_OUT, 225.0), (W - R_TIP, BASE - R_TIP, R_TIP, 45.0),
                                 (TOWER + R_IN, BASE + R_IN, R_IN, 225.0)):
            c = px(cx, cy)
            diag.path(f"M {c[0] - 2.5:.1f} {c[1]:.1f} a 2.5 2.5 0 1 0 5 0 a 2.5 2.5 0 1 0 -5 0",
                      style=Style(fill=INK, stroke=INK, stroke_width=0.5), z=2)
        kr = Draft(diag, ink=RED)
        # Fillet radii: leader from the centre through the arc.
        kr.radius_dim(px(R_OUT, R_OUT), R_OUT * S, 225, f"$R{R_OUT:g}$", overshoot=34)
        kr.radius_dim(px(W - R_TIP, BASE - R_TIP), R_TIP * S, 45, f"$R{R_TIP:g}$", overshoot=34)
        tip = px(TOWER + R_IN + R_IN * math.cos(math.radians(225)), BASE + R_IN + R_IN * math.sin(math.radians(225)))
        kr.leader(tip, (tip[0] + 70, tip[1] - 20), f"$R{R_IN:g}$")
        # Chamfer callouts.
        k.leader(px(W - C_BASE / 2, C_BASE / 2), (px(W, 0)[0] + 50, px(W, 0)[1] + 54),
                 f"chamfer ${C_BASE:g}\\times45^\\circ$")
        k.leader(px(TOWER - C_TOP / 2, H - C_TOP / 2), (px(TOWER, H)[0] + 44, px(TOWER, H)[1] - 38),
                 f"chamfer ${C_TOP:g}\\times45^\\circ$")
        # Overall dimensions, offset well clear.
        k.dimension(px(0, 0), px(W, 0), f"${W:g}$", offset=70, side=1)
        k.dimension(px(0, 0), px(0, H), "", offset=44, side=-1)
        diag.text(f"${H:g}$", size=11).at(OX - 44 - 14, OY - H * S / 2, anchor="right_center")
        k.dimension(px(W, 0), px(W, BASE), "", offset=40, side=1)
        diag.text(f"${BASE:g}$", size=11).at(px(W, 0)[0] + 40 + 12, OY - BASE * S / 2 + 0, anchor="left_center")
        # Chamfer detail inset (x 8): the cut legs and the 45 degree angle.
        ix, iy, z = 640.0, 300.0, 14.0
        c = C_BASE * z
        sq = [(ix, iy), (ix + 120, iy), (ix + 120, iy - 120), (ix, iy - 120)]
        cut = [(ix, iy), (ix + 120 - c, iy), (ix + 120, iy - c), (ix + 120, iy - 120), (ix, iy - 120)]
        diag.polygon(cut, style=Style(fill="#DCE6F2", stroke="none"), z=-3)
        k.hatch(cut, angle=45, gap=8)
        k.outline(cut)
        k.dimension((ix + 120 - c, iy), (ix + 120, iy), f"${C_BASE:g}$", offset=26, side=1)
        k.dimension((ix + 120, iy), (ix + 120, iy - c), "", offset=34, side=1)
        diag.text(f"${C_BASE:g}$", size=11).at(ix + 120 + 34 + 12, iy - c / 2, anchor="left_center")
        diag.text("$45^\\circ$", size=12).at(ix + 120 - c - 34, iy + 16, anchor="center")
        diag.text("Detail of the chamfer", size=12).at(ix + 60, iy - 150, anchor="center")
        diag.text("Section, mm. Red = fillet radii, dots = arc centres.", size=12).at(OX, 500, anchor="left_center")
        diag.caption(
            "**Figure 7:** Fillet radii and chamfer callouts on a hatched section; every corner treatment is generated from its stated size",
            small_caps=True)
    return diag


def build_diagram(output_dir: Path | str = "output/cad") -> Path:
    return render_all(diagram(), output_dir, "07_fillet_chamfer")["svg"]


if __name__ == "__main__":
    dest = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("output/cad")
    build_diagram(dest)
