"""Reference sheet for the thirteen ``project_management`` icons.

Every cell shows one icon from ``ShapeLibrary`` at presentation size, with its
name underneath (the string you pass as ``Shape(..., icon="name")``) and a
24 px copy beside it, the size the glyphs are drawn for. The names and the
descriptions come from ``ShapeLibrary._ICON_CATALOG``, so adding an icon to the
domain adds it to this sheet and a renamed icon cannot leave a stale label.
"""
from __future__ import annotations

import sys
from pathlib import Path

from diagrams_as_code import Diagram, Shape
from diagrams_as_code.output import render_all
from diagrams_as_code.shapes import ShapeLibrary
from diagrams_as_code.style import Style

DOMAIN = "project_management"
COLS = 5
CELL_W, CELL_H, GAP = 204, 150, 12
X0, Y0 = 40, 40
BIG, SMALL = 56, 24
INK, GREY = "#2F3B52", "#6B7280"


def rect(x0, y0, x1, y1):
    return [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]


def icons() -> list[tuple[str, str]]:
    """(name, description) for every icon in the domain, sorted by name."""
    items = [(n, d) for n, (dom, d) in ShapeLibrary._ICON_CATALOG.items() if dom == DOMAIN]
    return sorted(items)


def diagram() -> Diagram:
    items = icons()
    with Diagram("Project management icon set", theme="pastel_light") as diag:
        for i, (name, description) in enumerate(items):
            col, row = i % COLS, i // COLS
            x = X0 + col * (CELL_W + GAP)
            y = Y0 + row * (CELL_H + GAP)
            diag.polygon(rect(x, y, x + CELL_W, y + CELL_H),
                         style=Style(fill="#FFFFFF", stroke="#C9CED6", stroke_width=1.0), z=-1)
            big = Shape(f"big_{name}", name, icon=name, kind="icon", width=BIG + 24, height=BIG + 24,
                        metadata={"icon_size": BIG, "icon_color": INK})
            diag.add(big)
            big.at(x + CELL_W / 2, y + 14, anchor="top_center")
            small = Shape(f"small_{name}", "", icon=name, kind="icon", width=SMALL, height=SMALL,
                          metadata={"icon_size": SMALL, "icon_color": GREY})
            diag.add(small)
            small.at(x + CELL_W - 10, y + 10, anchor="top_right")
            diag.text(description, size=9.5, color=GREY).at(
                x + CELL_W / 2, y + CELL_H - 18, anchor="center")
        diag.caption(
            f"**Figure 12:** the {len(items)} icons of the {DOMAIN} domain, 24x24 grid, 2 px stroke, "
            "shown at 56 px and at their native 24 px",
            small_caps=True, max_width=900,
        )
    return diag


def build_diagram(output_dir: Path | str = "examples/project_management") -> Path:
    return render_all(diagram(), output_dir, "12_icon_set_reference")["svg"]


if __name__ == "__main__":
    dest = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("examples/project_management")
    build_diagram(dest)
