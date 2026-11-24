"""Example: Matrix organisation (ORGANISATION domain).

Functions run down the rows and product lines across the columns. Each specialist
sits in a cell and has two bosses: a solid line to the functional head (craft,
career, pay) and a dashed line to the product lead (priorities, day-to-day work).
"""
from __future__ import annotations

import sys
from pathlib import Path

from diagrams_as_code import Diagram, Port, Style
from diagrams_as_code.output import render_all

FUNCTIONS = ("Engineering", "Design", "Data Science", "Marketing")
PRODUCTS = ("Payments", "Lending", "Wealth")
#: headcount per (function, product) cell.
HEADCOUNT = (
    (14, 9, 6),
    (4, 3, 2),
    (3, 5, 4),
    (2, 3, 3),
)
HEAD = Style(fill="#D9E3F5", stroke="#2F4B86")
LEAD = Style(fill="#F8E6C8", stroke="#B8860B")
CELL = Style(fill="#FFFFFF", stroke="#6B7280")
FOCUS = Style(fill="#E4F1E8", stroke="#3C8D53", stroke_width=2.5)
CW, CH, GX, GY = 150.0, 62.0, 40.0, 22.0
X0, Y0 = 60.0, 230.0
HGAP = 130.0  # room for the solid line's label
HEAD_W = 150.0


def diagram() -> Diagram:
    with Diagram("Matrix organisation", theme="paper") as diag:
        gm = diag.shape("General Manager", 180, 46, style=HEAD).at(
            X0 + HEAD_W + HGAP + (3 * CW + 2 * GX) / 2 - 90, 40)
        leads = []
        for j, name in enumerate(PRODUCTS):
            x = X0 + HEAD_W + HGAP + j * (CW + GX)
            lead = diag.shape(f"{name}\nProduct Lead", CW, 52, style=LEAD).at(x, Y0 - 100)
            leads.append(lead)
            gm >> diag.edge(source_port=Port.SOUTH, target_port=Port.NORTH, arrow_head=False) >> lead

        heads = []
        cells: dict[tuple[int, int], object] = {}
        for i, name in enumerate(FUNCTIONS):
            y = Y0 + i * (CH + GY)
            heads.append(diag.shape(f"Head of\n{name}", HEAD_W, CH, style=HEAD).at(X0, y))
            for j in range(len(PRODUCTS)):
                x = X0 + HEAD_W + HGAP + j * (CW + GX)
                style = FOCUS if (i, j) == (0, 0) else CELL
                cells[i, j] = diag.shape(f"{name.split()[0]}\n{HEADCOUNT[i][j]} people", CW, CH, style=style).at(x, y)

        # One cell shows both bosses; its row and column neighbours are clear of the lines.
        focus = cells[0, 0]
        heads[0] >> diag.edge("craft, career, pay", arrow_head=False,
                              source_port=Port.EAST, target_port=Port.WEST) >> focus
        leads[0] >> diag.edge("priorities", style="dashed", color="#B8860B", arrow_head=False,
                              source_port=Port.SOUTH, target_port=Port.NORTH) >> focus

        diag.text("Highlighted cell: an engineer on Payments reports to the Head of Engineering (solid) "
                  "and takes priorities from the Payments lead (dashed).",
                  size=12).at(X0, Y0 + 4 * (CH + GY) + 14)
    return diag


def build_diagram(output_dir: Path | str = "examples/org") -> Path:
    return render_all(diagram(), output_dir, "02_matrix_organisation")["svg"]


if __name__ == "__main__":
    build_diagram(Path(sys.argv[1]) if len(sys.argv) > 1 else Path("examples/org"))
