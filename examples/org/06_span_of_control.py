"""Example: Span of control, flat versus tall (ORGANISATION domain).

The same 31 people organised two ways: a flat hierarchy with a span of 5 (three
levels) and a tall one with a span of 2 (five levels). Wider spans cut the layers a
decision must cross but load each manager with more direct reports.
"""
from __future__ import annotations

import sys
from pathlib import Path

from diagrams_as_code import Diagram, Port, Style
from diagrams_as_code.output import render_all

SLOT, BW, BH = 36.0, 26.0, 20.0
X0 = 60.0
ROOT = Style(fill="#2F4B86", stroke="#2F4B86")
MANAGER = Style(fill="#D9E3F5", stroke="#2F4B86")
WORKER = Style(fill="#FFFFFF", stroke="#6B7280")


def draw_tree(diag: Diagram, span: int, depth: int, x0: float, y0: float, row_h: float, tag: str) -> None:
    next_slot = [0]
    placed: list[tuple[object, int]] = []  # (shape, level) in left-to-right order per level

    def place(level: int) -> float:
        """Place a subtree rooted at ``level``; return the root's centre x."""
        if level == depth - 1:
            cx = x0 + (next_slot[0] + 0.5) * SLOT
            next_slot[0] += 1
        else:
            kids = [place(level + 1) for _ in range(span)]
            cx = (kids[0] + kids[-1]) / 2
        style = ROOT if level == 0 else (WORKER if level == depth - 1 else MANAGER)
        node = diag.shape("", BW, BH, style=style, id=f"{tag}_{len(placed)}").at(cx - BW / 2, y0 + level * row_h)
        placed.append((node, level))
        return cx

    place(0)
    # Edges: the k-th manager on a level owns the k-th block of `span` shapes on the next level.
    by_level: dict[int, list] = {}
    for node, level in placed:
        by_level.setdefault(level, []).append(node)
    for level in range(depth - 1):
        children = by_level[level + 1]
        for k, node in enumerate(by_level[level]):
            for child in children[k * span:(k + 1) * span]:
                node >> diag.edge(source_port=Port.SOUTH, target_port=Port.NORTH, arrow_head=False,
                                  clearance=4) >> child


def diagram() -> Diagram:
    flat_w = 25 * SLOT
    tall_w = 16 * SLOT
    with Diagram("Span of control: flat versus tall", theme="paper") as diag:
        diag.text("**Flat: span of 5, 3 levels**", size=15).at(X0, 70)
        draw_tree(diag, 5, 3, X0, 110, 70, "flat")
        tall_x = X0 + (flat_w - tall_w) / 2
        diag.text("**Tall: span of 2, 5 levels**", size=15).at(X0, 330)
        draw_tree(diag, 2, 5, tall_x, 370, 62, "tall")

        sx = X0 + flat_w + 50
        diag.text("**Flat**\n31 people\nEvery manager has 5 reports\n"
                  "A decision crosses 2 levels\nManagers: 6 (19%)\nRisk: thin coaching, wide load",
                  size=13).at(sx, 110)
        diag.text("**Tall**\n31 people\nEvery manager has 2 reports\n"
                  "A decision crosses 4 levels\nManagers: 15 (48%)\nRisk: slow, filtered communication",
                  size=13).at(sx, 370)
    return diag


def build_diagram(output_dir: Path | str = "examples/org") -> Path:
    return render_all(diagram(), output_dir, "06_span_of_control")["svg"]


if __name__ == "__main__":
    build_diagram(Path(sys.argv[1]) if len(sys.argv) > 1 else Path("examples/org"))
