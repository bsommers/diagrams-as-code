"""Timing diagram of a valid/ready handshake carrying three bytes.

A clock and four signals share one time grid. Dashed guides mark the rising
clock edges; the data bus is drawn as hexagonal cells holding its value; and
two dimension arrows mark the setup and hold time of one byte about the edge
that samples it.
"""
from __future__ import annotations

import sys
from pathlib import Path

from diagrams_as_code import Diagram, Style
from diagrams_as_code.output import render_all

X0, PERIOD, EDGES = 160.0, 80.0, 6
X1 = X0 + PERIOD * EDGES + 20
TOP, PITCH, AMP = 80.0, 48.0, 22.0  # first row, row spacing, waveform height
SLOPE = 4.0  # width of a transition
DELAY = 28.0  # clock edge to output change
WAVE = Style(stroke_width=1.5)
HAIR = Style(stroke_width=0.7, stroke="#666666")
GUIDE = Style(stroke_width=0.7, stroke="#666666", dash="3,3")
CELL = Style(fill="#E4E4E8", stroke_width=1.5, font_size=11)
SMALL = 11.0


def edge(k: int) -> float:
    """x of rising clock edge number k (from 0)."""
    return X0 + PERIOD * (k + 0.5)


def wave(row: int, changes: list[float], level: int = 0) -> list[tuple[float, float]]:
    """Points of a two-level waveform that toggles at each x in ``changes``."""
    def y(lv: int) -> float:
        return TOP + row * PITCH + (0.0 if lv else AMP)

    points = [(X0, y(level))]
    for x in changes:
        points += [(x - SLOPE / 2, y(level)), (x + SLOPE / 2, y(1 - level))]
        level = 1 - level
    return points + [(X1, y(level))]


def diagram() -> Diagram:
    with Diagram("Valid/ready handshake timing", theme="paper") as diag:
        names = ["clk", "valid", "ready", "valid $\\land$ ready", "data[7:0]"]
        for row, name in enumerate(names):
            diag.text(name, size=13).at(X0 - 16, TOP + row * PITCH + AMP / 2, anchor="right_center")

        # Guides first, so the waveforms are painted over them.
        bottom = TOP + 4 * PITCH + AMP + 40
        for k in range(EDGES):
            diag.polyline([(edge(k), TOP - 12), (edge(k), bottom)], style=GUIDE, obstacle=False)
            diag.text(str(k + 1), size=SMALL, color="#555555").at(edge(k), TOP - 16, anchor="bottom_center")

        clock = [x for k in range(EDGES) for x in (edge(k), edge(k) + PERIOD / 2)]
        after = [edge(k) + DELAY for k in range(EDGES)]
        diag.polyline(wave(0, clock), style=WAVE)
        diag.polyline(wave(1, [after[0], after[4]]), style=WAVE)
        diag.polyline(wave(2, [after[1], after[4]]), style=WAVE)
        diag.polyline(wave(3, [after[1], after[4]]), style=WAVE)

        # The bus: idle on the centre line, then one hexagonal cell per byte.
        y0 = TOP + 4 * PITCH
        mid, y1, h = y0 + AMP / 2, y0 + AMP, SLOPE
        diag.polyline([(X0, mid), (after[0], mid)], style=WAVE)
        for value, a, b in (("0xA5", after[0], after[2]), ("0x3C", after[2], after[3]), ("0x7E", after[3], after[4])):
            diag.polygon([(a, mid), (a + h, y0), (b - h, y0), (b, mid), (b - h, y1), (a + h, y1)], value, style=CELL)
        diag.polyline([(after[4], mid), (X1, mid)], style=WAVE)

        # Setup and hold of the second byte about edge 4, which samples it.
        dim = y1 + 22
        for x in (after[2], after[3]):
            diag.polyline([(x, y1 + 2), (x, dim + 6)], style=HAIR, obstacle=False)
        arrow = {"routing": "direct", "two_way": True, "width": 0.75, "arrow_size": 0.6}
        diag.connect((after[2], dim), (edge(3), dim), **arrow)
        diag.connect((edge(3), dim), (after[3], dim), **arrow)
        diag.text("$t_{su}$", size=13).at((after[2] + edge(3)) / 2, dim + 5, anchor="top_center")
        diag.text("$t_h$", size=13).at(after[3] + 6, dim, anchor="left_center")

        diag.text(
            "A byte is taken on each rising edge at which *valid* and *ready* are both high: "
            "edges 3, 4 and 5. At edge 2 the receiver is not ready, so the sender holds 0xA5 for a second cycle.",
            size=12, max_width=X1 - X0, font="serif", italic=True,
        ).at(X0, bottom + 14)
        diag.caption("**Figure 7:** Valid/ready handshake with setup and hold times of the data bus",
                     small_caps=True)
    return diag


def build_diagram(output_dir: Path | str = "output/technical") -> Path:
    return render_all(diagram(), output_dir, "07_timing_diagram")["svg"]


if __name__ == "__main__":
    dest = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("output/technical")
    build_diagram(dest)
