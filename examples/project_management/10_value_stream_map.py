"""A value-stream map of a software change, from request to release.

Process boxes carry their data (cycle time, people, first-pass quality), the
triangles between them are queues, and the timeline ladder underneath steps up
over each wait and down over each process. A queue's length follows from its
wait and the takt time (one item per 8 hours), and the lead time, the value-added
share and the worst wait and slowest step are computed. Most of the lead time is
spent waiting, which is the usual finding and the reason to draw the map.
"""
from __future__ import annotations

import sys
from pathlib import Path

from diagrams_as_code import Diagram
from diagrams_as_code.output import render_all
from diagrams_as_code.style import Style

TAKT_H = 8.0   # one item arrives every 8 working hours

# (process, cycle time in hours, people, first-pass quality %, wait before it in hours)
STEPS = [
    ("Refine", 4, 2, 90, 40),
    ("Develop", 16, 3, 85, 16),
    ("Review", 3, 2, 80, 24),
    ("Test", 6, 2, 92, 32),
    ("Release", 1, 1, 98, 8),
]

GAP, BOX_W = 84, 120
X0, Y_BOX = 40, 150
TITLE_H, DATA_H = 32, 74
INK, ALERT, MUTED = "#2F3B52", "#C0392B", "#6B7280"


def rect(x0, y0, x1, y1):
    return [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]


def arrow(diag: Diagram, x0: float, y0: float, x1: float, y1: float, colour: str = INK, width: float = 1.8) -> None:
    """A straight horizontal or vertical arrow with a filled head."""
    dx, dy = (x1 > x0) - (x1 < x0), (y1 > y0) - (y1 < y0)
    hx, hy = x1 - dx * 9, y1 - dy * 9
    diag.path(f"M {x0:.2f} {y0:.2f} L {hx:.2f} {hy:.2f}", style=Style(fill="none", stroke=colour, stroke_width=width), z=1)
    px, py = -dy * 5, dx * 5
    diag.polygon([(x1, y1), (hx + px, hy + py), (hx - px, hy - py)], style=Style(fill=colour, stroke="none"), z=1)


