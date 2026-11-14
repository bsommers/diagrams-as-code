"""align(), distribute(), grid snap and lengths in mm and pt (PRIM-09)."""
from __future__ import annotations

import sys
from pathlib import Path

from diagrams_as_code import Diagram, align, distribute, mm
from diagrams_as_code.output import render_all


def diagram() -> Diagram:
    with Diagram("Alignment, grid and units", theme="paper", grid=10) as diag:
        # Lengths may carry units; the grid then pulls every corner to 10 px.
        first = diag.shape("90 pt x 12 mm", "90pt", "12mm").at("15mm", "15mm")
        row = [first] + [diag.shape(name, "90pt", "12mm") for name in ("B", "C", "D")]
        distribute(row, "right", gap=30)

        tall = [diag.shape(name, 90, height) for name, height in (("short", 40), ("medium", 70), ("tall", 100))]
        tall[0].below(first, margin=mm(26), align="left")
        distribute(tall, "right", gap=30, align="bottom")

        stack = [diag.shape(name, width, 34) for name, width in (("wide", 160), ("mid", 110), ("narrow", 70))]
        stack[0].right_of(tall[-1], margin=60, align="bottom")
        distribute(stack, "above", gap=12, align="right")
        note = diag.text("bottoms aligned  |  right edges aligned", size="9pt")
        note.below(tall[0], margin=20, align="left")
        align([tall[0], note], "left")
        diag.caption("**Figure 9:** Rows and columns set out with align() and distribute()", small_caps=True)
    return diag


def build_diagram(output_dir: Path | str = "output/primitives") -> Path:
    return render_all(diagram(), output_dir, "09_align_distribute_units")["svg"]


if __name__ == "__main__":
    dest = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("output/primitives")
    build_diagram(dest)
