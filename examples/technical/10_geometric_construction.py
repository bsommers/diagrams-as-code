"""The circumcircle of a triangle, constructed from its perpendicular bisectors.

Every coordinate is computed from the three vertices: the midpoints of the
sides, the circumcentre $O$ where the perpendicular bisectors meet, and the
radius $R$. Equal tick marks show each side cut in half, small squares mark the
right angles, and the three radii show that $O$ is equally far from the vertices.
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

from diagrams_as_code import Diagram, Style
from diagrams_as_code.output import render_all

A, B, C = (210.0, 80.0), (110.0, 330.0), (430.0, 330.0)
TRIANGLE = Style(fill="#DCE6F2", fill_opacity=0.5, stroke="#111111", stroke_width=1.6)
FINE = Style(fill="none", stroke="#222222", stroke_width=0.9)
CONSTRUCTION = {"routing": "direct", "arrow_head": False, "width": 0.9, "style": "dashed", "color": "#555555"}
RADIUS = {"routing": "direct", "arrow_head": False, "width": 0.9, "color": "#1F2F57"}


def circumcentre(a, b, c):
    """The point equally far from ``a``, ``b`` and ``c``."""
    d = 2 * (a[0] * (b[1] - c[1]) + b[0] * (c[1] - a[1]) + c[0] * (a[1] - b[1]))
    sq = [p[0] ** 2 + p[1] ** 2 for p in (a, b, c)]
    x = (sq[0] * (b[1] - c[1]) + sq[1] * (c[1] - a[1]) + sq[2] * (a[1] - b[1])) / d
    y = (sq[0] * (c[0] - b[0]) + sq[1] * (a[0] - c[0]) + sq[2] * (b[0] - a[0])) / d
    return (x, y)


def unit(p, q):
    """The unit vector from ``p`` towards ``q``."""
    length = math.dist(p, q)
    return ((q[0] - p[0]) / length, (q[1] - p[1]) / length)


def along(p, direction, distance):
    return (p[0] + direction[0] * distance, p[1] + direction[1] * distance)


def strokes(pairs) -> str:
    """SVG path data for separate straight strokes."""
    return " ".join(f"M {p[0]:.2f} {p[1]:.2f} L {q[0]:.2f} {q[1]:.2f}" for p, q in pairs)


def widest_gap(origin, points):
    """The unit vector from ``origin`` down the middle of the widest gap between ``points``."""
    angles = sorted(math.atan2(p[1] - origin[1], p[0] - origin[0]) for p in points)
    gaps = [(b - a, a) for a, b in zip(angles, angles[1:] + [angles[0] + math.tau])]
    width, start = max(gaps)
    return (math.cos(start + width / 2), math.sin(start + width / 2))


def diagram() -> Diagram:
    o = circumcentre(A, B, C)
    r = math.dist(o, A)
    with Diagram("Circumcircle of a triangle", theme="paper") as diag:
        diag.path(
            f"M {o[0] - r:.2f} {o[1]:.2f} A {r:.2f} {r:.2f} 0 1 0 {o[0] + r:.2f} {o[1]:.2f} "
            f"A {r:.2f} {r:.2f} 0 1 0 {o[0] - r:.2f} {o[1]:.2f} Z",
            style=Style(fill="none", stroke="#1F2F57", stroke_width=1.2),
        )
        diag.polygon([A, B, C], style=TRIANGLE, z=-1)
        centre = diag.point(*o, dot=True)

        def name(text: str, where, size: float = 15) -> None:
            diag.text(text, size=size).at(*where, anchor="center")

        midpoints, marks = [], []
        # Each side, the name of its midpoint and the number of ticks that marks its halves.
        for (p, q), letter, count in (((B, C), "a", 1), ((C, A), "b", 2), ((A, B), "c", 3)):
            m = ((p[0] + q[0]) / 2, (p[1] + q[1]) / 2)
            midpoints.append(m)
            side, inward = unit(p, q), unit(m, o)
            diag.connect(along(m, inward, -30), centre, **CONSTRUCTION)
            diag.point(*m, dot=True, radius=2.0)
            name(f"$M_{letter}$", along(along(m, inward, -14), side, 18), size=13)
            # A right-angle mark in the corner between the side and its bisector.
            corner = along(m, side, -8)
            marks += [(corner, along(corner, inward, 8)), (along(corner, inward, 8), along(m, inward, 8))]
            for end in (p, q):
                quarter = ((m[0] + end[0]) / 2, (m[1] + end[1]) / 2)
                for k in range(count):
                    tick = along(quarter, side, (k - (count - 1) / 2) * 4)
                    marks.append((along(tick, inward, -5), along(tick, inward, 5)))
        diag.path(strokes(marks), style=FINE)

        for vertex, letter in ((A, "A"), (B, "B"), (C, "C")):
            diag.connect(centre, diag.point(*vertex, dot=True), **RADIUS)
            name(f"${letter}$", along(vertex, unit(o, vertex), 15))
        name("$O$", along(o, widest_gap(o, [A, B, C, *midpoints]), 17))
        name("$R$", along(along(o, unit(o, C), r / 2), (0.0, -1.0), 11), size=13)

        diag.text(
            "The perpendicular bisectors of the\nsides meet at the circumcentre $O$,\n"
            "which is equally far from the vertices:\n\n"
            "$|OA| = |OB| = |OC| = R$",
            size=13,
        ).at(o[0] + r + 40, o[1] - 45)
        diag.caption(
            "**Figure 10:** The circumcircle of triangle $ABC$, centred where the perpendicular bisectors meet",
            small_caps=True,
        )
    return diag


def build_diagram(output_dir: Path | str = "output/technical") -> Path:
    return render_all(diagram(), output_dir, "10_geometric_construction")["svg"]


if __name__ == "__main__":
    dest = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("output/technical")
    build_diagram(dest)
