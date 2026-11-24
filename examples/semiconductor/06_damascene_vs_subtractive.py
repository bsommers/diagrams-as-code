"""Subtractive aluminium patterning versus copper damascene, four cross-sections each (SEMICONDUCTOR domain).

Top row: the older subtractive flow deposits the metal first, etches it into lines
and fills the gaps with dielectric. Bottom row: copper cannot be etched into lines
practically, so damascene etches trenches in the dielectric, lines them with a
diffusion barrier, over-plates copper and polishes the surplus away (CMP). Schematic
and not to scale; dual damascene (trench and via in one fill) and the etch-stop
layers are left out for clarity.
"""
from __future__ import annotations

import sys
from pathlib import Path

from diagrams_as_code import Diagram, Style
from diagrams_as_code.draft import Draft
from diagrams_as_code.output import render_all

INK = "#1F2F57"
ILD, AL, CU, RESIST, BARRIER = "#DCE8F4", "#A9B4C4", "#D98B4A", "#E9A15B", "#2B2B2B"
W = 190.0


def diagram() -> Diagram:
    with Diagram("Subtractive Al vs copper damascene patterning (schematic cross-sections)", theme="paper") as diag:
        k = Draft(diag, size=11.5)

        def poly(ox, oy, pts, fill, z=-3):
            diag.polygon([(ox + x, oy + y) for x, y in pts], style=Style(fill=fill, stroke=INK, stroke_width=1.0), z=z)

        def rect(ox, oy, x0, y0, x1, y1, fill, z=-3):
            poly(ox, oy, [(x0, y0), (x1, y0), (x1, y1), (x0, y1)], fill, z)

        def line(ox, oy, pts, width=2.6, color=BARRIER, z=-1):
            diag.polyline([(ox + x, oy + y) for x, y in pts], style=Style(fill="none", stroke=color, stroke_width=width), z=z)

        lines_x = ((15, 65), (125, 175))
        # ----------------------------------------------------------------- subtractive
        oy = 90.0
        steps_s = ["1  Deposit Al film", "2  Pattern resist, etch Al", "3  Strip resist, fill gaps", "4  Planarize dielectric"]
        for i, title in enumerate(steps_s):
            ox = 200 + i * 220
            rect(ox, oy, 0, 110, W, 150, ILD, z=-4)
            if i == 0:
                rect(ox, oy, 0, 80, W, 110, AL)
            else:
                if i in (2, 3):
                    rect(ox, oy, 0, 60 if i == 2 else 80, W, 110, ILD, z=-3)
                for a, b in lines_x:
                    rect(ox, oy, a, 80, b, 110, AL, z=-2)
                    if i == 1:
                        rect(ox, oy, a, 64, b, 80, RESIST, z=-2)
            diag.text(title, size=12.5).at(ox + W / 2, oy + 165, anchor="top_center")
        diag.text("**Subtractive**\n(aluminium)\nmetal first, then etch", size=13).at(30, oy + 90, anchor="left_center")
        # ------------------------------------------------------------------- damascene
        oy = 310.0
        steps_d = ["1  Deposit dielectric", "2  Etch trenches", "3  Barrier + Cu plating", "4  CMP: polish flat"]
        notched = [(0, 80), (15, 80), (15, 110), (65, 110), (65, 80), (125, 80), (125, 110), (175, 110), (175, 80), (W, 80)]
        for i, title in enumerate(steps_d):
            ox = 200 + i * 220
            if i == 0:
                rect(ox, oy, 0, 80, W, 150, ILD, z=-4)
            elif i in (1, 2):
                poly(ox, oy, notched + [(W, 150), (0, 150)], ILD, z=-4)
            else:
                rect(ox, oy, 0, 80, W, 150, ILD, z=-4)
            if i == 2:
                poly(ox, oy, [(0, 62), (W, 62)] + list(reversed(notched)), CU, z=-3)
                line(ox, oy, notched)
            if i == 3:
                for a, b in lines_x:
                    rect(ox, oy, a, 80, b, 110, CU, z=-3)
                    line(ox, oy, [(a, 80), (a, 110), (b, 110), (b, 80)])
            diag.text(title, size=12.5).at(ox + W / 2, oy + 165, anchor="top_center")
        diag.text("**Damascene**\n(copper)\netch trenches, then fill", size=13).at(30, oy + 90, anchor="left_center")
        k.leader((200 + 2 * 220 + 30, 310 + 72), (200 + 2 * 220 + 95, 310 + 22), "Cu overburden", anchor="center")

        # legend
        ly = 310 + 215
        items = [("dielectric (oxide / low-k)", ILD), ("aluminium", AL), ("copper", CU), ("resist", RESIST), ("barrier liner", BARRIER)]
        x = 200
        for name, col in items:
            rect(0, 0, x, ly, x + 22, ly + 14, col)
            diag.text(name, size=11.5).at(x + 30, ly + 7, anchor="left_center")
            x += 30 + 7.2 * len(name) + 30
        diag.caption("**Figure 6:** Subtractive aluminium versus copper damascene. Schematic, not to scale; "
                     "real flows add etch-stop layers, a via level and (for Cu) a capping layer.", small_caps=True)
    return diag


def build_diagram(output_dir: Path | str = "examples/semiconductor") -> Path:
    return render_all(diagram(), output_dir, "06_damascene_vs_subtractive")["svg"]


if __name__ == "__main__":
    dest = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("examples/semiconductor")
    build_diagram(dest)
