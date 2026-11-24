"""Tumbling, sliding and session windows over one event stream (DATA ENGINEERING domain).

The same ten events are grouped three ways in event time. Tumbling windows
are fixed and disjoint (size 10 s); sliding windows have size 10 s and a
5 s slide so each event lands in two windows; session windows close after a
5 s gap with no event. Counts are computed from the event list.
"""
from __future__ import annotations

import sys
from pathlib import Path

from diagrams_as_code import Diagram, Style
from diagrams_as_code.output import render_all
from diagrams_as_code.plot import Plot

EVENTS = [1, 3, 4, 8, 9, 15, 16, 17, 24, 25]    # event times in seconds
SPAN = 30
SIZE, SLIDE, GAP = 10, 5, 5
INK = "#1F2F57"
FILLS = ["#9DC3E6", "#F6C98B", "#A9D9B1", "#E3B5D9", "#F2E39A"]
OX, W = 190.0, 620.0


def count(lo: float, hi: float) -> int:
    return sum(1 for t in EVENTS if lo <= t < hi)


def sessions() -> list[tuple[int, int]]:
    out, start, last = [], EVENTS[0], EVENTS[0]
    for t in EVENTS[1:]:
        if t - last >= GAP:
            out.append((start, last + GAP))
            start = t
        last = t
    out.append((start, last + GAP))
    return out


def window(diag: Diagram, p: Plot, lo: float, hi: float, y0: float, y1: float, fill: str, text: str) -> None:
    pts = [p.px(lo, y0), p.px(lo, y1), p.px(min(hi, SPAN), y1), p.px(min(hi, SPAN), y0)]
    diag.polygon(pts, style=Style(fill=fill, stroke=INK, stroke_width=1.2, fill_opacity=0.65), z=0)
    cx, cy = p.px((lo + min(hi, SPAN)) / 2, (y0 + y1) / 2)
    diag.text(text, size=11).at(cx, cy, anchor="center")


def panel(diag: Diagram, title: str, sub: str, bottom: float, height: float, rows: int) -> Plot:
    p = Plot(diag, x=(0, SPAN), y=(0, rows), origin=(OX, bottom), size=(W, height))
    p.axes(xstep=5, ystep=1, through_zero=False, arrows=False, size=10, ylabels=False)
    diag.text(f"**{title}**\n{sub}", size=13).at(40, bottom - height / 2, anchor="left_center")
    for t in EVENTS:
        p.dot(t, 0, radius=3.5)
    return p


def diagram() -> Diagram:
    with Diagram("Stream Windows: Tumbling, Sliding and Session", theme="paper") as diag:
        ev = Plot(diag, x=(0, SPAN), y=(0, 1), origin=(OX, 120), size=(W, 40))
        ev.axes(xstep=5, through_zero=False, arrows=False, size=10, ylabels=False)
        diag.text("**Events**", size=13).at(40, 100, anchor="left_center")
        for t in EVENTS:
            ev.dot(t, 0.5, radius=4.5)

        p1 = panel(diag, "Tumbling", "size 10 s", 240, 60, 1)
        for i, lo in enumerate(range(0, SPAN, SIZE)):
            window(diag, p1, lo, lo + SIZE, 0.15, 0.9, FILLS[i], f"[{lo}, {lo + SIZE})  n={count(lo, lo + SIZE)}")

        starts = list(range(0, SPAN, SLIDE))[:5]
        p2 = panel(diag, "Sliding", "size 10 s, slide 5 s", 420, 130, 5)
        for i, lo in enumerate(starts):
            window(diag, p2, lo, lo + SIZE, 4 - i + 0.1, 4 - i + 0.9, FILLS[i % 5],
                   f"[{lo}, {lo + SIZE})  n={count(lo, lo + SIZE)}")

        p3 = panel(diag, "Session", "gap 5 s", 540, 60, 1)
        for i, (lo, hi) in enumerate(sessions()):
            window(diag, p3, lo, hi, 0.15, 0.9, FILLS[i], f"[{lo}, {hi})  n={count(lo, hi)}")

        diag.text("event time (s)", size=12).at(OX + W / 2, 575, anchor="top_center")
        diag.text(
            "Tumbling: every event is in exactly one window. Sliding: an event is in size / slide = 2 windows\n"
            "(only 1 for events before 5 s: windows starting before 0 are omitted). Session: window length follows the data, and an\n"
            "event within 5 s of the previous one extends the session.",
            size=12, line_height=1.4,
        ).at(40, 620)
    return diag


def build_diagram(output_dir: Path | str = "examples/data_engineering") -> Path:
    return render_all(diagram(), output_dir, "04_stream_windows")["svg"]


if __name__ == "__main__":
    dest = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("examples/data_engineering")
    build_diagram(dest)
