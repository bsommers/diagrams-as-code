"""A B+-tree index of order 4 and the layout of one of its leaf pages (DATABASE domain).

The top half is the tree: a root page holding two separator keys and three
child pointers, and three leaf pages holding the keys in order, chained by
sibling pointers for range scans. The bottom half enlarges the middle leaf
as an 8 KiB slotted page: a fixed header, an array of line pointers growing
forward, index tuples growing back from the end, and a special area with the
sibling links.
"""
from __future__ import annotations

import sys
from pathlib import Path

from diagrams_as_code import Diagram, Style
from diagrams_as_code.output import render_all

KEY_W, PTR_W, CELL_H = 40.0, 16.0, 30.0
KEY = Style(fill="#FFFFFF", font_size=13)
PTR = Style(fill="#D9D9DE", font_size=11)
HEADER = Style(fill="#E4E4E8", font_size=11)
TUPLE = Style(fill="#C9CDD6", font_size=11)
SPECIAL = Style(fill="#B9BECB", font_size=11)
FRAME = Style(fill="#FFFFFF")
SMALL = 11.0
LEAVES = ([5, 12, 21], [30, 41, 52], [60, 74, 88])
LEAF_X = (60.0, 280.0, 500.0)
ROOT_Y, LEAF_Y = 90.0, 210.0
PAGE_X, PAGE_Y, PAGE_W = 60.0, 330.0, 562.0
GAP = 104.0  # free space between the line pointers and the tuples


