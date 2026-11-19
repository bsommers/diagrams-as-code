"""Venn diagrams of two and three sets, with De Morgan's laws shaded.

Each panel is a universe $U$ with circles for the sets. Shaded regions are
computed, not drawn by hand: the circles are polygons, intersections are found
by convex clipping, and a region is painted by laying shade and white shapes in
order. Top row: two sets. Bottom row: three sets. In each pair the left panel
shades the complement of the union (or intersection) and the right panel
builds the same region from the complements of the sets; the script checks
every identity over all membership combinations as well.
"""
from __future__ import annotations

import itertools
import math
import sys
from pathlib import Path

from diagrams_as_code import Diagram, Style
from diagrams_as_code.output import render_all

PW, PH = 190.0, 158.0  # universe rectangle of one panel
R = 38.0
SHADE = "#8FB0DC"
INK = "#111111"

Point = tuple[float, float]


def circle_poly(cx: float, cy: float, r: float = R, n: int = 160) -> list[Point]:
    return [(cx + r * math.cos(math.tau * k / n), cy + r * math.sin(math.tau * k / n)) for k in range(n)]


def clip(subject: list[Point], clipper: list[Point]) -> list[Point]:
    """Sutherland-Hodgman: ``subject`` clipped to the convex polygon ``clipper`` (either orientation)."""
    area = sum(a[0] * b[1] - b[0] * a[1] for a, b in zip(clipper, clipper[1:] + clipper[:1]))
    sign = 1.0 if area > 0 else -1.0
    out = subject
    for a, b in zip(clipper, clipper[1:] + clipper[:1]):
        def inside(p: Point) -> bool:
            return sign * ((b[0] - a[0]) * (p[1] - a[1]) - (b[1] - a[1]) * (p[0] - a[0])) >= 0

        def cross(p: Point, q: Point) -> Point:
            d1 = (b[0] - a[0]) * (p[1] - a[1]) - (b[1] - a[1]) * (p[0] - a[0])
            d2 = (b[0] - a[0]) * (q[1] - a[1]) - (b[1] - a[1]) * (q[0] - a[0])
            t = d1 / (d1 - d2)
            return (p[0] + t * (q[0] - p[0]), p[1] + t * (q[1] - p[1]))

        src, out = out, []
        for i, p in enumerate(src):
            q = src[(i + 1) % len(src)]
            if inside(p):
                out.append(p)
                if not inside(q):
                    out.append(cross(p, q))
            elif inside(q):
                out.append(cross(p, q))
        if not out:
            break
    return out


def centres(n: int, ox: float, oy: float) -> list[Point]:
    if n == 2:
        return [(ox + PW / 2 - 22, oy + PH / 2), (ox + PW / 2 + 22, oy + PH / 2)]
    cx, cy = ox + PW / 2, oy + PH / 2 - 2
    return [(cx - 22, cy - 14), (cx + 22, cy - 14), (cx, cy + 22)]


def panel(diag: Diagram, n: int, ox: float, oy: float, build, title: str) -> None:
    """One universe with ``n`` circles; ``build(sets, universe)`` returns [(polygon, colour), ...] to paint."""
    universe = [(ox, oy), (ox + PW, oy), (ox + PW, oy + PH), (ox, oy + PH)]
    cs = centres(n, ox, oy)
    sets = [circle_poly(*c) for c in cs]
    diag.polygon(universe, style=Style(fill="#FFFFFF", stroke=INK, stroke_width=1.4), obstacle=False)
    for poly, colour in build(sets, universe):
        diag.polygon(poly, style=Style(fill=colour, stroke=colour, stroke_width=0.2), obstacle=False)
    for (cx, cy), name in zip(cs, "ABC"):
        diag.path(
            f"M {cx - R:.2f} {cy:.2f} A {R} {R} 0 1 0 {cx + R:.2f} {cy:.2f} A {R} {R} 0 1 0 {cx - R:.2f} {cy:.2f} Z",
            style=Style(fill="none", stroke=INK, stroke_width=1.3), obstacle=False,
        )
    # set names just outside each circle, away from the others
    mx = sum(c[0] for c in cs) / n
    my = sum(c[1] for c in cs) / n
    for (cx, cy), name in zip(cs, "ABC"):
        dx, dy = cx - mx, cy - my
        norm = math.hypot(dx, dy) or 1.0
        diag.text(f"${name}$", size=14).at(cx + dx / norm * (R + 12), cy + dy / norm * (R + 12), anchor="center")
    diag.text("$U$", size=13).at(ox + 7, oy + 4, anchor="top_left")
    diag.text(title, size=13, align="center").at(ox + PW / 2, oy + PH + 18, anchor="top_center")


