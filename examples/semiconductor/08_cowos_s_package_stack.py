"""CoWoS-S style 2.5D package: SoC and HBM on a silicon interposer on an organic substrate (SEMICONDUCTOR domain).

Chip-on-Wafer-on-Substrate with a silicon interposer (the "-S" variant): the logic
die and the HBM stacks sit side by side on a passive silicon interposer whose
wiring layers (RDL) join them through fine-pitch microbumps; through-silicon vias
(TSVs) carry signals and power down to the C4 bumps, an organic package substrate
fans out to the BGA balls that solder to the board. Each HBM stack is DRAM dies
joined by TSVs and microbumps on a base logic die. Schematic cross-section, not to
scale (bump and TSV pitch are exaggerated roughly 5 to 20 times; the lid, heat
spreader and passive devices are omitted).
"""
from __future__ import annotations

import sys
from pathlib import Path

from diagrams_as_code import Diagram, Style
from diagrams_as_code.draft import Draft
from diagrams_as_code.output import render_all

INK = "#1F2F57"
DIE, DRAM, BASE = "#9DB7D9", "#B9CBE3", "#8FA6C7"
SI_INT, TSV_CU, BUMP, UNDERFILL = "#D5DAE2", "#D98B4A", "#9A9A9A", "#F5E8B8"
SUB, SUB_LINE, BALL = "#CFE2C7", "#7FA37A", "#B0B0B0"
OY = 60.0


def diagram() -> Diagram:
    with Diagram("CoWoS-S 2.5D package stack (schematic cross-section, not to scale)", theme="paper") as diag:
        k = Draft(diag, size=11.5)

        def box(x0, y0, x1, y1, fill, z=-3, width=1.0):
            diag.polygon([(x0, OY + y0), (x1, OY + y0), (x1, OY + y1), (x0, OY + y1)],
                         style=Style(fill=fill, stroke=INK, stroke_width=width), z=z)

        def ball(cx, cy, r, fill, z=-2):
            diag.path(f"M {cx - r:.2f} {OY + cy:.2f} a {r:.2f} {r:.2f} 0 1 0 {2 * r:.2f} 0 a {r:.2f} {r:.2f} 0 1 0 {-2 * r:.2f} 0 Z",
                      style=Style(fill=fill, stroke=INK, stroke_width=0.9), z=z)

        # ---- layer positions (y top, y bottom) ---------------------------------------------
        Y_DIE_BOT = 150.0          # underside of the dies
        Y_UB = (150.0, 158.0)      # microbump layer
        Y_RDL = (158.0, 176.0)
        Y_INT = (176.0, 226.0)     # interposer silicon
        Y_C4 = (226.0, 240.0)
        Y_SUB = (240.0, 300.0)
        Y_BGA = (300.0, 320.0)
        XL, XR = 60.0, 740.0       # interposer extent
        SL, SR = 20.0, 780.0       # substrate extent

        # substrate with build-up layers and vias
        box(SL, Y_SUB[0], SR, Y_SUB[1], SUB, z=-5)
        for yy in (252, 264, 276, 288):
            box(SL + 6, yy, SR - 6, yy + 2, SUB_LINE, z=-4, width=0.5)
        # underfill between interposer and substrate and around the microbumps
        box(XL - 6, Y_INT[1], XR + 6, Y_SUB[0], UNDERFILL, z=-5, width=0.6)
        # interposer: RDL on top of the silicon body
        box(XL, Y_INT[0], XR, Y_INT[1], SI_INT, z=-4)
        box(XL, Y_RDL[0], XR, Y_RDL[1], "#E8E1F0", z=-4)
        # dies ---------------------------------------------------------------------------
        hbms = ((90.0, 200.0), (570.0, 680.0))
        soc = (260.0, 540.0)
        box(soc[0], 80, soc[1], Y_DIE_BOT, DIE, z=-3)
        diag.text("SoC / GPU die\n(logic)", size=13).at((soc[0] + soc[1]) / 2 + 0.0, OY + 115, anchor="center")
        for hx0, hx1 in hbms:
            # base logic die plus four DRAM dies, 12 px each with 4 px gaps for the microbumps
            y = Y_DIE_BOT
            tiers = [("base", BASE)] + [("dram", DRAM)] * 4
            for n, (kind, col) in enumerate(tiers):
                box(hx0, y - 14, hx1, y, col, z=-3)
                if n < 4:  # microbumps between this die and the next one up
                    for bx in (hx0 + 16, hx0 + 42, hx0 + 68, hx0 + 94):
                        box(bx - 5, y - 18, bx + 5, y - 14, BUMP, z=-2, width=0.6)
                y -= 18
            top = y + 18 - 14
            for bx in (hx0 + 16, hx0 + 42, hx0 + 68, hx0 + 94):
                box(bx - 2.5, top, bx + 2.5, Y_DIE_BOT, TSV_CU, z=-1, width=0.5)
            diag.text("HBM stack", size=12.5).at((hx0 + hx1) / 2, OY + top - 8, anchor="bottom_center")
        # microbumps under every die
        for x in list(range(112, 200, 26)) + list(range(574, 680, 26)) + list(range(270, 540, 24)):
            box(x - 5, Y_UB[0], x + 5, Y_UB[1], BUMP, z=-2, width=0.6)
        # RDL wiring between SoC and each HBM (two layers of lines)
        for yy, (a, b) in ((163, (150, 275)), (170, (150, 275)), (163, (525, 650)), (170, (525, 650))):
            diag.polyline([(a, OY + yy), (b, OY + yy)], style=Style(fill="none", stroke="#6B4FA0", stroke_width=1.6), z=-1)
        # TSVs through the interposer
        tsv_x = list(range(100, 700, 40))
        for x in tsv_x:
            box(x - 4, Y_RDL[1], x + 4, Y_INT[1], TSV_CU, z=-2, width=0.5)
        # C4 bumps (solder balls) on the underside of the interposer
        for x in tsv_x:
            ball(x, (Y_C4[0] + Y_C4[1]) / 2, 8.0, BUMP)
        # BGA balls under the substrate
        for x in range(50, 760, 50):
            ball(x, Y_BGA[0] + 10, 10.0, BALL)

        # ---- labels ---------------------------------------------------------------------
        def tag(tip, at, text, anchor):
            k.leader((tip[0], OY + tip[1]), (at[0], OY + at[1]), text, anchor=anchor)

        tag((100, 143), (10, 80), "HBM base logic die\n(PHY, controller)", "right_center")
        tag((95, 100), (10, 20), "HBM DRAM dies", "right_center")
        tag((110, 154), (10, 190), "microbumps", "right_center")
        tag((XL + 6, 200), (10, 265), "silicon interposer", "right_center")
        tag((132, 110), (10, 135), "TSV through DRAM dies", "right_center")
        tag((735, 167), (810, 150), "RDL wiring (die-to-die)", "left_center")
        tag((660, 200), (810, 192), "interposer TSV", "left_center")
        tag((660, 233), (810, 232), "C4 bumps in underfill", "left_center")
        tag((770, 275), (810, 275), "organic substrate\n(build-up layers)", "left_center")
        tag((750, 310), (810, 325), "BGA balls to board", "left_center")
        diag.caption("**Figure 8:** CoWoS-S style 2.5D package. Schematic cross-section, not to scale.", small_caps=True)
    return diag


def build_diagram(output_dir: Path | str = "examples/semiconductor") -> Path:
    return render_all(diagram(), output_dir, "08_cowos_s_package_stack")["svg"]


if __name__ == "__main__":
    dest = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("examples/semiconductor")
    build_diagram(dest)
