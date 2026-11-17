"""Merge sort on eight keys, drawn as its divide-and-merge recursion.

The upper half splits the array in two until every piece holds one key; the
lower half merges sorted pieces back up, two at a time. Every merge level
touches all $n$ keys once, and there are $\\log_2 n$ of them, which is where
$T(n) = 2T(n/2) + \\Theta(n) = \\Theta(n \\log n)$ comes from. The rows are
computed by actually running the algorithm on the input.
"""
from __future__ import annotations

import sys
from pathlib import Path

from diagrams_as_code import Diagram, Style
from diagrams_as_code.output import render_all

DATA = [38, 27, 43, 3, 9, 82, 10, 5]
CELL_W, CELL_H = 30.0, 28.0
X0, SLOT, TOP, PITCH = 150.0, 60.0, 80.0, 70.0
SPLIT = Style(fill="#FFFFFF", font_size=13)
LEAF = Style(fill="#E9E9EC", font_size=13)
MERGED = Style(fill="#DCE6F2", font_size=13)
FRAME = Style(fill="none", stroke_width=1.6)
DIVIDE = {"routing": "direct", "width": 0.9, "color": "#777777", "head": "open", "arrow_size": 0.8}
MERGE = {"routing": "direct", "width": 1.3, "arrow_size": 0.8}


def split_rows(n: int) -> list[list[tuple[int, int]]]:
    """Index ranges [lo, hi) at each depth of the recursion, top-down."""
    rows, current = [], [(0, n)]
    while True:
        rows.append(current)
        if all(hi - lo == 1 for lo, hi in current):
            return rows
        current = [part for lo, hi in current for part in
                   ([(lo, (lo + hi) // 2), ((lo + hi) // 2, hi)] if hi - lo > 1 else [(lo, hi)])]


def diagram() -> Diagram:
    n = len(DATA)
    down = split_rows(n)
    depth = len(down) - 1  # log2 n
    with Diagram("Merge sort recursion on eight keys", theme="paper") as diag:

        def centre(lo: int, hi: int) -> float:
            return X0 + SLOT * ((lo + hi - 1) / 2)

        def array(values: list[int], lo: int, hi: int, y: float, style: Style):
            width = CELL_W * len(values)
            frame = diag.shape("", width, CELL_H, style=FRAME, fit_label=False).at(centre(lo, hi), y, anchor="top_center")
            for k, value in enumerate(values):
                diag.shape(str(value), CELL_W, CELL_H, style=style, fit_label=False).inside(frame, "top_left", k * CELL_W, 0)
            return frame

        boxes: dict[tuple[int, int, int], object] = {}
        for row, ranges in enumerate(down):
            style = LEAF if row == depth else SPLIT
            for lo, hi in ranges:
                boxes[(row, lo, hi)] = array(DATA[lo:hi], lo, hi, TOP + row * PITCH, style)
                if row:
                    parent = next((r for r in down[row - 1] if r[0] <= lo and hi <= r[1]))
                    diag.connect(boxes[(row - 1, *parent)].anchor("bottom", 0.5),
                                 boxes[(row, lo, hi)].anchor("top", 0.5), **DIVIDE)

        # Merge back up: the same ranges in reverse, now sorted.
        for step, ranges in enumerate(reversed(down[:-1]), start=1):
            row = depth + step
            for lo, hi in ranges:
                box = array(sorted(DATA[lo:hi]), lo, hi, TOP + row * PITCH, MERGED)
                mid = (lo + hi) // 2
                for part in ((lo, mid), (mid, hi)):
                    diag.connect(boxes[(row - 1, *part)].anchor("bottom", 0.5), box.anchor("top", 0.5), **MERGE)
                boxes[(row, lo, hi)] = box

        # Braces for the two phases, and the cost of each merge level.
        diag.bracket("**divide**\n$\\mathrm{log}_2 n$ levels\nof splitting", side="left").spanning(
            boxes[(0, 0, n)], boxes[(depth - 1, 0, 2)], gap=22)
        diag.bracket("**merge**\n$\\mathrm{log}_2 n$ levels\nof merging", side="left").spanning(
            boxes[(depth + 1, 0, 2)], boxes[(2 * depth, 0, n)], gap=22)
        right = X0 + SLOT * (n - 1) + 40
        diag.text("**work per level**", size=12).at(right, TOP + (depth + 1) * PITCH - 26, anchor="bottom_left")
        for step in range(1, depth + 1):
            row = depth + step
            pieces = n >> step
            diag.text(f"${pieces} \\times {n // pieces} = n$ keys moved", size=12).at(
                right, TOP + row * PITCH + CELL_H / 2, anchor="left_center")
        diag.text(
            "$T(n) = 2\\,T(n/2) + cn$\n"
            "$= cn \\cdot \\mathrm{log}_2 n + n\\,T(1)$\n"
            "$= \\Theta(n \\log n)$",
            size=14,
        ).at(right, TOP + PITCH * 0.3)
        diag.text("input", size=11, italic=True, color="#555555").at(
            centre(0, n) + CELL_W * n / 2 + 10, TOP + CELL_H / 2, anchor="left_center")
        diag.text("base case: $n = 1$", size=11, italic=True, color="#555555").at(
            centre(0, n) + SLOT * n / 2 + 10, TOP + depth * PITCH + CELL_H / 2, anchor="left_center")
        diag.caption("**Figure 3:** Merge sort splits $n = 8$ keys over $\\mathrm{log}_2 n = 3$ levels and merges them back "
                     "in $\\Theta(n)$ per level", small_caps=True)
    return diag


def build_diagram(output_dir: Path | str = "output/computer_science") -> Path:
    return render_all(diagram(), output_dir, "03_merge_sort_recursion")["svg"]


if __name__ == "__main__":
    dest = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("output/computer_science")
    build_diagram(dest)