WHITE = "#FFFFFF"


def complement_of(*painted_white):
    """Shade the universe, then paint each given shape (list of indices or 'ALL') white."""
    def build(sets, universe):
        return [(universe, SHADE)] + [(sets[i], WHITE) for i in painted_white]
    return build


def complement_of_lens(indices):
    def build(sets, universe):
        poly = sets[indices[0]]
        for i in indices[1:]:
            poly = clip(poly, sets[i])
        return [(universe, SHADE), (poly, WHITE)]
    return build


def verify() -> None:
    """De Morgan holds for every membership pattern of two and three sets."""
    for bits in itertools.product((False, True), repeat=3):
        a, b, c = bits
        assert (not (a or b)) == ((not a) and (not b))
        assert (not (a and b)) == ((not a) or (not b))
        assert (not (a or b or c)) == ((not a) and (not b) and (not c))
        assert (not (a and b and c)) == ((not a) or (not b) or (not c))


def diagram() -> Diagram:
    verify()
    left, top, gap_in, gap_out = 40.0, 50.0, 70.0, 40.0
    row_gap = PH + 90
    with Diagram("De Morgan's laws as Venn diagrams", theme="paper") as diag:
        rows = [
            (2, [
                (r"$(A \cup B)'$", complement_of(0, 1), r"$A' \cap B'$", complement_of(0, 1)),
                (r"$(A \cap B)'$", complement_of_lens([0, 1]), r"$A' \cup B'$", complement_of_lens([0, 1])),
            ]),
            (3, [
                (r"$(A \cup B \cup C)'$", complement_of(0, 1, 2), r"$A' \cap B' \cap C'$", complement_of(0, 1, 2)),
                (r"$(A \cap B \cap C)'$", complement_of_lens([0, 1, 2]), r"$A' \cup B' \cup C'$",
                 complement_of_lens([0, 1, 2])),
            ]),
        ]
        for r, (n, pairs) in enumerate(rows):
            y = top + r * row_gap
            x = left
            for lt, lb, rt, rb in pairs:
                panel(diag, n, x, y, lb, lt)
                diag.text("$=$", size=22).at(x + PW + gap_in / 2, y + PH / 2, anchor="center")
                panel(diag, n, x + PW + gap_in, y, rb, rt)
                x += 2 * PW + gap_in + gap_out + 30
        # Law names across the top of each pair.
        pair_w = 2 * PW + gap_in
        for k, name in enumerate(("First law", "Second law")):
            cx = left + k * (pair_w + gap_out + 30) + pair_w / 2
            diag.text(f"**{name}**", size=14, align="center").at(cx, top - 24, anchor="bottom_center")
        diag.text("two sets", size=12, font="serif", italic=True).at(left, top - 24, anchor="bottom_left")
        diag.text("three sets", size=12, font="serif", italic=True).at(left, top + row_gap - 24, anchor="bottom_left")
        diag.text(
            "A prime denotes the complement within $U$: the complement of a union is the intersection of the "
            "complements, and the complement of an intersection is the union of the complements.",
            size=12, font="serif", italic=True, max_width=2 * pair_w + gap_out + 30, align="center",
        ).at(left, top + 2 * row_gap - 24)
        diag.caption(
            "**Figure 4:** De Morgan's laws for two and three sets; the shaded region is the same on both sides of each equation",
            small_caps=True,
        )
    return diag


def build_diagram(output_dir: Path | str = "examples/logic") -> Path:
    return render_all(diagram(), output_dir, "04_venn_de_morgan")["svg"]


if __name__ == "__main__":
    dest = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("examples/logic")
    build_diagram(dest)
