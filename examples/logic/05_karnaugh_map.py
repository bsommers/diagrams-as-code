"""A four-variable Karnaugh map with its grouped prime implicants.

The function is given as a list of minterms. The script finds every prime
implicant by Quine-McCluskey merging, chooses a cover (essential implicants
first, then the largest remaining), and draws each chosen group on the map.
Rows and columns are in Gray order, so neighbouring cells differ in one
variable and a group may wrap around an edge; a wrapped group is drawn as two
pieces with an open side. The minimal sum of products is assembled from the
same groups.
"""
from __future__ import annotations

import itertools
import sys
from pathlib import Path

from diagrams_as_code import Diagram, Style
from diagrams_as_code.output import render_all

MINTERMS = [0, 2, 3, 5, 7, 8, 10, 11, 13, 15]  # f(A, B, C, D) = sum of m(...)
VARS = "ABCD"
GRAY = [0b00, 0b01, 0b11, 0b10]  # row labels AB, column labels CD
CELL = 72.0
X0, Y0 = 150.0, 110.0
COLOURS = ["#C0392B", "#1F6FB5", "#2E8B57", "#B8860B", "#7B3FA0", "#555555"]


def implicant_cells(term: str) -> set[int]:
    """Minterms covered by a pattern such as ``'-0-1'``."""
    return {m for m in range(16) if all(t == "-" or int(t) == (m >> (3 - i)) & 1 for i, t in enumerate(term))}


def prime_implicants(minterms: list[int]) -> list[str]:
    terms = {format(m, "04b") for m in minterms}
    primes: set[str] = set()
    while terms:
        merged, used = set(), set()
        for a, b in itertools.combinations(sorted(terms), 2):
            diff = [i for i in range(4) if a[i] != b[i]]
            if len(diff) == 1 and "-" not in (a[diff[0]], b[diff[0]]):
                merged.add(a[: diff[0]] + "-" + a[diff[0] + 1:])
                used |= {a, b}
        primes |= terms - used
        terms = merged
    return sorted(primes)


def choose_cover(minterms: list[int], primes: list[str]) -> list[str]:
    need = set(minterms)
    chosen: list[str] = []
    for m in sorted(need):  # essential implicants
        owners = [p for p in primes if m in implicant_cells(p)]
        if len(owners) == 1 and owners[0] not in chosen:
            chosen.append(owners[0])
    covered = set().union(*(implicant_cells(p) for p in chosen)) if chosen else set()
    while need - covered:
        best = max((p for p in primes if p not in chosen), key=lambda p: len((implicant_cells(p) & need) - covered))
        chosen.append(best)
        covered |= implicant_cells(best)
    return chosen


def product_term(pattern: str) -> str:
    out = ""
    for name, bit in zip(VARS, pattern):
        if bit == "1":
            out += name
        elif bit == "0":
            out += name + "'"
    return out or "1"


def cell_of(minterm: int) -> tuple[int, int]:
    """(row, column) of a minterm on the map; the row is AB, the column CD."""
    return GRAY.index(minterm >> 2), GRAY.index(minterm & 3)


def pieces(cells: set[int]) -> list[tuple[int, int, int, int, bool, bool, bool, bool]]:
    """Rectangles (r0, r1, c0, c1, open_left, open_right, open_top, open_bottom) covering a group."""
    rows = sorted({cell_of(m)[0] for m in cells})
    cols = sorted({cell_of(m)[1] for m in cells})

    def spans(idx: list[int]) -> list[tuple[int, int, bool, bool]]:
        if len(idx) == 4:
            return [(0, 3, False, False)]
        if idx == [0, 3]:  # wraps: pieces at both edges, open towards the edge they continue through
            return [(0, 0, True, False), (3, 3, False, True)]
        if 0 in idx and 3 in idx:  # three-wide wrap cannot occur for a power-of-two group
            raise ValueError(idx)
        return [(idx[0], idx[-1], False, False)]

    out = []
    for r0, r1, ot, ob in spans(rows):
        for c0, c1, ol, orr in spans(cols):
            out.append((r0, r1, c0, c1, ol, orr, ot, ob))
    return out


