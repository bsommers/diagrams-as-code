"""An idempotent backfill on a daily-partitioned table (DATA ENGINEERING domain).

A scheduled run loads one partition per day and fails on day 9, leaving a
partial partition and nothing after it. The backfill re-runs days 9-14 with
INSERT OVERWRITE on each date partition (delete + insert in one transaction),
so the result depends only on the source data. Re-running day 12 again, for
late-arriving events, changes nothing but its content: no duplicates.
Row counts are illustrative.
"""
from __future__ import annotations

import sys
from pathlib import Path

from diagrams_as_code import Diagram, Style
from diagrams_as_code.output import render_all
from diagrams_as_code.plot import Plot

DAYS = 14
OK = Style(fill="#BFE5C8", stroke="#2E7D4F", font_size=11)
FAIL = Style(fill="#F5C2C2", stroke="#C0392B", font_size=11)
SKIP = Style(fill="#E5E5E5", stroke="#9A9A9A", font_size=11, dash="3,3")
REDO = Style(fill="#C9E7F5", stroke="#1E88C7", font_size=11)
LATE = Style(fill="#FDE9B5", stroke="#C98A00", font_size=11)
HEAD = Style(fill="#FFFFFF", stroke="#FFFFFF", font_size=11)
PX, CW, PITCH = 252.0, 42.0, 46.0
BEFORE = [118, 121, 117, 125, 130, 98, 95, 122, 41, 0, 0, 0, 0, 0]
AFTER = [118, 121, 117, 125, 130, 98, 95, 122, 119, 124, 126, 131, 127, 120]


def row(diag: Diagram, y: float, label: str, styles: list[tuple[int, Style, str]]) -> None:
    head, _, sub = label.partition("\n")
    diag.text(f"**{head}**" + (f"\n{sub}" if sub else ""), size=12).at(40, y + 17, anchor="left_center")
    for day, style, text in styles:
        diag.shape(text, CW, 34, style=style, fit_label=False).at(PX + (day - 1) * PITCH, y)


def diagram() -> Diagram:
    with Diagram("Idempotent Backfill Timeline", theme="paper") as diag:
        for d in range(1, DAYS + 1):
            diag.text(f"Nov {d}", size=11).at(PX + (d - 1) * PITCH + CW / 2, 90, anchor="center")
        row(diag, 105, "1. Scheduled run",
            [(d, OK, "ok") for d in range(1, 9)] + [(9, FAIL, "fail")] + [(d, SKIP, "") for d in range(10, 15)])
        row(diag, 155, "2. Backfill 9 to 14\nINSERT OVERWRITE", [(d, REDO, "redo") for d in range(9, 15)])
        row(diag, 205, "3. Re-run day 12\nlate events", [(12, LATE, "redo")])

        p = Plot(diag, x=(0.5, DAYS + 0.5), y=(0, 160), origin=(PX - 2, 470), size=(DAYS * PITCH, 180))
        p.grid(xstep=1, ystep=40)
        p.axes(ylabel="", xstep=1, ystep=40, through_zero=False, arrows=False, xlabels=False)
        p.bar_chart([(d - 0.2, BEFORE[d - 1]) for d in range(1, DAYS + 1)], width=0.36, fill="#C9CDD6")
        p.bar_chart([(d + 0.2, AFTER[d - 1]) for d in range(1, DAYS + 1)], width=0.36, fill="#7FB38E")
        diag.text("**Rows per partition**", size=12).at(40, 380, anchor="left_center")
        diag.text("grey: after run 1\ngreen: after backfill", size=11).at(40, 410, anchor="left_center")
        p.label(9, 41, "partial", size=10, dx=-16, dy=-12)
        diag.text(
            "Why re-running is safe: each task writes only its own date partition, replacing it as one unit (an atomic\n"
            "partition swap or a transaction), and reads a fixed event_date range, never now(). The same input gives the\n"
            "same partition however many times the task runs. A plain INSERT would double the counts on every retry.",
            size=12, line_height=1.4,
        ).at(40, 535)
    return diag


def build_diagram(output_dir: Path | str = "examples/data_engineering") -> Path:
    return render_all(diagram(), output_dir, "08_idempotent_backfill_timeline")["svg"]


if __name__ == "__main__":
    dest = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("examples/data_engineering")
    build_diagram(dest)
