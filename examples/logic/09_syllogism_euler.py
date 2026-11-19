"""Three valid syllogisms shown as Euler diagrams.

Each panel states two premises and a conclusion about the terms $S$ (subject),
$P$ (predicate) and $M$ (middle). Circles show how the classes must be nested,
separate or overlapping for the premises to hold; the conclusion can then be
read straight off the picture. A cross marks a region known to be non-empty,
which is what "some" asserts. The circle geometry is checked by the script
against each premise before anything is drawn.
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

from diagrams_as_code import Diagram, Style
from diagrams_as_code.output import render_all

RING = Style(fill="none", stroke="#111111", stroke_width=1.6)
FILLS = ("#F1F1F1", "#DCE6F2", "#BFD3EC")
PANEL_W = 310.0
TOP = 110.0

Circle = tuple[float, float, float]  # cx, cy, r


def inside(a: Circle, b: Circle) -> bool:
    """Circle ``a`` lies wholly inside ``b``."""
    return math.hypot(a[0] - b[0], a[1] - b[1]) + a[2] <= b[2]


def apart(a: Circle, b: Circle) -> bool:
    return math.hypot(a[0] - b[0], a[1] - b[1]) >= a[2] + b[2]


def overlap(a: Circle, b: Circle) -> bool:
    return not apart(a, b) and not inside(a, b) and not inside(b, a)


def circle(diag: Diagram, c: Circle, fill: str, fill_opacity: float = 1.0) -> None:
    cx, cy, r = c
    diag.path(
        f"M {cx - r:.2f} {cy:.2f} A {r} {r} 0 1 0 {cx + r:.2f} {cy:.2f} A {r} {r} 0 1 0 {cx - r:.2f} {cy:.2f} Z",
        style=Style(fill=fill, fill_opacity=fill_opacity, stroke="#111111", stroke_width=1.6), obstacle=False,
    )


def label(diag: Diagram, name: str, x: float, y: float) -> None:
    diag.text(f"${name}$", size=16).at(x, y, anchor="center")


def argument(diag: Diagram, cx: float, title: str, premises: list[str], conclusion: str) -> None:
    diag.text(title, size=14, align="center").at(cx, 44, anchor="center")
    y = TOP + 215
    lines = premises
    for k, text in enumerate(lines):
        diag.text(text, size=14).at(cx - 100, y + k * 24, anchor="left_center")
    bar = y + len(lines) * 24 - 8
    diag.polyline([(cx - 110, bar), (cx + 110, bar)], style=Style(stroke="#111111", stroke_width=1.2), obstacle=False)
    diag.text(conclusion, size=14).at(cx - 100, bar + 18, anchor="left_center")


def diagram() -> Diagram:
    with Diagram("Syllogisms as Euler diagrams", theme="paper") as diag:
        cy = TOP + 90

        # 1. Barbara: all M are P, all S are M, so all S are P -- nested circles.
        cx = 170.0
        P, M, S = (cx, cy, 84.0), (cx, cy + 14, 56.0), (cx, cy + 26, 28.0)
        assert inside(M, P) and inside(S, M)
        for c, f in ((P, FILLS[0]), (M, FILLS[1]), (S, FILLS[2])):
            circle(diag, c, f)
        label(diag, "P", cx, cy - 66)
        label(diag, "M", cx, cy - 30)
        label(diag, "S", cx, cy + 26)
        argument(diag, cx, "**Barbara** (AAA-1)", ["All $M$ are $P$.", "All $S$ are $M$."], "So all $S$ are $P$.")

        # 2. Celarent: no M is P, all S are M, so no S is P -- P apart from M, S inside M.
        cx = 170.0 + PANEL_W
        P, M = (cx - 62, cy, 52.0), (cx + 58, cy, 56.0)
        S = (cx + 58, cy + 12, 26.0)
        assert apart(P, M) and inside(S, M)
        circle(diag, P, FILLS[0])
        circle(diag, M, FILLS[1])
        circle(diag, S, FILLS[2])
        label(diag, "P", cx - 62, cy)
        label(diag, "M", cx + 58, cy - 38)
        label(diag, "S", cx + 58, cy + 12)
        argument(diag, cx, "**Celarent** (EAE-1)", ["No $M$ is $P$.", "All $S$ are $M$."], "So no $S$ is $P$.")

        # 3. Darii: all M are P, some S are M, so some S are P -- M inside P, S overlapping M; the
        #    cross marks a member of S that is also in M and so, by the first premise, in P.
        cx = 170.0 + 2 * PANEL_W
        P, M, S = (cx - 6, cy, 86.0), (cx - 26, cy, 50.0), (cx + 46, cy, 48.0)
        assert inside(M, P) and overlap(S, M) and overlap(S, P)
        circle(diag, P, FILLS[0])
        circle(diag, M, FILLS[1])
        circle(diag, S, "#8FB0DC", 0.5)
        lens_x = (S[0] - S[2] + M[0] + M[2]) / 2
        label(diag, "P", cx - 6, cy - 70)
        label(diag, "M", cx - 54, cy)
        label(diag, "S", cx + 90, cy - 56)
        diag.text(r"$\times$", size=28).at(lens_x, cy, anchor="center")
        argument(diag, cx, "**Darii** (AII-1)", ["All $M$ are $P$.", "Some $S$ are $M$."], "So some $S$ are $P$.")

        diag.text(
            "Nested circles read as *all*, separate circles as *no*, and a cross in an overlap as *some*.",
            size=12, font="serif", italic=True,
        ).at(60, TOP + 340)
        diag.caption(
            "**Figure 9:** Three valid syllogisms as Euler diagrams, with the conclusion read from the picture",
            small_caps=True,
        )
    return diag


def build_diagram(output_dir: Path | str = "examples/logic") -> Path:
    return render_all(diagram(), output_dir, "09_syllogism_euler")["svg"]


if __name__ == "__main__":
    dest = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("examples/logic")
    build_diagram(dest)
