"""Planar CMOS inverter in cross-section: PMOS in an n-well beside an NMOS (SEMICONDUCTOR domain).

Both transistors share one polysilicon gate signal (V_in); their drains are tied
together by metal 1 (V_out); the PMOS source goes to V_DD and the NMOS source to
ground. Layers are labelled in the order a fab builds them: well, shallow trench
isolation (STI), gate oxide and poly, spacers, source/drain implants, contacts
and the first metal. Schematic cross-section, not to scale: vertical features
are exaggerated, the gate contact lies out of the plane, and the well and
substrate taps are omitted.
"""
from __future__ import annotations

import sys
from pathlib import Path

from diagrams_as_code import Diagram, Style
from diagrams_as_code.draft import Draft
from diagrams_as_code.output import render_all

INK = "#1F2F57"
OX, OY = 130.0, 50.0  # origin of the drawing (surface y = OY + 200 before offset)
SURF = 200.0
SI, NWELL, STI = "#CDD2DA", "#EAD7B0", "#BBD6EE"
POLY, SPACER, GOX = "#D77C74", "#6FA8A0", "#27408B"
PPLUS, NPLUS = "#F3B6C8", "#B5D8A5"
ILD, W_PLUG, METAL = "#F4F4F4", "#555555", "#E2A95B"


def diagram() -> Diagram:
    with Diagram("Planar CMOS inverter, cross-section (schematic, not to scale)", theme="paper") as diag:
        k = Draft(diag, size=11.5)

        def poly(pts, fill, z=-3, hatch=None, width=1.0):
            p = [(OX + x, OY + y) for x, y in pts]
            diag.polygon(p, style=Style(fill=fill, stroke=INK, stroke_width=width), z=z)
            if hatch:
                k.hatch(p, angle=hatch, gap=6, width=0.5)

        def box(x0, y0, x1, y1, fill, **kw):
            poly([(x0, y0), (x1, y0), (x1, y1), (x0, y1)], fill, **kw)

        def pt(x, y):
            return (OX + x, OY + y)

        # Interlayer dielectric over everything, then the silicon and its wells.
        box(10, 95, 740, SURF, ILD, z=-5)
        box(10, SURF, 740, 330, SI, z=-5)
        box(30, SURF, 370, 285, NWELL, z=-4)
        # shallow trench isolation
        for a, b in ((20, 70), (330, 410), (670, 730)):
            box(a, SURF - 3, b, SURF + 42, STI, z=-3, hatch=45)
        # source / drain implants
        for a, b in ((90, 160), (240, 310)):
            box(a, SURF, b, SURF + 20, PPLUS)
        for a, b in ((430, 500), (580, 650)):
            box(a, SURF, b, SURF + 20, NPLUS)
        # gate oxide, poly gates and spacers (PMOS channel 160-240, NMOS 500-580)
        for g0, g1 in ((160, 240), (500, 580)):
            box(g0, SURF - 4, g1, SURF, GOX)
            box(g0, SURF - 40, g1, SURF - 4, POLY)
            poly([(g0 - 10, SURF - 4), (g0, SURF - 4), (g0, SURF - 30), (g0 - 10, SURF - 4)], SPACER, z=-2)
            poly([(g1, SURF - 4), (g1 + 10, SURF - 4), (g1, SURF - 30), (g1, SURF - 4)], SPACER, z=-2)
        # tungsten contacts and metal 1
        for cx in (125, 275, 465, 615):
            box(cx - 10, 118, cx + 10, SURF, W_PLUG, z=-2)
        box(95, 98, 155, 118, METAL, z=-2)    # VDD
        box(255, 98, 485, 118, METAL, z=-2)   # Vout ties both drains
        box(595, 98, 655, 118, METAL, z=-2)   # GND

        # ---- labels (leaders) -------------------------------------------------
        k.leader(pt(60, 310), pt(-20, 330), "p-type substrate", anchor="right_center")
        k.leader(pt(50, 265), pt(-20, 265), "n-well", anchor="right_center")
        k.leader(pt(45, SURF + 25), pt(-20, 220), "STI (SiO$_2$)", anchor="right_center")
        k.leader(pt(100, SURF + 10), pt(-20, 195), "p+ source", anchor="right_center")
        k.leader(pt(465, SURF + 14), pt(465, 285), "n+ drain", anchor="top_center")
        k.leader(pt(275, SURF + 14), pt(275, 250), "p+ drain", anchor="top_center")
        k.leader(pt(640, SURF + 10), pt(780, 235), "n+ source", anchor="left_center")
        k.leader(pt(200, SURF - 30), pt(200, 62), "poly-Si gate", anchor="center")
        k.leader(pt(165, SURF - 18), pt(65, 165), "spacer", anchor="right_center")
        k.leader(pt(618, 160), pt(780, 160), "W contact", anchor="left_center")
        k.leader(pt(660, 108), pt(780, 108), "metal 1 (Cu)", anchor="left_center")
        k.leader(pt(540, SURF - 2), pt(780, 200), "gate oxide (thin)", anchor="left_center")

        for x, t in ((125, "$V_{DD}$"), (370, "$V_{out}$"), (625, "GND")):
            diag.text(t, size=13).at(OX + x, OY + 80, anchor="bottom_center")
        diag.text("PMOS", size=14).at(OX + 200, OY + 335, anchor="top_center")
        diag.text("NMOS", size=14).at(OX + 540, OY + 335, anchor="top_center")
        diag.text("gate poly runs to a contact out of the plane: $V_{in}$ drives both gates",
                  size=11.5, color="#444444").at(OX + 370, OY + 360, anchor="top_center")
        k.dimension(pt(500, SURF - 40), pt(580, SURF - 40), "$L$", offset=-22, side=1)
        diag.caption("**Figure 3:** Planar bulk CMOS inverter. Schematic cross-section, not to scale; "
                     "taps and the gate contact are omitted.", small_caps=True)
    return diag


def build_diagram(output_dir: Path | str = "examples/semiconductor") -> Path:
    return render_all(diagram(), output_dir, "03_cmos_inverter_cross_section")["svg"]


if __name__ == "__main__":
    dest = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("examples/semiconductor")
    build_diagram(dest)
