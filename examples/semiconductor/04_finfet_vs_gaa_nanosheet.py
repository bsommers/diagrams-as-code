"""FinFET versus gate-all-around nanosheet transistors, cut across the gate (SEMICONDUCTOR domain).

Both views are taken perpendicular to the channel, through the gate: current flows
into the page. In a FinFET the gate wraps three sides of each silicon fin; in a
gate-all-around (GAA) nanosheet device it wraps all four sides of each stacked
sheet, which improves electrostatic control and lets the sheet width be tuned for
drive current. Schematic and not to scale; fin and sheet counts, widths and the
inner structure of the high-k / metal-gate stack are simplified.
"""
from __future__ import annotations

import sys
from pathlib import Path

from diagrams_as_code import Diagram, Style
from diagrams_as_code.draft import Draft
from diagrams_as_code.output import render_all

INK = "#1F2F57"
SI, STI, HIK, GATE = "#BFC6D2", "#BBD6EE", "#27408B", "#E2A95B"


def diagram() -> Diagram:
    with Diagram("FinFET vs gate-all-around nanosheet (cross-section through the gate, schematic)",
                 theme="paper") as diag:
        k = Draft(diag, size=11.5)

        def box(ox, x0, y0, x1, y1, fill, z=-3, hatch=False, holes=()):
            p = [(ox + x0, 90 + y0), (ox + x1, 90 + y0), (ox + x1, 90 + y1), (ox + x0, 90 + y1)]
            diag.polygon(p, style=Style(fill=fill, stroke=INK, stroke_width=1.0), z=z)
            if hatch:
                k.hatch(p, angle=45, gap=6, width=0.5, holes=[[(ox + a, 90 + b), (ox + c, 90 + b), (ox + c, 90 + d), (ox + a, 90 + d)] for a, b, c, d in holes])

        def pt(ox, x, y):
            return (ox + x, 90 + y)

        t = 3.0  # high-k thickness (exaggerated)
        # ------------------------------------------------------------ FinFET
        A = 70.0
        box(A, 0, 230, 340, 290, SI, z=-5)                         # substrate
        box(A, 0, 200, 340, 230, STI, z=-4, hatch=True, holes=[(x - 12, 200, x + 12, 230) for x in (70, 160, 250)])            # STI between fins
        box(A, 20, 50, 320, 200, GATE, z=-4)                       # metal gate over STI and fins
        fins = (70, 160, 250)
        for x in fins:
            box(A, x - 12 - t, 85 - t, x + 12 + t, 200, HIK, z=-3)  # high-k wrapping the fin
            box(A, x - 12, 85, x + 12, 232, SI, z=-2)               # the fin itself
        # ------------------------------------------------------------ GAA
        B = 560.0
        box(B, 0, 230, 340, 290, SI, z=-5)
        box(B, 0, 200, 340, 230, STI, z=-4, hatch=True, holes=[(110, 200, 230, 230)])
        box(B, 40, 40, 300, 200, GATE, z=-4)
        box(B, 110, 190, 230, 232, SI, z=-3)                        # substrate mesa under the stack
        for y0 in (62, 108, 154):
            box(B, 80 - t, y0 - t, 260 + t, y0 + 16 + t, HIK, z=-3)
            box(B, 80, y0, 260, y0 + 16, SI, z=-2)

        # panel titles
        diag.text("FinFET: gate on three sides", size=15).at(A + 170, 70, anchor="bottom_center")
        diag.text("Gate-all-around nanosheet: gate on four sides", size=15).at(B + 170, 70, anchor="bottom_center")

        # FinFET labels and dimensions
        k.leader(pt(A, 70, 170), pt(A, -30, 125), "silicon fin\n(channel)", anchor="right_center")
        k.leader(pt(A, 28, 70), pt(A, -30, 70), "metal gate", anchor="right_center")
        k.leader(pt(A, 250 + 13, 130), pt(A, 370, 125), "high-k\ndielectric", anchor="left_center")
        k.leader(pt(A, 300, 215), pt(A, 370, 215), "STI oxide", anchor="left_center")
        k.leader(pt(A, 300, 270), pt(A, 370, 270), "Si substrate", anchor="left_center")
        k.dimension(pt(A, 58, 85), pt(A, 82, 85), "$W_{fin}$", offset=-55, side=1)

        # GAA labels
        k.leader(pt(B, 170, 70), pt(B, -30, 70), "Si nanosheet\n(channel)", anchor="right_center")
        k.leader(pt(B, 52, 160), pt(B, -30, 165), "metal gate", anchor="right_center")
        k.leader(pt(B, 262, 125), pt(B, 370, 105), "high-k\ndielectric", anchor="left_center")
        k.leader(pt(B, 300, 215), pt(B, 370, 215), "STI oxide", anchor="left_center")
        k.leader(pt(B, 300, 270), pt(B, 370, 270), "Si substrate", anchor="left_center")
        k.dimension(pt(B, 80, 108), pt(B, 260, 108), "$W_{sheet}$", offset=-88, side=1)
        diag.text("current flows into the page (source to drain)", size=11.5, color="#444444").at(
            A + 170, 90 + 320, anchor="top_center")
        diag.text("current flows into the page (source to drain)", size=11.5, color="#444444").at(
            B + 170, 90 + 320, anchor="top_center")
        diag.caption("**Figure 4:** Same gate-cut view of a FinFET and a gate-all-around nanosheet. Schematic, not to scale; "
                     "real devices use several fins or sheets in parallel and a layered work-function metal stack.",
                     small_caps=True)
    return diag


def build_diagram(output_dir: Path | str = "examples/semiconductor") -> Path:
    return render_all(diagram(), output_dir, "04_finfet_vs_gaa_nanosheet")["svg"]


if __name__ == "__main__":
    dest = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("examples/semiconductor")
    build_diagram(dest)
