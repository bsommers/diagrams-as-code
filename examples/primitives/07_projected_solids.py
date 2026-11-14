"""Solids in oblique and isometric projection, with hidden edges and a cutting plane (PRIM-07)."""
from __future__ import annotations

import sys
from pathlib import Path

from diagrams_as_code import Diagram, Style
from diagrams_as_code.solids import Solid, isometric, oblique
from diagrams_as_code.output import render_all


def diagram() -> Diagram:
    glass = Style(fill="#DCE6F2", fill_opacity=0.55)
    with Diagram("Projected solids", theme="paper") as diag:
        box = diag.cuboid("cuboid, oblique", 120, 80, 90, style=Style(fill="#F2F2F2")).at(60, 60)
        iso = diag.solid(
            Solid.box(100, 60, 100), "cuboid, isometric", projection=isometric(), style=glass
        ).right_of(box, margin=60, align="bottom")
        octahedron = Solid.hull([(60, 0, 0), (-60, 0, 0), (0, 70, 0), (0, -70, 0), (0, 0, 60), (0, 0, -60)])
        cut = diag.solid(
            octahedron, "polyhedron with a cutting plane", projection=oblique(30, 0.6),
            style=glass, cut=((0, 15, 0), (0, 1, 0)), cut_size=95,
        ).right_of(iso, margin=60, align="bottom")
        prism = diag.solid(
            Solid.prism([(0, 0), (90, 0), (45, 70)], 110), "prism", projection=oblique(40, 0.5),
            hidden="none", style=Style(fill="#F2F2F2"),
        ).right_of(cut, margin=60, align="bottom")
        diag.caption("**Figure 7:** Convex solids; edges behind the solid are dashed", small_caps=True)
    return diag


def build_diagram(output_dir: Path | str = "output/primitives") -> Path:
    return render_all(diagram(), output_dir, "07_projected_solids")["svg"]


if __name__ == "__main__":
    dest = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("output/primitives")
    build_diagram(dest)
