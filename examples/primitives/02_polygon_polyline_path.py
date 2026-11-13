"""Polygons, polylines and free paths (PRIM-02)."""
from __future__ import annotations

import sys
from pathlib import Path

from diagrams_as_code import Diagram, Style
from diagrams_as_code.output import render_all


def diagram() -> Diagram:
    grey = Style(fill="#E6E6E6")
    with Diagram("Polygons, polylines and paths", theme="paper") as diag:
        # Drawn where its own coordinates say.
        diag.polygon([(60, 140), (120, 60), (180, 140)], "A", style=grey)
        # The same kind of outline, placed like any shape.
        hexagon = diag.polygon(
            [(30, 0), (90, 0), (120, 45), (90, 90), (30, 90), (0, 45)], "hex", style=grey
        ).at(230, 55)
        diag.polyline(
            [(0, 40), (25, 40), (35, 10), (55, 70), (65, 40), (110, 40)],
            style=Style(stroke_width=1.5),
        ).right_of(hexagon, margin=50)
        # SVG path data: lines, curves and arcs.
        diag.path("M 0 60 Q 40 -20 80 60 T 160 60", style=Style(fill="none", stroke_width=1.5)).at(60, 190)
        lens = diag.path(
            "M 0 40 A 60 60 0 0 1 100 40 A 60 60 0 0 1 0 40 Z", "lens", style=grey
        ).at(280, 185)
        diag.path(
            "M 10 0 H 90 A 10 10 0 0 1 100 10 V 50 A 10 10 0 0 1 90 60 H 10 A 10 10 0 0 1 0 50 V 10 A 10 10 0 0 1 10 0 Z",
            "rounded", style=Style(dash="5,3"),
        ).right_of(lens, margin=50)
        diag.caption("**Figure 2:** Outlines from points and from path data", small_caps=True)
    return diag


def build_diagram(output_dir: Path | str = "output/primitives") -> Path:
    return render_all(diagram(), output_dir, "02_polygon_polyline_path")["svg"]


if __name__ == "__main__":
    dest = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("output/primitives")
    build_diagram(dest)
