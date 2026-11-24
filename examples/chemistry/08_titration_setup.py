"""Titration setup: a 50 mL burette over a stirred Erlenmeyer flask, with dimension leaders.

Lengths are to scale at 0.62 px per mm (the burette's graduated length of 500 mm and
the 145 mm flask); tube widths are enlarged to stay readable. The meniscus is placed
from the reading itself: a 0 to 50 mL scale of 500 mm is 10 mm per mL, so a reading of
25.00 mL sits 250 mm below the zero mark. The numbers match the strong acid curve of
figure 2: 25.00 mL of 0.100 M HCl needs 25.00 mL of 0.100 M NaOH.
"""
from __future__ import annotations

import sys
from pathlib import Path

from diagrams_as_code import Diagram, Style
from diagrams_as_code.draft import Draft
from diagrams_as_code.output import render_all

MM = 0.62                       # px per mm
INK, STEEL, GLASS = "#1F2F57", "#555555", "#FFFFFF"
TITRANT, ANALYTE = "#E6EEF8", "#F6D3DC"
BX = 330.0                      # burette axis
Y0 = 110.0                      # the 0 mL mark
PER_ML = 10.0 * MM              # 10 mm of scale per mL
READING = 25.00                 # mL


def y_ml(v: float) -> float:
    return Y0 + v * PER_ML


