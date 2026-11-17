"""A reduced ordered binary decision diagram built from a truth table.

The function $f = x_1 x_2 + x_3$ is given only as its truth table. The script
builds the full decision tree in the order $x_1 < x_2 < x_3$ and reduces it by
the two standard rules: a node whose two branches lead to the same place is
removed, and nodes with identical variable and branches are shared. A dashed
edge is the low branch ($x_i = 0$), a solid edge the high branch ($x_i = 1$).
The result is checked against the table on all eight assignments.
"""
from __future__ import annotations

import itertools
import sys
from pathlib import Path

from diagrams_as_code import Diagram, Style
from diagrams_as_code.output import render_all

VARS = ["x1", "x2", "x3"]


def f(x1: int, x2: int, x3: int) -> int:
    return (x1 & x2) | x3


def build_robdd(table: dict[tuple[int, ...], int]):
    """Return (nodes, root, tree_size); nodes maps id -> (level, low, high), terminals are ids 0 and 1."""
    n = len(VARS)
    nodes: dict[int, tuple[int, int, int]] = {}
    unique: dict[tuple[int, int, int], int] = {}
    tree_size = 0

    def mk(level: int, prefix: tuple[int, ...]) -> int:
        nonlocal tree_size
        if level == n:
            return table[prefix]
        tree_size += 1
        low, high = mk(level + 1, prefix + (0,)), mk(level + 1, prefix + (1,))
        if low == high:  # rule 1: redundant test
            return low
        key = (level, low, high)
        if key not in unique:  # rule 2: share identical nodes
            unique[key] = len(nodes) + 2
            nodes[unique[key]] = key
        return unique[key]

    root = mk(0, ())
    return nodes, root, tree_size


def evaluate(nodes, root: int, bits: tuple[int, ...]) -> int:
    node = root
    while node > 1:
        level, low, high = nodes[node]
        node = high if bits[level] else low
    return node


def diagram() -> Diagram:
    table = {bits: f(*bits) for bits in itertools.product((0, 1), repeat=3)}
    nodes, root, tree_size = build_robdd(table)
    assert all(evaluate(nodes, root, b) == v for b, v in table.items())

    ox, top, dy, d = 480.0, 80.0, 100.0, 90.0
    pos: dict[int, tuple[float, float]] = {root: (ox, top)}
    # Place level by level: a child sits to the lower left or upper right of its parent.
    proposals: dict[int, list[float]] = {}
    for level in range(len(VARS)):
        for nid, (lv, low, high) in nodes.items():
            if lv != level:
                continue
            x = pos[nid][0]
            for child, side in ((low, -1), (high, 1)):
                proposals.setdefault(child, []).append(x + side * d)
        for child, xs in proposals.items():
            if child not in pos:
                lvl = nodes[child][0] if child > 1 else len(VARS)
                if lvl == level + 1 or (child <= 1 and level == len(VARS) - 1):
                    pos[child] = (sum(xs) / len(xs), top + lvl * dy)
    # Terminals reached early (like the 1 of x2) still hang on the bottom row.
    for t in (0, 1):
        if t in proposals and t not in pos:
            pos[t] = (sum(proposals[t]) / len(proposals[t]), top + len(VARS) * dy)

    with Diagram("Binary decision diagram", theme="paper") as diag:
        # Truth table on the left.
        tx, ty, cw, ch = 40.0, 60.0, 46.0, 30.0
        for j, h in enumerate(("$x_1$", "$x_2$", "$x_3$", "$f$")):
            diag.polygon(_rect(tx + j * cw, ty, cw, ch), h,
                         style=Style(fill="#D9DCE3" if j < 3 else "#B9BDC9", stroke_width=1.3, font_size=14))
        for i, (bits, val) in enumerate(table.items()):
            for j, v in enumerate((*bits, val)):
                diag.polygon(_rect(tx + j * cw, ty + (i + 1) * ch, cw, ch), str(v),
                             style=Style(fill="#BFD3EC" if (j == 3 and v) else "#FFFFFF", stroke_width=1.0, font_size=14))
        diag.text(r"$f = x_1 x_2 + x_3$", size=15).at(tx + 2 * cw, ty + 9 * ch + 20, anchor="top_center")

        # Decision nodes and terminals.
        shapes = {}
        for nid, (lv, low, high) in nodes.items():
            x, y = pos[nid]
            shapes[nid] = diag.shape(f"$x_{lv + 1}$", 46, 46, style=Style(radius=23, font_size=15, fill="#F3F3F3",
                                                                          stroke_width=1.6)).at(x, y, anchor="center")
        for t in (0, 1):
            x, y = pos[t]
            shapes[t] = diag.shape(str(t), 40, 40, style=Style(font_size=16, stroke_width=1.8,
                                                               fill="#BFD3EC" if t else "#FFFFFF")).at(x, y, anchor="center")
        for nid, (lv, low, high) in nodes.items():
            diag.connect(shapes[nid], shapes[low], routing="direct", style="dashed", width=1.3)
            diag.connect(shapes[nid], shapes[high], routing="direct", width=1.5)
        for k, name in enumerate(VARS):
            diag.text(f"${name[0]}_{name[1]}$", size=14, color="#666666").at(ox - 190, top + k * dy, anchor="center")
        diag.text("*terminals*", size=12, font="serif", color="#666666").at(ox - 190, top + len(VARS) * dy, anchor="center")

        # Legend.
        ly = top + len(VARS) * dy + 70
        diag.polyline([(ox - 170, ly), (ox - 120, ly)], style=Style(stroke="#111111", stroke_width=1.5), obstacle=False)
        diag.text("high branch, $x_i = 1$", size=12).at(ox - 110, ly, anchor="left_center")
        diag.polyline([(ox + 60, ly), (ox + 110, ly)], style=Style(stroke="#111111", stroke_width=1.3, dash="6,4"),
                      obstacle=False)
        diag.text("low branch, $x_i = 0$", size=12).at(ox + 120, ly, anchor="left_center")
        diag.text(
            f"The full decision tree has {tree_size} internal nodes; removing redundant tests and sharing "
            f"identical sub-diagrams leaves {len(nodes)}.",
            size=12, font="serif", italic=True, max_width=700,
        ).at(tx, ly + 34)
        diag.caption(
            "**Figure 7:** Reduced ordered BDD of $f = x_1 x_2 + x_3$, built from its truth table",
            small_caps=True,
        )
    return diag


def _rect(x: float, y: float, w: float, h: float) -> list[tuple[float, float]]:
    return [(x, y), (x + w, y), (x + w, y + h), (x, y + h)]


def build_diagram(output_dir: Path | str = "output/logic") -> Path:
    return render_all(diagram(), output_dir, "07_binary_decision_diagram")["svg"]


if __name__ == "__main__":
    dest = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("output/logic")
    build_diagram(dest)
