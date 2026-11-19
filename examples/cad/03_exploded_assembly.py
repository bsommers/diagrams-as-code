"""Exploded bolted joint with numbered balloons and a parts list.

An M10 x 40 hex bolt clamps a 12 mm plate through a washer and a nut. The
stack is drawn in half section along one centreline, pulled apart by a fixed
gap. Grip length and thread projection are computed from the part sizes.
"""
from __future__ import annotations

import sys
from pathlib import Path

from diagrams_as_code import Diagram, Style
from diagrams_as_code.draft import Draft
from diagrams_as_code.output import render_all

S = 4.0  # px per mm
INK = "#1F2F57"
D_BOLT, L_BOLT, AF, K_HEAD = 10.0, 40.0, 17.0, 6.4
PL_W, PL_T, PL_HOLE = 60.0, 12.0, 11.0
WA_OD, WA_ID, WA_T = 20.0, 10.5, 2.0
NUT_M = 8.4
GAP = 34.0
CX = 230.0


def rect(x0, y0, x1, y1):
    return [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]


def diagram() -> Diagram:
    grip = PL_T + WA_T
    proj = L_BOLT - grip - NUT_M
    with Diagram("Exploded bolted joint", theme="paper") as diag:
        k = Draft(diag)
        y = 40.0
        parts = {}

        def band(tag, h):
            nonlocal y
            parts[tag] = (y, y + h)
            y += h + GAP

        band("bolt", (K_HEAD + L_BOLT) * S)
        band("plate", PL_T * S)
        band("washer", WA_T * S)
        band("nut", NUT_M * S)
        face = Style(fill="#DCE6F2", stroke=INK, stroke_width=2.0)

        def section(poly):
            diag.polygon(poly, style=face, z=-3)
            k.hatch(poly, angle=45, gap=6)

        # Bolt: hex head (elevation) and threaded shank.
        y0, y1 = parts["bolt"]
        hh = K_HEAD * S
        diag.polygon(rect(CX - AF * S / 2, y0, CX + AF * S / 2, y0 + hh), style=face)
        diag.polygon(rect(CX - D_BOLT * S / 2, y0 + hh, CX + D_BOLT * S / 2, y1), style=face)
        for t in range(int(y0 + hh + 10), int(y1 - 8), 7):
            k.d.path(f"M {CX - D_BOLT * S / 2} {t} L {CX + D_BOLT * S / 2} {t - 3}",
                     style=Style(fill="none", stroke=INK, stroke_width=0.7))
        # Plate in half section: two hatched halves around the hole.
        y0, y1 = parts["plate"]
        for sgn in (-1, 1):
            xa, xb = sorted((CX + sgn * PL_HOLE * S / 2, CX + sgn * PL_W * S / 2))
            section(rect(xa, y0, xb, y1))
        # Washer.
        y0, y1 = parts["washer"]
        for sgn in (-1, 1):
            xa, xb = sorted((CX + sgn * WA_ID * S / 2, CX + sgn * WA_OD * S / 2))
            section(rect(xa, y0, xb, y1))
        # Nut (hole at the thread minor diameter, 8.4).
        y0, y1 = parts["nut"]
        for sgn in (-1, 1):
            xa, xb = sorted((CX + sgn * 8.4 * S / 2, CX + sgn * AF * S / 2))
            section(rect(xa, y0, xb, y1))
        # Centreline and explode lines.
        k.centerline((CX, 18), (CX, y - GAP + 22))
        # Balloons and leaders.
        bx = CX + 190
        marks = [("bolt", 1, (CX + AF * S / 2, parts["bolt"][0] + 12)),
                 ("plate", 2, (CX + PL_W * S / 2, sum(parts["plate"]) / 2)),
                 ("washer", 3, (CX + WA_OD * S / 2, sum(parts["washer"]) / 2)),
                 ("nut", 4, (CX + AF * S / 2, sum(parts["nut"]) / 2))]
        for tag, n, tip in marks:
            by = sum(parts[tag]) / 2 if tag != "bolt" else parts[tag][0] + 40
            k.d.path(f"M {tip[0]} {tip[1]} L {bx - 14} {by}",
                     style=Style(fill="none", stroke=INK, stroke_width=0.8))
            diag.path(f"M {bx - 14} {by} a 14 14 0 1 0 28 0 a 14 14 0 1 0 -28 0",
                      style=Style(fill="#FFFFFF", stroke=INK, stroke_width=1.3), z=2)
            diag.text(str(n), size=13, z=3).at(bx, by, anchor="center")
        # Dimensions on the bolt and plate.
        k.dimension((CX - AF * S / 2, parts["bolt"][0] + hh), (CX - AF * S / 2, parts["bolt"][1]),
                    f"$L = {L_BOLT:g}$", offset=44, side=1)
        k.dimension((CX - PL_W * S / 2, parts["plate"][0]), (CX - PL_W * S / 2, parts["plate"][1]),
                    f"${PL_T:g}$", offset=34, side=1)
        # Parts list.
        tx, ty = bx + 70, 70.0
        cols = [("ITEM", 44), ("QTY", 40), ("DESCRIPTION", 210)]
        rows = [("1", "1", f"Hex bolt M10 $\\times$ {L_BOLT:g}"),
                ("2", "1", f"Plate {PL_W:g} $\\times$ {PL_T:g}, $\\emptyset{PL_HOLE:g}$ hole"),
                ("3", "1", f"Washer $\\emptyset{WA_ID:g}$ / $\\emptyset{WA_OD:g}$ $\\times$ {WA_T:g}"),
                ("4", "1", f"Hex nut M10, $m = {NUT_M:g}$")]
        rh = 28.0
        cell = Style(fill="#FFFFFF", stroke=INK, stroke_width=1.0)
        hdr = Style(fill="#E6ECF5", stroke=INK, stroke_width=1.0)
        for r, row in enumerate([tuple(c[0] for c in cols)] + rows):
            x = tx
            for (title, w), txt in zip(cols, row):
                diag.polygon(rect(x, ty + r * rh, x + w, ty + (r + 1) * rh), style=hdr if r == 0 else cell)
                diag.text(txt, size=11).at(x + 8 if title == "DESCRIPTION" else x + w / 2, ty + r * rh + rh / 2,
                                           anchor="left_center" if title == "DESCRIPTION" else "center")
                x += w
        diag.text(f"Grip length $= {PL_T:g} + {WA_T:g} = {grip:g}$ mm.\n"
                  f"Thread projecting past the nut $= {L_BOLT:g} - {grip:g} - {NUT_M:g} = {proj:.1f}$ mm.",
                  size=12).at(tx, ty + 6 * rh, anchor="top_left")
        diag.caption(
            "**Figure 3:** Exploded view of a bolted joint with numbered balloons, centreline and parts list; the plate, washer and nut are cut in half section",
            small_caps=True)
    return diag


def build_diagram(output_dir: Path | str = "examples/cad") -> Path:
    return render_all(diagram(), output_dir, "03_exploded_assembly")["svg"]


if __name__ == "__main__":
    dest = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("examples/cad")
    build_diagram(dest)