def diagram() -> Diagram:
    with Diagram("Titration setup", theme="paper") as diag:
        k = Draft(diag, ink=INK, size=12)
        solid = lambda w, c=INK, fill="none": Style(fill=fill, stroke=c, stroke_width=w)
        bench = y_ml(50) + 182

        # Bench, stand, clamp.
        diag.polyline([(10, bench), (500, bench)], style=solid(2.4))
        diag.polyline([(40, 70), (40, bench)], style=solid(7, STEEL))
        diag.polyline([(40, 70), (40, bench)], style=solid(4.4, "#D0D0D0"))
        diag.polygon([(14, bench), (110, bench), (110, bench - 9), (14, bench - 9)], style=solid(1.4, fill="#D0D0D0"))
        diag.polyline([(40, 140), (BX - 10, 140)], style=solid(5, STEEL))
        diag.polygon([(BX - 12, 128), (BX + 12, 128), (BX + 12, 152), (BX - 12, 152)], style=solid(1.6, STEEL, "#D9D9D9"), z=3)

        # Burette: liquid below the meniscus, then the tube, scale and numbers.
        stop_y = y_ml(50) + 12
        diag.polygon([(BX - 8, y_ml(READING)), (BX + 8, y_ml(READING)), (BX + 8, stop_y), (BX - 8, stop_y)],
                     style=solid(0, TITRANT, TITRANT), z=0)
        diag.polyline([(BX - 8, 96), (BX - 8, stop_y)], style=solid(1.8), z=2)
        diag.polyline([(BX + 8, 96), (BX + 8, stop_y)], style=solid(1.8), z=2)
        ticks = []
        for i in range(51):
            y = y_ml(i)
            length = 8 if i % 10 == 0 else 5 if i % 5 == 0 else 3
            ticks.append(f"M {BX + 8 - length:.2f} {y:.2f} h {length}")
        diag.path(" ".join(ticks), style=solid(0.8), z=2)
        for v in range(0, 51, 10):
            diag.text(str(v), size=11).at(BX - 13, y_ml(v), anchor="right_center")
        diag.polyline([(BX - 8, y_ml(READING)), (BX + 8, y_ml(READING))], style=solid(1.6, "#9C2F2F"), z=3)

        # Stopcock, tip and a hanging drop.
        diag.polygon([(BX - 22, stop_y + 2), (BX + 22, stop_y + 2), (BX + 22, stop_y + 8), (BX - 22, stop_y + 8)],
                     style=solid(1.4, STEEL, "#BDBDBD"), z=3)
        diag.polygon([(BX - 4, stop_y + 8), (BX + 4, stop_y + 8), (BX + 1.5, stop_y + 62), (BX - 1.5, stop_y + 62)],
                     style=solid(1.4), z=2)
        tip_y = stop_y + 62

        # Erlenmeyer flask: neck top, shoulder, base; liquid and stir bar.
        neck_top = tip_y - 12
        shoulder = neck_top + 22
        base = neck_top + 145 * MM
        lx = BX - 11 - 22 * (535 - shoulder) / (base - shoulder)
        rx = 2 * BX - lx
        diag.polygon([(lx, 535), (rx, 535), (BX + 33, base), (BX - 33, base)], style=solid(0, ANALYTE, ANALYTE), z=0)
        diag.path(f"M {BX - 11} {neck_top} L {BX - 11} {shoulder} L {BX - 33} {base} L {BX + 33} {base} "
                  f"L {BX + 11} {shoulder} L {BX + 11} {neck_top}", style=solid(2.0), z=2)
        diag.polygon([(BX - 9, base - 7), (BX + 9, base - 7), (BX + 9, base - 1), (BX - 9, base - 1)],
                     style=solid(1.2, INK, GLASS), z=3)

        # Magnetic stirrer.
        diag.polygon([(BX - 60, base), (BX + 60, base), (BX + 60, bench), (BX - 60, bench)], style=solid(1.8, INK, "#BDBDBD"), z=1)
        diag.polygon([(BX + 38, base + 11), (BX + 48, base + 11), (BX + 48, base + 21), (BX + 38, base + 21)],
                     style=solid(1.2, INK, "#E6E6E6"), z=2)

        # Dimension leaders (to scale).
        k.dimension((BX + 8, y_ml(0)), (BX + 8, y_ml(50)), "$500$ mm  (0 to 50 mL)", offset=52, side=-1)
        k.dimension((BX + 33, neck_top), (BX + 33, base), "$145$ mm", offset=36, side=-1)

        # Labels.
        k.leader((BX - 8, y_ml(READING)), (230, y_ml(READING)), f"reading {READING:.2f} mL\n(bottom of meniscus,\nat eye level)", anchor="right_center")
        k.leader((BX + 18, stop_y + 5), (BX + 85, stop_y + 12), "stopcock", anchor="left_center")
        k.leader((BX - 1, tip_y - 8), (232, tip_y - 30), "tip 19 mm inside\nthe neck", anchor="right_center")
        k.leader((BX - 24, 545), (215, 520), "250 mL flask:\n25.00 mL HCl\n+ indicator", anchor="right_center")
        k.leader((BX - 5, base - 4), (225, base + 22), "stir bar", anchor="right_center")
        k.leader((BX + 40, base + 16), (BX + 85, base + 24), "magnetic stirrer", anchor="left_center")

        x0 = 570
        diag.text(
            "**Procedure**\n"
            "1  Rinse the burette with titrant, fill it, and run\n"
            "    some through the tip to clear air bubbles.\n"
            "2  Record the initial reading to 0.01 mL.\n"
            "3  Pipette 25.00 mL of acid into the flask, add\n"
            "    two drops of phenolphthalein, start the stirrer.\n"
            "4  Add titrant quickly at first, then dropwise as the\n"
            "    colour begins to linger; stop at the first\n"
            "    faint pink that lasts 30 seconds.\n"
            "5  Record the final reading; the titre is the\n"
            "    difference between the two readings.",
            size=13,
        ).at(x0, 110, anchor="top_left")
        diag.text(
            "**Result for this run**\n"
            "initial 0.00 mL, final 25.00 mL, titre 25.00 mL\n"
            "$n(\\ce{NaOH}) = 0.100 \\times 0.02500 = 2.50 \\times 10^{-3}$ mol\n"
            "$\\ce{HCl + NaOH -> NaCl + H2O}$ is 1 : 1, so\n"
            "$c(\\ce{HCl}) = 2.50 \\times 10^{-3} / 0.02500 = 0.100$ M",
            size=13,
        ).at(x0, 365, anchor="top_left")
        diag.text("Lengths are drawn to scale (1 mm = 0.62 px); tube widths are enlarged.", size=12, color="#555555").at(x0, 500, anchor="top_left")
        diag.caption("**Figure 8:** Titration apparatus: a 50 mL burette delivering titrant into a stirred flask, with the main dimensions",
                     small_caps=True)
    return diag


def build_diagram(output_dir: Path | str = "examples/chemistry") -> Path:
    return render_all(diagram(), output_dir, "08_titration_setup")["svg"]


if __name__ == "__main__":
    build_diagram(Path(sys.argv[1]) if len(sys.argv) > 1 else Path("examples/chemistry"))
