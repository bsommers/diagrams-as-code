"""Edge weights, arrowhead styles and two-way arrows (PRIM-05)."""
from __future__ import annotations

import sys
from pathlib import Path

from diagrams_as_code import Diagram
from diagrams_as_code.output import render_all


HEADS = ("triangle", "stealth", "open", "diamond", "circle", "bar")


def diagram() -> Diagram:
    with Diagram("Edge weights and arrowheads", theme="paper") as diag:
        diag.text("**Arrowheads**").at(60, 40)
        for row, head in enumerate(HEADS):
            y = 70 + row * 42
            a = diag.shape(head, 90, 30).at(60, y)
            b = diag.shape("", 40, 30).at(300, y)
            a >> diag.edge(head=head) >> b

        diag.text("**Weights and sizes**").at(420, 40)
        for row, (width, size, note) in enumerate(
            [(0.75, 1.0, "0.75 px"), (1.5, 1.0, "1.5 px"), (3.0, 1.0, "3 px spine"), (1.0, 2.0, "1 px, 2x head")]
        ):
            y = 70 + row * 42
            a = diag.shape(note, 110, 30).at(420, y)
            b = diag.shape("", 40, 30).at(680, y)
            a >> diag.edge(width=width, arrow_size=size) >> b

        left = diag.shape("request", 110, 30).at(420, 248)
        right = diag.shape("", 40, 30).at(680, 248)
        left >> diag.edge(two_way=True, head="stealth", tail="stealth", width=1.5) >> right
        more = diag.shape("stage 1", 110, 30).at(420, 290)
        last = diag.shape("n", 40, 30).at(680, 290)
        more >> diag.edge(ellipsis=True, width=1.0) >> last
        diag.caption("**Figure 5:** Line weights, arrowheads, a two-way arrow and an ellipsis", small_caps=True)
    return diag


def build_diagram(output_dir: Path | str = "output/primitives") -> Path:
    return render_all(diagram(), output_dir, "05_edge_weights_and_arrowheads")["svg"]


if __name__ == "__main__":
    dest = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("output/primitives")
    build_diagram(dest)
