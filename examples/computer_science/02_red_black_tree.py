"""A red-black tree of ten keys, with its NIL leaves drawn.

The keys are in binary-search-tree order (every left subtree smaller, every
right subtree larger), and the colouring satisfies the red-black invariants:
the root and the NIL leaves are black, no red node has a red child, and every
path from the root to a NIL leaf passes the same number of black nodes. One
such path is drawn heavy. The horizontal position of each node is its rank in
an in-order walk, so the picture reads left to right as the sorted sequence.
"""
from __future__ import annotations

import sys
from pathlib import Path

from diagrams_as_code import Diagram, Style
from diagrams_as_code.output import render_all

# key -> (colour, left child, right child); None is a NIL leaf.
TREE = {
    13: ("B", 8, 17),
    8: ("R", 1, 11),
    17: ("R", 15, 25),
    1: ("B", None, 6),
    11: ("B", None, None),
    15: ("B", None, None),
    25: ("B", 22, 27),
    6: ("R", None, None),
    22: ("R", None, None),
    27: ("R", None, None),
}
ROOT = 13
HIGHLIGHT = (13, 17, 25, 22)  # a root-to-NIL path; the NIL is 22's left leaf
X0, STEP, TOP, LEVEL = 70.0, 42.0, 70.0, 82.0
D = 44.0  # node diameter
RED = Style(radius=D / 2, fill="#C62828", stroke="#7F1414", text_color="#FFFFFF", font_size=15)
BLACK = Style(radius=D / 2, fill="#1A1A1A", stroke="#000000", text_color="#FFFFFF", font_size=15)
NIL = Style(fill="#1A1A1A", stroke="#000000", text_color="#FFFFFF", font_size=9)
LINE = {"routing": "direct", "arrow_head": False, "width": 1.0}
HEAVY = {"routing": "direct", "arrow_head": False, "width": 3.0}


def inorder_slots() -> list[tuple[object, int, object]]:
    """(item, depth, parent) in in-order, NIL leaves included as ('NIL', parent, side)."""
    out: list[tuple[object, int, object]] = []

    def walk(key, depth, parent, side):
        if key is None:
            out.append((("NIL", parent, side), depth, parent))
            return
        _, left, right = TREE[key]
        walk(left, depth + 1, key, "L")
        out.append((key, depth, parent))
        walk(right, depth + 1, key, "R")

    walk(ROOT, 0, None, None)
    return out


def diagram() -> Diagram:
    slots = inorder_slots()
    keys = [item for item, _, _ in slots if not isinstance(item, tuple)]
    assert keys == sorted(keys), "the tree must be a valid BST"
    with Diagram("Red-black tree with NIL leaves", theme="paper") as diag:
        nodes: dict[object, object] = {}
        for index, (item, depth, _) in enumerate(slots):
            x, y = X0 + index * STEP, TOP + depth * LEVEL
            if isinstance(item, tuple):
                nodes[item] = diag.shape("NIL", 30, 18, style=NIL).at(x, y - 10, anchor="center")
            else:
                colour = TREE[item][0]
                nodes[item] = diag.shape(str(item), D, D, style=RED if colour == "R" else BLACK).at(
                    x, y, anchor="center")

        heavy_pairs = set(zip(HIGHLIGHT, HIGHLIGHT[1:])) | {(22, ("NIL", 22, "L"))}
        for item, _, parent in slots:
            if parent is None:
                continue
            child = nodes[item]
            key = item if not isinstance(item, tuple) else item
            options = HEAVY if (parent, key) in heavy_pairs else LINE
            diag.connect(nodes[parent].anchor("bottom", 0.5), child.anchor("top", 0.5), **options)

        right = X0 + (len(slots) - 1) * STEP
        diag.text(
            "**Invariants**\n"
            "1. Every node is red or black.\n"
            "2. The root and every NIL leaf are black.\n"
            "3. A red node has two black children.\n"
            "4. All root-to-NIL paths pass the same\nnumber of black nodes: black-height\n"
            "$bh(13) = 2$ (heavy path: 13, 17, 25, 22, NIL).",
            size=12,
        ).at(right - 250, TOP - 30)
        diag.text(
            "With $n$ keys the height is at most $2\\,\\mathrm{log}_2 (n + 1)$, so\n"
            "search, insert and delete run in $O(\\log n)$; insert needs\n"
            "at most 2 rotations, delete at most 3.",
            size=12, font="serif", italic=True,
        ).at(X0 - 20, TOP + 4 * LEVEL + 20)
        diag.text("in-order walk: $1 < 6 < 8 < 11 < 13 < 15 < 17 < 22 < 25 < 27$", size=12, color="#555555").at(
            right + 20, TOP + 4 * LEVEL + 20, anchor="top_right")
        diag.caption("**Figure 2:** A valid red-black tree; node positions follow the in-order rank of the keys",
                     small_caps=True)
    return diag


def build_diagram(output_dir: Path | str = "examples/computer_science") -> Path:
    return render_all(diagram(), output_dir, "02_red_black_tree")["svg"]


if __name__ == "__main__":
    dest = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("examples/computer_science")
    build_diagram(dest)
