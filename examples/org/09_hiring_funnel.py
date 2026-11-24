"""Example: Hiring funnel (ORGANISATION domain, plot kit).

Candidates remaining at each stage of an engineering hiring pipeline, drawn as
horizontal bars on a linear axis so the drop-off is read at true scale, with the
stage-to-stage conversion alongside.
"""
from __future__ import annotations

import sys
from pathlib import Path

from diagrams_as_code import Diagram, Style
from diagrams_as_code.output import render_all
from diagrams_as_code.plot import Plot

INK = "#1F2F57"
STAGES = (
    ("Applications", 1200),
    ("Recruiter screen", 320),
    ("Hiring manager interview", 140),
    ("Onsite loop", 60),
    ("Offer", 18),
    ("Accepted", 14),
)
FILLS = ("#8FB3DE", "#8FB3DE", "#8FB3DE", "#8FB3DE", "#A9D3B0", "#E3A9A0")
XMAX = 1500
ORIGIN, SIZE = (300.0, 400.0), (620.0, 300.0)


def diagram() -> Diagram:
    n = len(STAGES)
    with Diagram("Hiring funnel", theme="paper") as diag:
        p = Plot(diag, x=(0, XMAX), y=(0, n), origin=ORIGIN, size=SIZE)
        p.grid(xstep=300)
        p.axes(xlabel="Candidates", xstep=300, through_zero=False, arrows=False, ylabels=False, ystep=1)
        diag.text("**Stage-to-stage conversion**", size=12).at(ORIGIN[0] + SIZE[0] + 40, p.px(0, n)[1] - 18,
                                                                  anchor="left_center")
        for i, (name, count) in enumerate(STAGES):
            yc = n - i - 0.5
            half = 0.32
            pts = [p.px(0, yc - half), p.px(0, yc + half), p.px(count, yc + half), p.px(count, yc - half)]
            diag.polygon(pts, style=Style(fill=FILLS[i], stroke=INK, stroke_width=0.9), z=0)
            x, y = p.px(0, yc)
            diag.text(name, size=13).at(x - 14, y, anchor="right_center")
            diag.text(f"**{count:,}**", size=13).at(p.px(count, yc)[0] + 8, y, anchor="left_center")
            if i:
                prev = STAGES[i - 1][1]
                diag.text(f"{count / prev:.0%} of {STAGES[i - 1][0].lower()}", size=12).at(
                    ORIGIN[0] + SIZE[0] + 40, y, anchor="left_center")
        total = STAGES[-1][1] / STAGES[0][1]
        diag.caption(
            f"**Figure:** Hiring funnel for one quarter of engineering hiring. "
            f"{STAGES[-1][1]} of {STAGES[0][1]:,} applicants joined ({total:.1%} overall); "
            f"the recruiter screen is the largest cut.",
            small_caps=True,
        )
    return diag


def build_diagram(output_dir: Path | str = "examples/org") -> Path:
    return render_all(diagram(), output_dir, "09_hiring_funnel")["svg"]


if __name__ == "__main__":
    build_diagram(Path(sys.argv[1]) if len(sys.argv) > 1 else Path("examples/org"))
