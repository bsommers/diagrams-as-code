"""A cumulative flow diagram (CFD) of a four-week delivery, drawn with the plot kit.

Four cumulative counts are tracked per working day: items arrived, started,
entered review and done. The bands between them are the columns of the board.
The vertical gap between the top and bottom of the in-progress stack at a day
is the work in progress, the horizontal gap between the "started" and "done"
curves is the cycle time. Both are measured from the data, not typed in. A band
that keeps widening (here, Review) is the bottleneck.
"""
from __future__ import annotations

import sys
from pathlib import Path

from diagrams_as_code import Diagram
from diagrams_as_code.output import render_all
from diagrams_as_code.plot import Plot

DAYS = 20
# Cumulative item counts per working day, top curve first.
ARRIVED = [round(8 + 3.2 * d) for d in range(DAYS + 1)]
STARTED = [round(2 + 2.6 * d) for d in range(DAYS + 1)]
REVIEW = [max(0, round(2.4 * (d - 2))) for d in range(DAYS + 1)]
DONE = [max(0, round(2.0 * (d - 3))) for d in range(DAYS + 1)]

BANDS = [  # (name, upper curve, lower curve, fill)
    ("Backlog", ARRIVED, STARTED, "#D9DEE7"),
    ("In progress", STARTED, REVIEW, "#9CC3E6"),
    ("Review", REVIEW, DONE, "#F2B880"),
    ("Done", DONE, None, "#8FCB9B"),
]
INK = "#1F2F57"


def at(series: list[int]):
    """Piecewise-linear interpolation of a per-day series."""
    def f(x: float) -> float:
        x = min(max(x, 0.0), float(DAYS))
        i = min(int(x), DAYS - 1)
        return series[i] + (series[i + 1] - series[i]) * (x - i)
    return f


def day_reaching(series: list[int], value: float) -> float:
    """The (fractional) day on which a rising series first reaches ``value``."""
    for i in range(DAYS):
        if series[i] < value <= series[i + 1]:
            return i + (value - series[i]) / (series[i + 1] - series[i])
    raise ValueError("value not reached")


def check() -> None:
    for d in range(DAYS + 1):
        assert ARRIVED[d] >= STARTED[d] >= REVIEW[d] >= DONE[d] >= 0, d
        if d:
            for s in (ARRIVED, STARTED, REVIEW, DONE):
                assert s[d] >= s[d - 1]


def diagram() -> Diagram:
    check()
    with Diagram("Cumulative flow diagram", theme="paper") as diag:
        p = Plot(diag, x=(0, DAYS), y=(0, 80), origin=(80, 380), size=(600, 320))
        for _, top, bottom, fill in BANDS:
            p.area(at(top), 0, DAYS, g=at(bottom) if bottom else None, fill=fill, opacity=1.0)
        p.grid(2, 10)
        p.axes(xlabel="Working day", ylabel="Cumulative items", xstep=2, ystep=10, through_zero=False)
        for series in (ARRIVED, STARTED, REVIEW, DONE):
            p.polyline(list(enumerate(series)), stroke=INK, width=1.4)

        # Band labels at the right edge, centred on each band's last height.
        for name, top, bottom, _ in BANDS:
            hi, lo = top[DAYS], bottom[DAYS] if bottom else 0
            p.label(DAYS, (hi + lo) / 2, f"**{name}**  {hi - lo}", size=12, dx=10)

        # WIP at day 18: from the done curve to the started curve.
        d = 18
        lo, hi = DONE[d], STARTED[d]
        wip = hi - lo
        p.line((d, lo), (d, hi), stroke="#8A1C1C", width=1.8)
        for yy in (lo, hi):
            p.line((d - 0.25, yy), (d + 0.25, yy), stroke="#8A1C1C", width=1.8)
        p.label(d, (lo + hi) / 2, f"WIP = {wip}", size=12, color="#8A1C1C", anchor="right_center", dx=-8)

        # Cycle time for the item started on day 6: how long until the done curve reaches that count.
        ds = 6
        level = STARTED[ds]
        done_day = day_reaching(DONE, level)
        ct = done_day - ds
        p.line((ds, level), (done_day, level), stroke="#8A1C1C", width=1.8, dash="5,3")
        for xx in (ds, done_day):
            p.line((xx, level - 1.2), (xx, level + 1.2), stroke="#8A1C1C", width=1.8)
        p.label((ds + done_day) / 2, level, f"cycle time = {ct:.1f} d", size=12, color="#8A1C1C",
                anchor="bottom_center", dy=-6)

        # Little's law over the second half of the period: average WIP / throughput.
        span = range(10, DAYS + 1)
        avg_wip = sum(STARTED[x] - DONE[x] for x in span) / len(span)
        throughput = (DONE[DAYS] - DONE[10]) / (DAYS - 10)
        diag.text("**Flow metrics, days 10 to 20**", size=13).at(80, 430, anchor="left_center")
        diag.text(f"Average WIP {avg_wip:.1f} items;  throughput {throughput:.1f} items per day;  "
                  f"Little's law gives an average cycle time of {avg_wip / throughput:.1f} days",
                  size=12).at(80, 454, anchor="left_center")
        diag.text(f"Review holds {REVIEW[DAYS] - DONE[DAYS]} items and has grown every week: "
                  "add reviewers before starting more work", size=12, color="#8A1C1C").at(80, 478, anchor="left_center")

        diag.caption(
            f"**Figure 6:** Cumulative flow of {ARRIVED[DAYS]} items over {DAYS} working days; "
            f"{DONE[DAYS]} are done, and the widening Review band marks the bottleneck",
            small_caps=True, max_width=900,
        )
    return diag


def build_diagram(output_dir: Path | str = "examples/project_management") -> Path:
    return render_all(diagram(), output_dir, "06_cumulative_flow")["svg"]


if __name__ == "__main__":
    dest = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("examples/project_management")
    build_diagram(dest)
