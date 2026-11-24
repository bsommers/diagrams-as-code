"""Back-end-of-line (BEOL) interconnect stack from transistor to solder bump (SEMICONDUCTOR domain).

One signal path climbs from a transistor drain through a tungsten contact, eight
copper levels joined by vias, a bond pad and a copper pillar with a solder cap.
Wire pitch and thickness grow with height: the thin local levels route between
neighbouring cells, the intermediate levels carry block-level wiring, and the
thick global levels carry power, clocks and long buses. Schematic and not to
scale; the number of levels, the low-k material and the barrier / etch-stop
liners (omitted here) differ between technologies.
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

from diagrams_as_code import Diagram, Style
from diagrams_as_code.draft import Draft
from diagrams_as_code.output import render_all

INK = "#1F2F57"
CU, W_PLUG, SI, STI = "#D98B4A", "#555555", "#CDD2DA", "#BBD6EE"
NPLUS, POLY, SPACER = "#B5D8A5", "#D77C74", "#6FA8A0"
TIERS = (
    # name, levels, wire width, spacing, metal thickness, via height, dielectric fill
    ("Local", (1, 2, 3), 14, 14, 16, 16, "#DCE8F4"),
    ("Intermediate", (4, 5, 6), 28, 28, 20, 18, "#E6EDF5"),
    ("Global", (7, 8), 64, 56, 36, 30, "#EEEEEE"),
)
CX, SURF = 330.0, 590.0  # path column x, silicon surface y


def diagram() -> Diagram:
    with Diagram("BEOL metal stack: transistor to bump (schematic, not to scale)", theme="paper") as diag:
        k = Draft(diag, size=11.5)
        X0, X1 = 80.0, 580.0

        def box(x0, y0, x1, y1, fill, z=-3, width=1.0):
            diag.polygon([(x0, y0), (x1, y0), (x1, y1), (x0, y1)],
                         style=Style(fill=fill, stroke=INK, stroke_width=width), z=z)

        # ---- silicon and one transistor ---------------------------------------------------
        box(X0, SURF, X1, SURF + 44, SI, z=-5)
        box(X0, SURF - 2, X0 + 40, SURF + 24, STI, z=-4)
        box(X1 - 40, SURF - 2, X1, SURF + 24, STI, z=-4)
        box(CX - 130, SURF, CX - 80, SURF + 12, NPLUS)
        box(CX - 30, SURF, CX + 30, SURF + 12, NPLUS)
        box(CX - 80, SURF - 26, CX - 30, SURF - 3, POLY)
        diag.polygon([(CX - 80, SURF - 3), (CX - 30, SURF - 3), (CX - 30, SURF), (CX - 80, SURF)],
                     style=Style(fill="#27408B", stroke=INK, stroke_width=0.8), z=-3)

        # ---- stack, built bottom-up --------------------------------------------------------
        y = SURF
        contact_h = 26.0
        levels = []  # (label, y_top, y_bottom) of each metal line
        box(X0, y - contact_h, X1, y, "#E9E9EE", z=-5)             # pre-metal dielectric
        box(CX - 8, y - contact_h, CX + 8, y, W_PLUG, z=-2)        # tungsten contact
        k.leader((CX + 8, y - 13), (X1 + 40, y - 6), "W contact", anchor="left_center")
        y -= contact_h
        tier_edges = []
        for name, lv, ww, sp, th, vh, fill in TIERS:
            top_of_tier_start = y
            for n in lv:
                # via layer then metal layer, one dielectric block each
                box(X0, y - vh, X1, y, fill, z=-5)
                box(CX - ww * 0.35, y - vh, CX + ww * 0.35, y, CU, z=-2)
                y -= vh
                box(X0, y - th, X1, y, fill, z=-5)
                for dx in (-2, -1, 1, 2):
                    cxn = CX + dx * (ww + sp)
                    if X0 + ww < cxn < X1 - ww:
                        box(cxn - ww / 2, y - th, cxn + ww / 2, y, CU, z=-2)
                box(CX - ww / 2, y - th, CX + ww / 2, y, CU, z=-2)
                levels.append((f"M{n}", y - th, y))
                y -= th
            tier_edges.append((name, top_of_tier_start, y))
        # ---- passivation, pad, pillar and solder cap ------------------------------------
        pas_top = y - 24
        box(X0, pas_top, X1, y, "#D9D9D9", z=-5)
        box(CX - 50, y - 12, CX + 50, y, "#C8C8D0", z=-2)           # bond pad (Al) in the top level
        box(CX - 36, pas_top - 40, CX + 36, y - 2, CU, z=-2)        # Cu pillar through the opening
        cap = [(CX - 36, pas_top - 40)]
        for i in range(0, 13):
            a = math.pi - math.pi * i / 12
            cap.append((CX + 38 * math.cos(a), pas_top - 40 - 34 * math.sin(a)))
        cap.append((CX + 36, pas_top - 40))
        diag.polygon(cap, style=Style(fill="#BFBFBF", stroke=INK, stroke_width=1.0), z=-2)
        k.leader((CX + 36, pas_top - 55), (X1 + 40, pas_top - 70), "solder cap", anchor="left_center")
        k.leader((CX + 36, pas_top - 20), (X1 + 40, pas_top - 25), "Cu pillar", anchor="left_center")
        k.leader((CX + 46, y - 6), (X1 + 40, y + 6), "Al bond pad", anchor="left_center")

        # ---- per-level labels on the left, tiers on the right -----------------------------
        for label, ya, yb in levels:
            diag.text(label, size=11.5).at(X0 - 10, (ya + yb) / 2, anchor="right_center")
        for name, ya, yb in tier_edges:
            if name != "Global":
                k.hidden_line([(X0 - 70, yb), (X1 + 12, yb)])
        tier_notes = {"Local": "thin Cu, low-k\nfine pitch", "Intermediate": "~2x pitch\nblock routing",
                      "Global": "thick Cu\npower, clocks, buses"}
        for name, ya, yb in tier_edges:
            diag.text(f"**{name}**\n{tier_notes[name]}", size=11.5).at(X1 + 40, (ya + yb) / 2, anchor="left_center")
        k.leader((CX - 50, SURF - 14), (X0 - 30, SURF - 4), "poly gate", anchor="right_center")
        k.leader((CX - 100, SURF + 6), (X0 - 30, SURF + 24), "n+ source", anchor="right_center")
        k.leader((CX + 20, SURF + 8), (X1 + 40, SURF + 24), "n+ drain", anchor="left_center")
        k.leader((X0 + 100, SURF + 34), (X0 - 30, SURF + 50), "Si substrate", anchor="right_center")
        diag.text("FEOL: transistors", size=12, color="#444444").at(CX, SURF + 70, anchor="top_center")
        diag.caption("**Figure 5:** BEOL interconnect stack, one signal path. Schematic cross-section, not to scale; "
                     "barrier and etch-stop liners and the dual-damascene via/line merge are omitted.", small_caps=True)
    return diag


def build_diagram(output_dir: Path | str = "examples/semiconductor") -> Path:
    return render_all(diagram(), output_dir, "05_beol_metal_stack")["svg"]


if __name__ == "__main__":
    dest = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("examples/semiconductor")
    build_diagram(dest)