def diagram() -> Diagram:
    ones = set(MINTERMS)
    primes = prime_implicants(MINTERMS)
    cover = choose_cover(MINTERMS, primes)
    covered = set().union(*(implicant_cells(p) for p in cover))
    assert covered == ones, "the chosen groups must cover exactly the ones"
    with Diagram("Karnaugh map", theme="paper") as diag:
        # Cells.
        for m in range(16):
            r, c = cell_of(m)
            x, y = X0 + c * CELL, Y0 + r * CELL
            diag.polygon(
                [(x, y), (x + CELL, y), (x + CELL, y + CELL), (x, y + CELL)],
                "1" if m in ones else "0",
                style=Style(fill="#FFFFFF", stroke="#111111", stroke_width=1.2, font_size=18,
                            text_color="#000000" if m in ones else "#999999"),
                obstacle=False,
            )
            diag.text(f"m{m}", size=9, color="#777777").at(x + CELL / 2, y + CELL - 17, anchor="bottom_center")
        # Axis labels.
        for k, g in enumerate(GRAY):
            diag.text(f"{g >> 1}{g & 1}", size=13).at(X0 + k * CELL + CELL / 2, Y0 - 8, anchor="bottom_center")
            diag.text(f"{g >> 1}{g & 1}", size=13).at(X0 - 10, Y0 + k * CELL + CELL / 2, anchor="right_center")
        diag.text("$CD$", size=14).at(X0 + 2 * CELL, Y0 - 34, anchor="bottom_center")
        diag.text("$AB$", size=14).at(X0 - 48, Y0 + 2 * CELL, anchor="right_center")

        # Groups, each inset a little more than the one before so that overlapping groups stay visible.
        for gi, pat in enumerate(cover):
            colour = COLOURS[gi % len(COLOURS)]
            inset = 5.0 + 3.0 * gi
            for r0, r1, c0, c1, ol, orr, ot, ob in pieces(implicant_cells(pat)):
                l, rgt = X0 + c0 * CELL + inset, X0 + (c1 + 1) * CELL - inset
                t, b = Y0 + r0 * CELL + inset, Y0 + (r1 + 1) * CELL - inset
                if ol:
                    l = X0 + c0 * CELL
                if orr:
                    rgt = X0 + (c1 + 1) * CELL
                if ot:
                    t = Y0 + r0 * CELL
                if ob:
                    b = Y0 + (r1 + 1) * CELL
                # Open sides: leave out the edge where the group continues over the border of the map.
                sides = {
                    "top": ((l, t), (rgt, t), ot), "right": ((rgt, t), (rgt, b), orr),
                    "bottom": ((rgt, b), (l, b), ob), "left": ((l, b), (l, t), ol),
                }
                path = ""
                for a, bpt, is_open in sides.values():
                    if not is_open:
                        path += f"M {a[0]:.1f} {a[1]:.1f} L {bpt[0]:.1f} {bpt[1]:.1f} "
                diag.path(path, style=Style(fill="none", stroke=colour, stroke_width=2.4), obstacle=False)

        # Legend and result.
        lx = X0 + 4 * CELL + 50
        diag.text("**Groups**", size=14).at(lx, Y0 - 6, anchor="bottom_left")
        for gi, pat in enumerate(cover):
            y = Y0 + 16 + gi * 38
            colour = COLOURS[gi % len(COLOURS)]
            diag.polyline([(lx, y), (lx + 34, y)], style=Style(stroke=colour, stroke_width=3.0), obstacle=False)
            size = len(implicant_cells(pat))
            diag.text(f"${product_term(pat)}$", size=15).at(lx + 46, y, anchor="left_center")
            mins = ",".join(str(m) for m in sorted(implicant_cells(pat)))
            diag.text(f"{size} cells: m({mins})", size=11, color="#555555").at(lx + 120, y, anchor="left_center")
        expr = " + ".join(product_term(p) for p in cover)
        bottom = Y0 + 4 * CELL + 30
        diag.text(
            "$f(A,B,C,D) = \\sum m(" + ", ".join(map(str, MINTERMS)) + ")$",
            size=14,
        ).at(X0 - 80, bottom, anchor="top_left")
        diag.text(f"$f = {expr}$", size=16).at(X0 - 80, bottom + 30, anchor="top_left")
        diag.text(
            f"{len(primes)} prime implicants found; {len(cover)} cover all {len(ones)} ones. "
            "Groups may wrap around the edges of the map.",
            size=12, font="serif", italic=True,
        ).at(X0 - 80, bottom + 62, anchor="top_left")
        diag.caption(
            "**Figure 5:** Karnaugh map of a four-variable function with its grouped implicants and minimal sum of products",
            small_caps=True,
        )
    return diag


def build_diagram(output_dir: Path | str = "examples/logic") -> Path:
    return render_all(diagram(), output_dir, "05_karnaugh_map")["svg"]


if __name__ == "__main__":
    dest = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("examples/logic")
    build_diagram(dest)
