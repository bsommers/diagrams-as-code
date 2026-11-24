"""Example: Stakeholder power/interest grid (ORGANISATION domain).

The Mendelow grid: stakeholders plotted by their power over the project (vertical)
and their interest in it (horizontal). The quadrant sets the engagement strategy.
"""
from __future__ import annotations

import sys
from pathlib import Path

from diagrams_as_code import Diagram, Style
from diagrams_as_code.output import render_all
from diagrams_as_code.plot import Plot

INK = "#1F2F57"
#: quadrant -> (title, fill, stroke), keyed by (high interest, high power).
QUADRANTS = {
    (False, True): ("Keep satisfied", "#F8ECD3", "#B8860B"),
    (True, True): ("Manage closely", "#F6D9CC", "#B0502E"),
    (False, False): ("Monitor", "#EEF0F3", "#6B7280"),
    (True, False): ("Keep informed", "#DCEBDD", "#3C8D53"),
}
#: (name, interest 0-10, power 0-10)
STAKEHOLDERS = (
    ("Regulator", 1.8, 8.6), ("Board", 3.6, 7.0),
    ("Executive sponsor", 8.0, 8.8), ("Largest customer", 6.4, 7.2), ("Product owner", 8.4, 5.8),
    ("Vendors", 1.8, 1.8), ("Press", 3.4, 3.4),
    ("Engineering teams", 7.6, 3.8), ("End users", 6.6, 1.6), ("Support", 8.8, 2.6),
)
W, H = 130.0, 34.0


def diagram() -> Diagram:
    with Diagram("Stakeholder power/interest grid", theme="paper") as diag:
        p = Plot(diag, x=(0, 10), y=(0, 10), origin=(110, 540), size=(660, 440))
        for (hi_interest, hi_power), (title, fill, stroke) in QUADRANTS.items():
            x0, x1 = (5, 10) if hi_interest else (0, 5)
            y0, y1 = (5, 10) if hi_power else (0, 5)
            pts = [p.px(x0, y0), p.px(x0, y1), p.px(x1, y1), p.px(x1, y0)]
            diag.polygon(pts, style=Style(fill=fill, stroke=INK, stroke_width=0.8), z=-2)
            tx, ty = p.px(x0 + 0.15, y1 - 0.1)
            diag.text(f"**{title}**", size=13).at(tx, ty, anchor="top_left")
        p.axes(xlabel="", ylabel="", through_zero=False, arrows=False, labels=False)
        lx, ly = p.px(10, 0)
        diag.text("Interest", size=14).at(p.px(5, 0)[0], ly + 14, anchor="top_center")
        diag.text("low", size=12).at(p.px(0, 0)[0], ly + 14, anchor="top_left")
        diag.text("high", size=12).at(lx, ly + 14, anchor="top_right")
        diag.text("Power", size=14).at(p.px(0, 5)[0] - 34, p.px(0, 5)[1], anchor="right_center")
        diag.text("high", size=12).at(p.px(0, 10)[0] - 34, p.px(0, 10)[1] + 6, anchor="right_center")
        diag.text("low", size=12).at(p.px(0, 0)[0] - 34, p.px(0, 0)[1] - 6, anchor="right_center")

        for name, interest, power in STAKEHOLDERS:
            _, fill, stroke = QUADRANTS[(interest >= 5, power >= 5)]
            cx, cy = p.px(interest, power)
            diag.shape(name, W, H, style=Style(fill="#FFFFFF", stroke=stroke, stroke_width=1.6)).at(
                cx - W / 2, cy - H / 2)
    return diag


def build_diagram(output_dir: Path | str = "examples/org") -> Path:
    return render_all(diagram(), output_dir, "07_stakeholder_power_interest")["svg"]


if __name__ == "__main__":
    build_diagram(Path(sys.argv[1]) if len(sys.argv) > 1 else Path("examples/org"))
