"""A stepped shaft with two geometric tolerance (GD&T) feature-control frames.

Datum A is the 20 mm journal axis. Frame 1 holds the 30 mm bearing seat to a
circular runout of 0.02 mm relative to A; frame 2 holds the shoulder face to
a perpendicularity of 0.05 mm relative to A. Axial positions and diameters are
drawn at 3 px per mm in the axial direction and 2.4 px per mm radially.
"""
from __future__ import annotations

import sys
from pathlib import Path

from diagrams_as_code import Diagram, Style
from diagrams_as_code.draft import Draft
from diagrams_as_code.output import render_all

KX, KR = 3.0, 2.4
STEPS = [(60.0, 40.0), (90.0, 30.0), (50.0, 20.0)]   # (length mm, diameter mm), left to right


def diagram() -> Diagram:
    x0, cy = 90.0, 300.0
    top, bot = [], []
    x = x0
    xs = [x0]
    for length, dia in STEPS:
        r = dia * KR / 2
        top += [(x, cy - r), (x + length * KX, cy - r)]
        bot += [(x, cy + r), (x + length * KX, cy + r)]
        x += length * KX
        xs.append(x)
    outline = top + bot[::-1]
    r1, r2, r3 = (s[1] * KR / 2 for s in STEPS)

    with Diagram("Stepped shaft with GD&T", theme="paper") as diag:
        k = Draft(diag, size=13)
        k.outline(outline, fill="#EEF0F4")
        # Shoulder edges drawn on top of the fill.
        k.centerline((x0 - 20, cy), (xs[-1] + 20, cy))

        # Diameter dimensions above, lengths below.
        k.dimension((xs[0], cy - r1), (xs[0], cy + r1), "", offset=34, side=1)
        diag.text("$\\emptyset 40$", size=13).at(xs[0] - 42, cy, anchor="right_center")
        k.dimension((xs[-1], cy - r3), (xs[-1], cy + r3), "", offset=34, side=-1)
        diag.text("$\\emptyset 20$", size=13).at(xs[-1] + 42, cy, anchor="left_center")
        for i, (length, _) in enumerate(STEPS):
            k.dimension((xs[i], cy + r1), (xs[i + 1], cy + r1), f"${length:g}$", offset=36 + 22 * (i % 2) + 40)
        k.dimension((xs[0], cy + r1), (xs[-1], cy + r1), "$200$", offset=150)

        # Datum A on the journal diameter (below the shaft, triangle + box).
        ax = xs[2] + 0.5 * STEPS[2][0] * KX
        tri = [(ax, cy + r3), (ax - 8, cy + r3 + 14), (ax + 8, cy + r3 + 14)]
        diag.polygon(tri, style=Style(fill="#1F2F57", stroke="#1F2F57", stroke_width=1.0), z=1)
        diag.path(f"M {ax:.1f} {cy + r3 + 14:.1f} L {ax:.1f} {cy + r3 + 28:.1f}", style=Style(fill="none", stroke="#1F2F57", stroke_width=1.0))
        k.gdt_frame((ax - 12, cy + r3 + 28), ["A"], height=24, cell_w=24)

        # Frame 1: circular runout of the 30 mm seat relative to A.
        mid2 = (xs[1] + xs[2]) / 2
        seat = (mid2 + 10, cy - r2)
        fx, fy = mid2 - 20, cy - r1 - 140
        k.d.path(f"M {seat[0]:.1f} {seat[1]:.1f} L {fx + 60:.1f} {fy + 24:.1f}",
                 style=Style(fill="none", stroke="#1F2F57", stroke_width=0.9))
        k.gdt_frame((fx, fy), ["$\\rightarrow$", "0.02", "A"], height=24, widths=[30, 52, 30])
        diag.text("circular runout", size=12).at(fx + 56, fy - 8, anchor="bottom_center")

        # Frame 2: perpendicularity of the 40/30 shoulder face relative to A.
        sh = (xs[1], cy - (r1 + r2) / 2)
        gx, gy = xs[0] - 10, cy - r1 - 140
        k.d.path(f"M {sh[0]:.1f} {sh[1]:.1f} L {gx + 60:.1f} {gy + 24:.1f}",
                 style=Style(fill="none", stroke="#1F2F57", stroke_width=0.9))
        k.gdt_frame((gx, gy), ["⊥", "0.05", "A"], height=24, widths=[30, 52, 30])
        diag.text("perpendicularity", size=12).at(gx + 56, gy - 8, anchor="bottom_center")

        diag.text("Dimensions in mm. Frames read: symbol, tolerance zone, datum.", size=12).at(
            x0, cy + 240, anchor="left_center")
        diag.caption(
            "**Figure 2:** Stepped shaft with two feature-control frames referenced to datum A",
            small_caps=True,
        )
    return diag


def build_diagram(output_dir: Path | str = "examples/engineering") -> Path:
    return render_all(diagram(), output_dir, "02_shaft_gdt")["svg"]


if __name__ == "__main__":
    dest = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("examples/engineering")
    build_diagram(dest)
