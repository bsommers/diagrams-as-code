"""Paint order with z (PRIM-08)."""
from __future__ import annotations

import sys
from pathlib import Path

from diagrams_as_code import Diagram, Style
from diagrams_as_code.output import render_all


def diagram() -> Diagram:
    with Diagram("Z-order", theme="paper") as diag:
        # z below zero: painted under the edges, a backdrop.
        diag.polygon(
            [(40, 50), (430, 50), (430, 230), (40, 230)], z=-1, obstacle=False,
            style=Style(fill="#EFEFEF", stroke="none"),
        )
        a = diag.shape("Source", 110, 46).at(70, 115)
        b = diag.shape("Sink", 110, 46).at(290, 115)
        a >> diag.edge(width=1.5) >> b

        # Equal z keeps declaration order; a higher z comes forward.
        # (Declared out of order on purpose: z decides, not the order written.)
        card = dict(width=120, height=70, label_position="top", obstacle=False)
        diag.shape("z = 2", style=Style(fill="#DDDDDD"), z=2, **card).at(560, 126)
        diag.shape("z = 0", style=Style(fill="#FFFFFF"), **card).at(480, 70)
        diag.shape("z = 1", style=Style(fill="#F4F4F4"), z=1, **card).at(520, 98)

        # An edge with z above zero is drawn over the nodes.
        cover = diag.shape("", 60, 150, style=Style(fill="#F4F4F4"), obstacle=False).at(190, 300)
        diag.connect((70, 375), (400, 375), routing="direct", width=1.5, z=1)
        diag.text("an edge with z = 1 crosses over the box", size=11).at(70, 465)
        diag.caption("**Figure 8:** Backdrops, stacking and edges drawn on top", small_caps=True)
    return diag


def build_diagram(output_dir: Path | str = "output/primitives") -> Path:
    return render_all(diagram(), output_dir, "08_z_order")["svg"]


if __name__ == "__main__":
    dest = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("output/primitives")
    build_diagram(dest)
