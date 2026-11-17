"""Truth tables of four two-input Boolean functions.

Every output column is computed by the script from the function itself, so the
tables cannot disagree with the formulas printed above them. Rows with output 1
are shaded, which makes the shape of each function visible at a glance: AND has
one such row, NAND is its complement, OR has three and XOR has the two rows in
which the inputs differ.
"""
from __future__ import annotations

import itertools
import sys
from pathlib import Path

from diagrams_as_code import Diagram, Style
from diagrams_as_code.output import render_all

CELL_W, CELL_H = 46.0, 30.0
GAP = 46.0
TOP = 90.0
LEFT = 40.0
FUNCTIONS = [
    ("AND", r"$A \land B$", lambda a, b: a & b),
    ("OR", r"$A \lor B$", lambda a, b: a | b),
    ("XOR", r"$A \oplus B$", lambda a, b: a ^ b),
    ("NAND", r"$\neg(A \land B)$", lambda a, b: 1 - (a & b)),
]
HEAD = Style(fill="#D9DCE3", stroke_width=1.4, font_size=14)
ZERO = Style(fill="#FFFFFF", stroke_width=1.0, font_size=14)
ONE = Style(fill="#BFD3EC", stroke_width=1.0, font_size=14, text_color="#000000")
OUT_HEAD = Style(fill="#B9BDC9", stroke_width=1.4, font_size=14)


def rect(x: float, y: float, w: float, h: float) -> list[tuple[float, float]]:
    return [(x, y), (x + w, y), (x + w, y + h), (x, y + h)]


def diagram() -> Diagram:
    rows = list(itertools.product((0, 1), repeat=2))
    table_w = 3 * CELL_W
    with Diagram("Truth tables", theme="paper") as diag:
        for k, (name, formula, fn) in enumerate(FUNCTIONS):
            x0 = LEFT + k * (table_w + GAP)
            diag.text(f"**{name}**", size=16, align="center").at(x0 + table_w / 2, TOP - 50, anchor="center")
            diag.text(formula, size=14, align="center").at(x0 + table_w / 2, TOP - 28, anchor="center")
            for j, head in enumerate(("$A$", "$B$", "$Y$")):
                diag.polygon(rect(x0 + j * CELL_W, TOP, CELL_W, CELL_H), head, style=OUT_HEAD if j == 2 else HEAD)
            for i, (a, b) in enumerate(rows):
                y = fn(a, b)
                y0 = TOP + CELL_H * (i + 1)
                for j, value in enumerate((a, b, y)):
                    style = ONE if (y and j == 2) else ZERO
                    diag.polygon(rect(x0 + j * CELL_W, y0, CELL_W, CELL_H), str(value), style=style)
            ones = sum(fn(a, b) for a, b in rows)
            diag.text(f"{ones} of 4 rows are 1", size=11, font="serif", italic=True, align="center").at(
                x0 + table_w / 2, TOP + CELL_H * 5 + 12, anchor="top_center"
            )
        bottom = TOP + CELL_H * 5 + 40
        diag.text(
            "Inputs $A$ and $B$ run through all four combinations in binary order. "
            "NAND is the output column of AND inverted; XOR is 1 exactly when the inputs differ.",
            size=12, font="serif", italic=True,
            max_width=4 * table_w + 3 * GAP, align="center",
        ).at(LEFT, bottom)
        diag.caption(
            "**Figure 1:** Truth tables of AND, OR, XOR and NAND, with the rows whose output is 1 shaded",
            small_caps=True,
        )
    return diag


def build_diagram(output_dir: Path | str = "output/logic") -> Path:
    return render_all(diagram(), output_dir, "01_truth_tables")["svg"]


if __name__ == "__main__":
    dest = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("output/logic")
    build_diagram(dest)
