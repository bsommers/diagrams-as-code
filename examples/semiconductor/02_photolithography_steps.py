"""Photolithography and pattern transfer as six cross-section panels (SEMICONDUCTOR domain).

One film on a silicon wafer is patterned with a positive photoresist: the resist
is coated, exposed through a mask, developed, used as the etch mask and then
stripped. Schematic and not to scale (a real resist is a few hundred nm thick,
the mask features are 4x larger than the printed ones). The wafer-fab loop and
the scanner cell are in examples/manufacturing; this is the cross-section view
of what one pass leaves on the wafer.
"""
from __future__ import annotations

import sys
from pathlib import Path

from diagrams_as_code import Diagram, Style
from diagrams_as_code.draft import Draft
from diagrams_as_code.output import render_all

INK = "#1F2F57"
SI, FILM, RESIST, EXPOSED = "#C9CED6", "#8FB8DE", "#E9A15B", "#F6D4A8"
CHROME, GLASS, UV = "#333333", "#E7F0F7", "#7A3FBF"
W, PITCH_X, PITCH_Y = 250.0, 300.0, 250.0
OPEN0, OPEN1 = 105.0, 145.0  # printed opening, panel-local x


def diagram() -> Diagram:
    with Diagram("Photolithography and pattern transfer (schematic cross-sections, not to scale)",
                 theme="paper") as diag:
        k = Draft(diag)

        def rect(ox, oy, x0, y0, x1, y1, fill, hatch=False):
            pts = [(ox + x0, oy + y0), (ox + x1, oy + y0), (ox + x1, oy + y1), (ox + x0, oy + y1)]
            diag.polygon(pts, style=Style(fill=fill, stroke=INK, stroke_width=1.0), z=-3)
            if hatch:
                k.hatch(pts, angle=45, gap=5, width=0.6)

        def label(text, ox, oy, size=13):
            diag.text(text, size=size).at(ox + W / 2, oy, anchor="top_center")

        panels = [
            ("1  Film on silicon", "film deposited (oxide, poly or metal)"),
            ("2  Spin-coat resist", "photoresist, then soft bake"),
            ("3  Expose", "UV through the mask; exposed resist (hatched)"),
            ("4  Develop", "exposed resist dissolves (positive tone)"),
            ("5  Etch", "film removed where resist is open"),
            ("6  Strip resist", "patterned film remains"),
        ]
        for i, (title, note) in enumerate(panels):
            ox = 50 + (i % 3) * PITCH_X
            oy = 60 + (i // 3) * PITCH_Y
            label(title, ox, oy + 158)
            diag.text(note, size=10.5, color="#444444").at(ox + W / 2, oy + 180, anchor="top_center")
            rect(ox, oy, 0, 120, W, 150, SI)                      # silicon substrate
            if i in (0, 1, 2, 3):
                rect(ox, oy, 0, 100, W, 120, FILM)                # unetched film
            if i == 4 or i == 5:
                rect(ox, oy, 0, 100, OPEN0, 120, FILM)
                rect(ox, oy, OPEN1, 100, W, 120, FILM)
            if i == 1:
                rect(ox, oy, 0, 70, W, 100, RESIST)
            if i == 2:
                rect(ox, oy, 0, 70, OPEN0, 100, RESIST)
                rect(ox, oy, OPEN0, 70, OPEN1, 100, EXPOSED, hatch=True)
                rect(ox, oy, OPEN1, 70, W, 100, RESIST)
                # mask: glass plate with chrome absorber either side of the opening
                rect(ox, oy, 0, 22, W, 32, GLASS)
                rect(ox, oy, 0, 32, OPEN0, 37, CHROME)
                rect(ox, oy, OPEN1, 32, W, 37, CHROME)
                for x in (OPEN0 + 8, (OPEN0 + OPEN1) / 2, OPEN1 - 8):
                    diag.connect((ox + x, oy - 4), (ox + x, oy + 66), routing="direct",
                                 width=1.8, head="stealth", color=UV)
                diag.text("UV", size=11, color=UV).at(ox + OPEN1 + 14, oy + 2, anchor="left_center")
                diag.text("mask", size=11).at(ox + 6, oy + 14, anchor="bottom_left")
            if i in (3, 4):
                rect(ox, oy, 0, 70, OPEN0, 100, RESIST)
                rect(ox, oy, OPEN1, 70, W, 100, RESIST)
        # legend
        ly = 60 + 2 * PITCH_Y - 20
        items = [("silicon", SI, False), ("film", FILM, False), ("photoresist", RESIST, False),
                 ("exposed resist", EXPOSED, True), ("mask glass", GLASS, False), ("chrome", CHROME, False)]
        for j, (name, col, hat) in enumerate(items):
            x = 70 + j * 140
            rect(0, 0, x, ly, x + 22, ly + 14, col, hatch=hat)
            diag.text(name, size=11.5).at(x + 30, ly + 7, anchor="left_center")
        diag.caption("**Figure 2:** One lithography and etch pass in cross-section. Layer thicknesses are exaggerated; "
                     "the opening is shown at wafer scale (a real mask is 4x).", small_caps=True)
    return diag


def build_diagram(output_dir: Path | str = "examples/semiconductor") -> Path:
    return render_all(diagram(), output_dir, "02_photolithography_steps")["svg"]


if __name__ == "__main__":
    dest = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("examples/semiconductor")
    build_diagram(dest)
