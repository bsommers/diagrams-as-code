"""A sprint burndown chart: ideal line against actual remaining work, with a forecast.

The sprint has 10 working days and 40 story points. Each day's completed points
are the only input; remaining work, the ideal line, the gap to ideal and the
forecast finish are all computed. A scope increase on day 4 shows as a vertical
step up. The dashed forecast extends today's average velocity to zero and lands
after the sprint's last day, so the chart says plainly that the sprint will
overrun.
"""
from __future__ import annotations

import sys
from pathlib import Path

from diagrams_as_code import Diagram
from diagrams_as_code.output import render_all
from diagrams_as_code.plot import Plot

SPRINT_DAYS = 10
COMMITTED = 40
TODAY = 7
DONE_PER_DAY = [3, 4, 2, 5, 3, 4, 5]          # points completed on days 1..TODAY
SCOPE_ADDED = {4: 6}                          # day -> points added at the end of that day

IDEAL = "#2E8B57"
ACTUAL = "#1F4E9E"
FORECAST = "#B8860B"
ALERT = "#8A1C1C"


def remaining_series() -> list[tuple[float, float]]:
    """Remaining-work points; a scope increase adds a vertical step at its day."""
    pts = [(0.0, float(COMMITTED))]
    left = float(COMMITTED)
    for day, done in enumerate(DONE_PER_DAY, start=1):
        left -= done
        pts.append((float(day), left))
        if day in SCOPE_ADDED:
            left += SCOPE_ADDED[day]
            pts.append((float(day), left))
    return pts


def diagram() -> Diagram:
    pts = remaining_series()
    left = pts[-1][1]
    scope = COMMITTED + sum(SCOPE_ADDED.values())
    velocity = sum(DONE_PER_DAY) / TODAY
    finish_day = TODAY + left / velocity
    ideal_today = COMMITTED * (1 - TODAY / SPRINT_DAYS)
    behind = left - ideal_today
    overrun = finish_day - SPRINT_DAYS
    leftover = left - velocity * (SPRINT_DAYS - TODAY)

    with Diagram("Sprint burndown chart", theme="paper") as diag:
        p = Plot(diag, x=(0, 13), y=(0, 50), origin=(80, 380), size=(640, 320))
        p.grid(1, 10)
        p.axes(xlabel="Working day", ylabel="Remaining points", xstep=1, ystep=10, through_zero=False)
        p.vline(SPRINT_DAYS, stroke="#6B7280", dash="4,4")
        p.label(SPRINT_DAYS, 50, "sprint ends", size=11, color="#4B5563", anchor="left_center", dx=6, dy=10)

        p.polyline([(0, COMMITTED), (SPRINT_DAYS, 0)], stroke=IDEAL, width=2.0, dash="7,4")
        p.polyline(pts, stroke=ACTUAL, width=2.4)
        for x, y in pts:
            p.dot(x, y, radius=3.5, fill=ACTUAL, stroke=ACTUAL)
        p.polyline([(TODAY, left), (finish_day, 0)], stroke=FORECAST, width=2.0, dash="2,4")
        p.dot(finish_day, 0, radius=4.5, fill="#FFFFFF", stroke=FORECAST)
        p.label(finish_day, 0, f"forecast: day {finish_day:.1f}", size=12, color=FORECAST,
                anchor="bottom_left", dx=8, dy=-26)

        p.vline(TODAY, stroke="#8A5A00", dash="3,3")
        p.label(TODAY, 50, "today", size=11, color="#8A5A00", anchor="right_center", dx=-6, dy=10)
        # Gap to ideal today.
        p.line((TODAY + 0.25, ideal_today), (TODAY + 0.25, left), stroke=ALERT, width=1.8)
        p.label(TODAY + 0.25, left + 5, f"{behind:.0f} pts behind", size=12, color=ALERT, dx=8)
        # Scope step.
        day, add = next(iter(SCOPE_ADDED.items()))
        p.label(day, left_at(pts, day) + add, f"+{add} scope", size=12, color=ALERT, dy=-8,
                anchor="bottom_center")

        p.legend([("Ideal burndown", IDEAL, "7,4"), ("Actual remaining", ACTUAL, ""),
                  ("Forecast at average velocity", FORECAST, "2,4")], at=(500, 100))

        diag.text("**Sprint status, day %d of %d**" % (TODAY, SPRINT_DAYS), size=13).at(80, 432, anchor="left_center")
        diag.text(f"Committed {COMMITTED} pts, scope now {scope} pts, done {scope - left:.0f} pts, remaining {left:.0f} pts. "
                  f"Average velocity {velocity:.2f} pts per day.", size=12).at(80, 456, anchor="left_center")
        diag.text(f"At that pace {leftover:.0f} pts spill past day {SPRINT_DAYS}; the work finishes on day "
                  f"{finish_day:.1f}, {overrun:.1f} days late.", size=12, color=ALERT).at(80, 480, anchor="left_center")

        diag.caption(
            f"**Figure 7:** Sprint burndown on day {TODAY}: {behind:.0f} points behind the ideal line "
            f"after a {add}-point scope increase",
            small_caps=True, max_width=900,
        )
    return diag


def left_at(pts: list[tuple[float, float]], day: int) -> float:
    """The remaining work just before a scope step on ``day``."""
    return next(y for x, y in pts if x == day)


def build_diagram(output_dir: Path | str = "examples/project_management") -> Path:
    return render_all(diagram(), output_dir, "07_sprint_burndown")["svg"]


if __name__ == "__main__":
    dest = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("examples/project_management")
    build_diagram(dest)
