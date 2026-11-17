"""A hash table with separate chaining, and one lookup traced through it.

Eight keys are inserted into $m = 7$ buckets with $h(k) = k \bmod 7$. Each
bucket holds the head pointer of a singly linked list; a new key is pushed on
the front of its chain, so the newest key comes first. A slash in a pointer
cell is NULL. The highlighted path follows ``search(17)``: hash, index, then
walk the chain of bucket 3 until the key matches.
"""
from __future__ import annotations

import sys
from pathlib import Path

from diagrams_as_code import Diagram, Style
from diagrams_as_code.output import render_all

M = 7
KEYS = (14, 22, 8, 3, 17, 31, 12, 26)  # in insertion order
X_TABLE, TOP, ROW = 300.0, 70.0, 46.0
SLOT_W, SLOT_H = 64.0, 34.0
KEY_W, PTR_W, GAP = 50.0, 24.0, 44.0
SLOT = Style(radius=0, shadow=False, fill="#EEE8D5", font_size=12)
CELL = Style(radius=0, shadow=False, fill="#FDF6E3", font_size=14)
PTR = Style(radius=0, shadow=False, fill="#FDF6E3")
HOT = Style(radius=0, shadow=False, fill="#F5D67B", stroke="#B58900", stroke_width=1.8, font_size=14)
NULL = Style(fill="none", stroke="#657B83", stroke_width=1.0)
LINK = {"routing": "direct", "width": 1.2, "arrow_size": 0.8}
TRACE = {"width": 2.0, "color": "#CB4B16"}


def chains() -> dict[int, list[int]]:
    """Bucket -> keys, newest first (insertion at the head)."""
    table: dict[int, list[int]] = {i: [] for i in range(M)}
    for key in KEYS:
        table[key % M].insert(0, key)
    return table


def diagram() -> Diagram:
    table = chains()
    with Diagram("Hash table with separate chaining", theme="solarized_light") as diag:

        def null_slash(x: float, y: float, w: float, h: float) -> None:
            diag.polyline([(x + 4, y + h - 4), (x + w - 4, y + 4)], style=NULL)

        diag.text("**bucket array** $T[0..6]$", size=13).at(X_TABLE + SLOT_W / 2, TOP - 12, anchor="bottom_center")
        diag.text("**chains** (singly linked lists)", size=13).at(
            X_TABLE + SLOT_W + GAP, TOP - 12, anchor="bottom_left")

        slots, nodes = [], {}
        for i in range(M):
            y = TOP + i * ROW
            slot = diag.shape("", SLOT_W, SLOT_H, style=SLOT).at(X_TABLE, y)
            diag.text(f"*{i}*", size=12, color="#657B83").inside(slot, "left_center", 7, 0)
            slots.append(slot)
            if not table[i]:
                null_slash(X_TABLE + SLOT_W / 2, y, SLOT_W / 2, SLOT_H)
                continue
            x = X_TABLE + SLOT_W + GAP
            diag.point(X_TABLE + SLOT_W * 0.72, y + SLOT_H / 2, dot=True, radius=3.0)
            prev_tail = (X_TABLE + SLOT_W * 0.72, y + SLOT_H / 2)
            for j, key in enumerate(table[i]):
                hot = i == 17 % M and table[i].index(17) >= j
                cell = diag.shape(str(key), KEY_W, SLOT_H, style=HOT if hot else CELL).at(x, y)
                ptr = diag.shape("", PTR_W, SLOT_H, style=PTR).at(x + KEY_W, y)
                nodes[key] = cell
                diag.connect(prev_tail, cell.anchor("left", 0.5), **{**LINK, **(TRACE if hot else {})})
                tail = (x + KEY_W + PTR_W / 2, y + SLOT_H / 2)
                if j == len(table[i]) - 1:
                    null_slash(x + KEY_W, y, PTR_W, SLOT_H)
                else:
                    diag.point(*tail, dot=True, radius=3.0)
                prev_tail = tail
                x += KEY_W + PTR_W + GAP

        # The lookup: key -> hash function -> bucket index.
        query = diag.shape("**search(17)**", 120, 38, style=Style(fill="#FDF6E3", font_size=13)).at(40, TOP + 3 * ROW - 70)
        hashf = diag.shape("$h(k) = k \\operatorname{mod} 7$\n$h(17) = 3$", 130, 52, style=Style(fill="#EEE8D5", font_size=13)).at(
            35, TOP + 3 * ROW - 9)
        query >> diag.edge(**TRACE) >> hashf
        hashf.anchor("right", 0.5) >> diag.edge(**TRACE) >> slots[3].anchor("left", 0.5)
        diag.text("compare 31, then 17: found\nafter 2 probes", size=12, italic=True, color="#CB4B16").at(
            X_TABLE + SLOT_W + GAP, TOP + 3 * ROW + SLOT_H + 3)

        diag.text(
            "Load factor $\\alpha = n / m = 8 / 7 \\approx 1.14$.\n"
            "Expected search cost $\\Theta(1 + \\alpha)$\nunder simple uniform hashing;\n"
            "insert at the head is $O(1)$,\nworst-case search $\\Theta(n)$.",
            size=12, font="serif",
        ).at(40, TOP + 4 * ROW + 30)
        diag.text("*inserted in order:* " + ", ".join(map(str, KEYS)), size=12, color="#657B83").at(40, TOP + 12)
        diag.caption("**Figure 1:** Separate chaining with head insertion; the lookup of key 17 is traced in orange",
                     small_caps=True)
    return diag


def build_diagram(output_dir: Path | str = "output/computer_science") -> Path:
    return render_all(diagram(), output_dir, "01_hash_table_chaining")["svg"]


if __name__ == "__main__":
    dest = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("output/computer_science")
    build_diagram(dest)