def diagram() -> Diagram:
    with Diagram("B+-Tree Index Page Structure", theme="paper") as diag:
        def cell(label: str, width: float, x: float, y: float, style: Style):
            return diag.shape(label, width, CELL_H, style=style, fit_label=False).at(x, y)

        # Root: P0 30 P1 60 P2, centred over the leaves.
        leaf_w = 3 * KEY_W + PTR_W
        root_w = 2 * KEY_W + 3 * PTR_W
        x = (LEAF_X[0] + LEAF_X[2] + leaf_w) / 2 - root_w / 2
        root_ptrs = []
        for i, key in enumerate((30, 60, None)):
            cell("", PTR_W, x, ROOT_Y, PTR)
            root_ptrs.append(x)
            x += PTR_W
            if key is not None:
                cell(str(key), KEY_W, x, ROOT_Y, KEY)
                x += KEY_W

        # Leaves: three keys then the right-sibling pointer.
        next_ptrs = []
        for keys, lx in zip(LEAVES, LEAF_X):
            cell(str(keys[0]), KEY_W, lx, LEAF_Y, KEY)
            for j, key in enumerate(keys[1:], start=1):
                cell(str(key), KEY_W, lx + j * KEY_W, LEAF_Y, KEY)
            cell("", PTR_W, lx + 3 * KEY_W, LEAF_Y, PTR)
            next_ptrs.append(lx + 3 * KEY_W)

        line = {"routing": "direct", "width": 1.0, "head": "triangle", "arrow_size": 0.8}
        for ptr, lx in zip(root_ptrs, LEAF_X):
            diag.point(ptr + PTR_W / 2, ROOT_Y + CELL_H / 2, dot=True)
            diag.connect((ptr + PTR_W / 2, ROOT_Y + CELL_H / 2), (lx + leaf_w / 2, LEAF_Y), **line)
        for ptr, lx in zip(next_ptrs[:2], LEAF_X[1:]):
            diag.point(ptr + PTR_W / 2, LEAF_Y + CELL_H / 2, dot=True)
            diag.connect((ptr + PTR_W / 2, LEAF_Y + CELL_H / 2), (lx, LEAF_Y + CELL_H / 2), **line)
        diag.text("$\\emptyset$", size=12).at(LEAF_X[2] + leaf_w + 8, LEAF_Y + CELL_H / 2, anchor="left_center")

        diag.text("**root**  level 1", size=SMALL).at(LEAF_X[0], ROOT_Y + CELL_H / 2, anchor="left_center")
        diag.text("**leaves**  level 0", size=SMALL).at(LEAF_X[0], LEAF_Y - 10, anchor="bottom_left")
        diag.text("$k < 30$", size=SMALL).at(LEAF_X[0] + leaf_w / 2 + 34, 160, anchor="right_center")
        diag.text("$30 \\leq k < 60$", size=SMALL).at(LEAF_X[1] + leaf_w / 2 + 8, 160, anchor="left_center")
        diag.text("$k \\geq 60$", size=SMALL).at(LEAF_X[2] + leaf_w / 2 - 34, 160, anchor="left_center")
        diag.text(
            "Height $h = \\lceil \\log\\nolimits_{f} N \\rceil$ for fan-out $f$:\n"
            "with $f = 400$, three levels index $6.4 \\times 10^{7}$ keys.",
            size=12, font="serif", italic=True,
        ).at(LEAF_X[2] + leaf_w + 40, ROOT_Y - 4)

        # The middle leaf enlarged as a slotted page.
        frame = diag.shape("", PAGE_W, 4 * CELL_H + GAP, style=FRAME, fit_label=False).at(PAGE_X, PAGE_Y)
        row = 0.0
        x = 0.0
        for label, width in (("pd_lsn", 120), ("pd_lower", 100), ("pd_upper", 100),
                             ("pd_special", 112), ("flags", 130)):
            diag.shape(label, width, CELL_H, style=HEADER, fit_label=False).inside(frame, "top_left", x, row)
            x += width
        row += CELL_H
        lps = []
        for i in range(3):
            lps.append(diag.shape(f"lp{i + 1}", 48, CELL_H, style=PTR, fit_label=False).inside(
                frame, "top_left", i * 48, row))
        diag.text("free space", size=SMALL, italic=True, color="#666666").inside(
            frame, "top_left", 400, row + 8)
        row += CELL_H + GAP
        tuple_row = row
        tuples = []
        x = PAGE_W - 3 * 110
        for key in (52, 41, 30):
            tuples.append(diag.shape(f"({key}, TID)", 110, CELL_H, style=TUPLE, fit_label=False).inside(
                frame, "top_left", x, row))
            x += 110
        row += CELL_H
        diag.shape("special: btpo_prev | btpo_next | level 0", PAGE_W, CELL_H, style=SPECIAL,
                             fit_label=False).inside(frame, "top_left", 0, row)

        curve = {"routing": "direct", "width": 0.9, "head": "triangle", "arrow_size": 0.7}
        for lp, tup in zip(lps, reversed(tuples)):
            lp.anchor("bottom", 0.5) >> diag.edge(**curve) >> tup.anchor("top", 0.5)

        grow = {"routing": "direct", "width": 1.5}
        diag.connect((PAGE_X + 154, PAGE_Y + 1.5 * CELL_H), (PAGE_X + 204, PAGE_Y + 1.5 * CELL_H), **grow)
        diag.connect((PAGE_X + PAGE_W - 340, PAGE_Y + tuple_row + CELL_H / 2),
                     (PAGE_X + PAGE_W - 390, PAGE_Y + tuple_row + CELL_H / 2), **grow)

        zoom = {"routing": "direct", "width": 0.75, "style": "dashed", "arrow_head": False}
        diag.connect((LEAF_X[1], LEAF_Y + CELL_H), (PAGE_X, PAGE_Y), **zoom)
        diag.connect((LEAF_X[1] + leaf_w, LEAF_Y + CELL_H), (PAGE_X + PAGE_W, PAGE_Y), **zoom)

        diag.bracket("8 KiB page", side="right").spanning(frame, gap=12)
        diag.text(
            "Line pointers grow forward from *pd_lower*;\n"
            "tuples grow back from *pd_upper*. A page\n"
            "splits when the two would meet.",
            size=12, font="serif", italic=True,
        ).at(PAGE_X + PAGE_W + 110, PAGE_Y + 80)
        diag.caption(
            "**Figure 7:** A B+-tree of order 4 and the slotted layout of its middle leaf page",
            small_caps=True,
        )
    return diag


def build_diagram(output_dir: Path | str = "output/database") -> Path:
    return render_all(diagram(), output_dir, "07_btree_index_pages")["svg"]


if __name__ == "__main__":
    dest = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("output/database")
    build_diagram(dest)
