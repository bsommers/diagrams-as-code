"""A 99.9% availability SLO over 30 days: error budget remaining and daily burn rate.

The budget is computed in the script: 0.1% of 30 days is 43.2 minutes of
allowed unavailability. Five incidents and a small constant background error
rate consume it. The left chart is the budget left as the window advances,
against the straight line a budget spent evenly would follow. The right chart
is the burn rate per day (budget consumed relative to the even pace); the
usual multi-window alert thresholds are 1x (spent evenly, ticket) and 6x (page).
"""
from __future__ import annotations

import sys
from pathlib import Path

from diagrams_as_code import Diagram, Style
from diagrams_as_code.output import render_all
from diagrams_as_code.plot import Plot

INK = "#1F2F57"
DAYS, SLO = 30, 0.999
BUDGET = DAYS * 24 * 60 * (1 - SLO)  # minutes of allowed downtime: 43.2
BACKGROUND = 0.2  # minutes of errors per day
INCIDENTS = [(3.2, 5.0), (8.6, 14.0), (14.1, 3.0), (18.4, 6.0), (24.7, 4.0)]  # (day, minutes)
GOOD, WARN, BAD = "#8FB3DE", "#E8C26A", "#D9776A"
EVEN = BUDGET / DAYS  # minutes per day if spent evenly


def budget_path() -> list[tuple[float, float]]:
    """(day, minutes remaining): a slow slope with a vertical drop at every incident."""
    pts, left, t = [(0.0, BUDGET)], BUDGET, 0.0
    for day, minutes in INCIDENTS + [(float(DAYS), 0.0)]:
        left -= BACKGROUND * (day - t)
        pts.append((day, left))
        left -= minutes
        pts.append((day, left))
        t = day
    return pts


def daily_burn() -> list[tuple[float, float]]:
    spent = [BACKGROUND] * DAYS
    for day, minutes in INCIDENTS:
        spent[int(day)] += minutes
    return [(d + 0.5, s / EVEN) for d, s in enumerate(spent)]


def diagram() -> Diagram:
    path = budget_path()
    remaining = path[-1][1]
    burn = daily_burn()
    with Diagram("SLO error budget and burn rate", theme="paper") as diag:
        # Left: budget remaining.
        a = Plot(diag, x=(0, DAYS), y=(0, 45), origin=(90, 400), size=(520, 280))
        a.grid(xstep=5, ystep=10)
        a.axes(xlabel="Day", ylabel="Budget left (min)", xstep=5, ystep=10,
               through_zero=False, arrows=False)
        a.line((0, BUDGET), (DAYS, 0), stroke="#8A5A00", width=1.2, dash="6,4")
        a.polyline(path, stroke="#2F6DB5", width=2.4)
        a.hline(0, stroke="#B03A2E", dash="", width=1.2)
        for k, (day, minutes) in enumerate(INCIDENTS, start=1):
            top = next(y for x, y in path if x == day)
            a.dot(day, top - minutes, radius=3.5, fill="#B03A2E", stroke="#B03A2E")
            a.label(day, top - minutes, f"INC-{k}: {minutes:g} min", size=11, anchor="top_center", dy=9)
        a.label(0.5, 0, "budget exhausted at 0", size=11, anchor="bottom_left", dy=-4)
        a.legend([("budget left", "#2F6DB5", ""), ("even pace", "#8A5A00", "6,4")], at=a.px(21, 43))
        diag.text("**Budget remaining**", size=14).at(90, 80, anchor="bottom_left")

        # Right: burn rate per day.
        b = Plot(diag, x=(0, DAYS), y=(0, 12), origin=(730, 400), size=(520, 280))
        b.grid(xstep=5, ystep=2)
        b.axes(xlabel="Day", ylabel="Burn rate (x)", xstep=5, ystep=2,
               through_zero=False, arrows=False)
        for x, v in burn:
            b.bar_chart([(x, v)], width=0.7, fill=BAD if v >= 6 else WARN if v >= 1 else GOOD, stroke=INK)
        b.hline(1, stroke="#8A5A00")
        b.hline(6, stroke="#B03A2E")
        b.label(DAYS, 1, "1x: ticket", size=11, anchor="bottom_right", dx=-4, dy=-3)
        b.label(DAYS, 6, "6x: page", size=11, anchor="bottom_right", dx=-4, dy=-3)
        worst = max(burn, key=lambda p: p[1])
        b.label(worst[0], worst[1], f"{worst[1]:.1f}x", size=11, anchor="bottom_center", dy=-4)
        b.legend([("under pace", GOOD, "fill"), ("above even pace", WARN, "fill"), ("page", BAD, "fill")],
                 at=b.px(21, 11.8))
        diag.text("**Burn rate per day**", size=14).at(730, 80, anchor="bottom_left")

        diag.caption(
            f"**Figure:** {SLO:.1%} availability over {DAYS} days allows {BUDGET:.1f} minutes of downtime. "
            f"Five incidents leave {remaining:.1f} minutes ({remaining / BUDGET:.0%}) of the budget.",
            small_caps=True,
        )
    return diag


def build_diagram(output_dir: Path | str = "examples/devops") -> Path:
    return render_all(diagram(), output_dir, "08_slo_error_budget_burn")["svg"]


if __name__ == "__main__":
    dest = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("examples/devops")
    build_diagram(dest)