def diagram() -> Diagram:
    waits = [s[4] for s in STEPS]
    cycles = [s[1] for s in STEPS]
    lead = sum(waits) + sum(cycles)
    pce = sum(cycles) / lead
    worst_wait = max(range(len(STEPS)), key=lambda i: (waits[i], -i))
    slowest = max(range(len(STEPS)), key=lambda i: (cycles[i], -i))
    rolled = 1.0
    for s in STEPS:
        rolled *= s[3] / 100

    with Diagram("Value stream map", theme="pastel_light") as diag:
        gap_x = [X0 + i * (GAP + BOX_W) for i in range(len(STEPS))]
        box_x = [g + GAP for g in gap_x]
        end_x = box_x[-1] + BOX_W

        # Source and sink.
        diag.polygon(rect(X0, 40, X0 + 120, 84), style=Style(fill="#E4E8EF", stroke=INK, stroke_width=1.4), z=0)
        diag.text("**Product owner**", size=12).at(X0 + 60, 62, anchor="center")
        diag.polygon(rect(end_x - 100, 40, end_x, 84), style=Style(fill="#E4E8EF", stroke=INK, stroke_width=1.4), z=0)
        diag.text("**Customers**", size=12).at(end_x - 50, 62, anchor="center")
        diag.text(f"1 change per {TAKT_H:g} h", size=11, color=MUTED).at(X0 + 128, 62, anchor="left_center")
        arrow(diag, gap_x[0] + GAP / 2, 84, gap_x[0] + GAP / 2, 152)
        arrow(diag, box_x[-1] + BOX_W / 2, Y_BOX, box_x[-1] + BOX_W / 2, 84)

        for i, (name, ct, people, fpq, wait) in enumerate(STEPS):
            bx = box_x[i]
            hot = i == slowest
            diag.polygon(rect(bx, Y_BOX, bx + BOX_W, Y_BOX + TITLE_H),
                         style=Style(fill=ALERT if hot else INK, stroke="none"), z=0)
            diag.text(f"**{name}**", size=13, color="#FFFFFF").at(bx + BOX_W / 2, Y_BOX + TITLE_H / 2, anchor="center")
            diag.polygon(rect(bx, Y_BOX + TITLE_H, bx + BOX_W, Y_BOX + TITLE_H + DATA_H),
                         style=Style(fill="#FFFFFF", stroke=ALERT if hot else INK, stroke_width=1.4), z=0)
            for k, line in enumerate((f"C/T {ct} h", f"{people} people", f"%C&A {fpq}%")):
                diag.text(line, size=12).at(bx + 12, Y_BOX + TITLE_H + 17 + k * 20, anchor="left_center")

            # Queue triangle in the gap before the box, and the push arrow beside it.
            gx = gap_x[i]
            tx, ty = gx + GAP / 2, Y_BOX + 58
            hotw = i == worst_wait
            diag.polygon([(tx, ty - 24), (tx + 20, ty + 10), (tx - 20, ty + 10)],
                         style=Style(fill="#F6EDB2", stroke=ALERT if hotw else INK, stroke_width=1.8 if hotw else 1.2), z=1)
            diag.text(f"**{round(wait / TAKT_H)}**", size=12, z=3).at(tx, ty + 2, anchor="center")
            diag.text(f"wait {wait} h", size=11, color=ALERT if hotw else MUTED).at(tx, ty + 28, anchor="center")
            if i:
                arrow(diag, gx - 4, Y_BOX + 16, gx + GAP / 2 - 26, Y_BOX + 16, colour=MUTED, width=1.4)
                arrow(diag, gx + GAP / 2 + 26, Y_BOX + 16, bx - 2, Y_BOX + 16, colour=MUTED, width=1.4)

        # Timeline ladder.
        top, bot = Y_BOX + TITLE_H + DATA_H + 56, Y_BOX + TITLE_H + DATA_H + 96
        pts = []
        for i in range(len(STEPS)):
            pts += [(gap_x[i], top), (box_x[i], top), (box_x[i], bot), (box_x[i] + BOX_W, bot),
                    (box_x[i] + BOX_W, top)]
        d = "M " + " L ".join(f"{x:.2f} {y:.2f}" for x, y in pts)
        diag.path(d, style=Style(fill="none", stroke=INK, stroke_width=1.6), z=1)
        for i, (name, ct, *_rest) in enumerate(STEPS):
            hotw = i == worst_wait
            diag.text(f"{waits[i]} h", size=12, color=ALERT if hotw else INK).at(
                gap_x[i] + GAP / 2, top - 12, anchor="center")
            diag.text(f"{ct} h", size=12, color=ALERT if i == slowest else INK).at(
                box_x[i] + BOX_W / 2, bot + 14, anchor="center")

        sy = bot + 52
        diag.polygon(rect(X0, sy, end_x, sy + 54), style=Style(fill="#F4F5F7", stroke="#C9CED6", stroke_width=1.0), z=-1)
        stats = [
            f"**Lead time** {lead} h ({lead / TAKT_H:.1f} takt periods)",
            f"**Process time** {sum(cycles)} h",
            f"**Waiting** {sum(waits)} h ({sum(waits) / lead:.0%})",
            f"**Value-added share** {pce:.0%}",
            f"**Rolled first-pass yield** {rolled:.0%}",
        ]
        col = (end_x - X0) / 3
        for k, line in enumerate(stats):
            diag.text(line, size=12).at(X0 + 14 + (k % 3) * col, sy + 18 + (k // 3) * 24, anchor="left_center")

        diag.caption(
            f"**Figure 10:** Value-stream map of one change: {lead} h lead time of which only {sum(cycles)} h "
            f"({pce:.0%}) is process; the longest wait is before {STEPS[worst_wait][0]} and the slowest step is {STEPS[slowest][0]}",
            small_caps=True, max_width=900,
        )
    return diag


def build_diagram(output_dir: Path | str = "examples/project_management") -> Path:
    return render_all(diagram(), output_dir, "10_value_stream_map")["svg"]


if __name__ == "__main__":
    dest = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("examples/project_management")
    build_diagram(dest)
