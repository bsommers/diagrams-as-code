"""A year of release trains on one timeline.

Each train is a shaded span from branch cut to release, labelled in a lane under
the ruler; overlapping trains take separate lanes. Releases are flagged above
the ruler and code freezes below it. Labels stack automatically so that none
overlap and no stem crosses another label, however close the dates fall.
"""
from __future__ import annotations

import sys
from datetime import date, timedelta
from pathlib import Path

from diagrams_as_code import Diagram
from diagrams_as_code.gantt import Timeline
from diagrams_as_code.output import render_all

#: (train, branch cut, release). Each train stabilises for two weeks after its freeze.
TRAINS = [
    ("26.1", date(2026, 1, 5), date(2026, 2, 23)),
    ("26.2", date(2026, 2, 16), date(2026, 4, 6)),
    ("26.3", date(2026, 3, 30), date(2026, 5, 18)),
    ("26.4", date(2026, 5, 11), date(2026, 6, 29)),
    ("26.5", date(2026, 6, 22), date(2026, 8, 10)),
    ("26.6", date(2026, 8, 3), date(2026, 9, 21)),
    ("26.7", date(2026, 9, 14), date(2026, 11, 2)),
    ("26.8", date(2026, 10, 26), date(2026, 12, 14)),
]
HOTFIXES = [(date(2026, 3, 3), "26.1.1 hotfix"), (date(2026, 7, 21), "26.4.2 security fix")]


def diagram() -> Diagram:
    with Diagram("Release trains 2026", theme="pastel_light") as diag:
        t = Timeline(diag, width=1100, origin=(40, 40), label_width=150)
        for name, cut, release in TRAINS:
            t.span(cut, release, f"Train {name}")
            t.event(release, f"**{name}** release", marker="diamond")
            t.event(release - timedelta(days=14), f"{name} code freeze", side="below")
        for when, label in HOTFIXES:
            t.event(when, label, color="#B03A2E")
        t.draw()
        diag.caption(
            "**Figure 2:** Release trains in 2026: releases above the ruler, code freezes "
            "below, each train's span in its own lane",
            small_caps=True, max_width=900,
        )
    return diag


def build_diagram(output_dir: Path | str = "examples/project_management") -> Path:
    return render_all(diagram(), output_dir, "02_release_train_timeline")["svg"]


if __name__ == "__main__":
    dest = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("examples/project_management")
    build_diagram(dest)
