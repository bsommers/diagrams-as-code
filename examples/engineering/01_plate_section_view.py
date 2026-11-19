"""A dimensioned plate with a through hole and its half-section A-A.

Plan view and section view are scaled from the same millimetre dimensions
(2.5 px per mm). The section cuts through the hole centre, so the hatched
metal is split by the 30 mm bore; hatching is clipped to the cut faces.
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

from diagrams_as_code import Diagram
from diagrams_as_code.draft import Draft
from diagrams_as_code.output import render_all

K = 2.5                      # px per mm
W, H, T, D = 120.0, 80.0, 20.0, 30.0   # plate width, height, thickness, bore diameter (mm)


def diagram() -> Diagram:
    x0, y0 = 120.0, 130.0           # plan view top-left
    pw, ph = W * K, H * K
    cx, cy = x0 + pw / 2, y0 + ph / 2
    r = D * K / 2
    plan = [(x0, y0), (x0 + pw, y0), (x0 + pw, y0 + ph), (x0, y0 + ph)]
    sx = 640.0                      # section view left edge
    sw = T * K
    top = [(sx, y0), (sx + sw, y0), (sx + sw, cy - r), (sx, cy - r)]
    bot = [(sx, cy + r), (sx + sw, cy + r), (sx + sw, y0 + ph), (sx, y0 + ph)]

    with Diagram("Plate with bore, section A-A", theme="paper") as diag:
        k = Draft(diag, size=13)
        # Plan view.
        k.outline(plan)
        n = 48
        circle = [(cx + r * math.cos(2 * math.pi * i / n), cy + r * math.sin(2 * math.pi * i / n)) for i in range(n)]
        k.outline(circle, width=2.0)
        k.centerline((cx, y0 - 14), (cx, y0 + ph + 14))
        k.centerline((x0 - 14, cy), (x0 + pw + 14, cy))
        k.section_arrows((cx + 50, y0 - 26), (cx + 50, y0 + ph + 26), "A", direction=1, length=26)
        k.dimension((x0, y0 + ph), (x0 + pw, y0 + ph), "$120$", offset=56)
        k.dimension((x0, y0 + ph), (x0, y0), "$80$", offset=46, side=-1)
        k.radius_dim((cx, cy), r, 135, "$\\emptyset 30$", diameter=True, overshoot=38)

        # Section A-A.
        for poly in (top, bot):
            k.outline(poly)
            k.hatch(poly, angle=45, gap=7)
        k.centerline((sx - 14, cy), (sx + sw + 14, cy))
        k.dimension((sx, y0 + ph), (sx + sw, y0 + ph), "$20$", offset=56)
        k.dimension((sx + sw, cy - r), (sx + sw, cy + r), "", offset=50, side=-1)
        diag.text("$\\emptyset 30$", size=13).at(sx + sw + 58, cy, anchor="left_center")
        diag.text("**SECTION A-A**", size=15).at(sx + sw / 2, y0 - 66, anchor="center")
        diag.text("**PLAN VIEW**", size=15).at(cx, y0 - 66, anchor="center")
        diag.text("Dimensions in mm. Material: mild steel plate, 20 mm thick.", size=12).at(
            x0, y0 + ph + 96, anchor="left_center")
        diag.caption(
            "**Figure 1:** Dimensioned plate with a through bore and hatched half-section A-A",
            small_caps=True,
        )
    return diag


def build_diagram(output_dir: Path | str = "examples/engineering") -> Path:
    return render_all(diagram(), output_dir, "01_plate_section_view")["svg"]


if __name__ == "__main__":
    dest = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("examples/engineering")
    build_diagram(dest)
