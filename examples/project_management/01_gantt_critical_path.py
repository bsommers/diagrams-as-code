"""A product launch plan as a Gantt chart, critical path computed and highlighted.

Only the first task has a date. Every other start follows from durations and
finish-to-start dependencies, the critical path is found by a forward and a
backward pass (zero-slack tasks), and the bars, arrows and milestones on it are
drawn in red. Percent complete fills each bar from the left; the dashed line is
the status date.
"""
from __future__ import annotations

import sys
from datetime import date
from pathlib import Path

from diagrams_as_code import Diagram
from diagrams_as_code.gantt import GanttChart
from diagrams_as_code.output import render_all

KICKOFF = date(2026, 3, 2)
STATUS = date(2026, 3, 30)


def chart(diag: Diagram) -> GanttChart:
    g = GanttChart(diag, today=STATUS, width=760, origin=(40, 40))
    with g.phase("Discovery"):
        g.task("research", "User research", start=KICKOFF, duration=10, progress=1.0)
        g.task("spec", "Product spec", after="research", duration=5, progress=1.0)
        g.task("arch", "Architecture review", after="research", duration=4, progress=1.0)
    g.milestone("signoff", "Spec sign-off", after=["spec", "arch"])
    with g.phase("Build"):
        g.task("api", "Backend API", after="signoff", duration=20, progress=0.45)
        g.task("ui", "Web client", after="signoff", duration=15, progress=0.6)
        g.task("data", "Data migration", after="signoff", duration=8, progress=0.8)
        g.task("integ", "Integration tests", after=["api", "ui"], duration=6)
    with g.phase("Launch"):
        g.task("docs", "Docs and training", after="ui", duration=7)
        g.task("beta", "Private beta", after=["integ", "data"], duration=10)
        g.task("fix", "Beta fixes", after="beta", duration=5)
    g.milestone("ga", "General availability", after=["fix", "docs"])
    return g


def diagram() -> Diagram:
    with Diagram("Launch plan Gantt chart", theme="pastel_light") as diag:
        g = chart(diag)
        layout = g.draw()
        labels = {t.id: t.label for t in g.tasks}
        path = " → ".join(labels[t] for t in layout.schedule.critical_path)
        diag.caption(
            f"**Figure 1:** A {(layout.schedule.finish - layout.schedule.start).days}-day launch plan. "
            f"Critical path (red, zero slack): {path}",
            small_caps=True, max_width=900,
        )
    return diag


def build_diagram(output_dir: Path | str = "examples/project_management") -> Path:
    return render_all(diagram(), output_dir, "01_gantt_critical_path")["svg"]


if __name__ == "__main__":
    dest = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("examples/project_management")
    build_diagram(dest)
