"""A PERT / CPM activity network, with the critical path from the Gantt scheduler.

Each node is one activity: early start and finish in the top corners, late start
and finish in the bottom corners, duration under the name and the slack at the
foot. The numbers come from ``diagrams_as_code.gantt.schedule``, the same
critical-path method that draws the Gantt chart in example 01, so the two views
of one plan can never disagree. Zero-slack activities and the links that drive
them are red; the column of a node is its longest-path depth.
"""
from __future__ import annotations

import sys
from datetime import date
from pathlib import Path

from diagrams_as_code import Diagram
from diagrams_as_code.gantt import Task, schedule
from diagrams_as_code.output import render_all
from diagrams_as_code.style import Style

START = date(2026, 6, 1)
# id, name, duration (days), predecessors, row (vertical position, in rows)
PLAN = [
    ("A", "Requirements", 5, (), 1.0),
    ("B", "System design", 7, ("A",), 0.5),
    ("C", "Procure hardware", 10, ("A",), 2.0),
    ("D", "Build backend", 12, ("B",), 0.0),
    ("E", "Build web client", 8, ("B",), 1.0),
    ("F", "Install environment", 6, ("C",), 2.0),
    ("G", "Integration test", 5, ("D", "E", "F"), 1.0),
    ("H", "Deploy", 3, ("G",), 1.0),
]

NODE_W, NODE_H, GAP_X, ROW_H = 142, 80, 66, 106
X0, Y0 = 40, 40
RED, INK, GREY = "#C0392B", "#2F3B52", "#7A8394"


def rect(x0, y0, x1, y1):
    return [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]


def arrow(diag, pts, colour, width):
    """An orthogonal polyline with a filled head on its last, horizontal segment."""
    (hx, hy), (tx, ty) = pts[-2], pts[-1]
    base = (tx - 9, ty)
    path = pts[:-1] + [base]
    diag.path("M " + " L ".join(f"{x:.2f} {y:.2f}" for x, y in path),
              style=Style(fill="none", stroke=colour, stroke_width=width), z=1)
    diag.polygon([(tx, ty), (tx - 9, ty - 5), (tx - 9, ty + 5)], style=Style(fill=colour, stroke="none"), z=2)


def diagram() -> Diagram:
    tasks = [Task(id=i, label=n, duration=d, start=START if not p else None, after=p) for i, n, d, p, _ in PLAN]
    sched = schedule(tasks)
    level: dict[str, int] = {}
    for tid, _n, _d, preds, _r in PLAN:
        level[tid] = 1 + max((level[p] for p in preds), default=-1)
    row = {t[0]: t[4] for t in PLAN}

    def day(d: date) -> int:
        return (d - START).days

    def box(tid):
        x = X0 + level[tid] * (NODE_W + GAP_X)
        y = Y0 + row[tid] * ROW_H
        return x, y

    with Diagram("PERT network with critical path", theme="pastel_light") as diag:
        links = set(sched.critical_links)
        # Arrows first (drawn below nodes).
        edges = [(p, t[0]) for t in PLAN for p in t[3]]
        for p, tid in sorted(edges, key=lambda e: e in links):   # critical links drawn last, on top
            px, py = box(p)
            sx, sy = box(tid)
            x_mid = px + NODE_W + GAP_X / 2
            y0, y1 = py + NODE_H / 2, sy + NODE_H / 2
            crit = (p, tid) in links
            pts = [(px + NODE_W, y0), (x_mid, y0), (x_mid, y1), (sx, y1)]
            if y0 == y1:
                pts = [(px + NODE_W, y0), (sx, y1)]
            arrow(diag, pts, RED if crit else GREY, 2.2 if crit else 1.3)

        for tid, name, dur, _preds, _r in PLAN:
            s = sched.tasks[tid]
            x, y = box(tid)
            crit = s.critical
            diag.polygon(rect(x, y, x + NODE_W, y + NODE_H),
                         style=Style(fill="#FDECEA" if crit else "#FFFFFF", stroke=RED if crit else INK,
                                     stroke_width=2.2 if crit else 1.3), z=0)
            diag.polygon(rect(x, y + 22, x + NODE_W, y + 23), style=Style(fill=RED if crit else INK, stroke="none"), z=1)
            diag.polygon(rect(x, y + NODE_H - 22, x + NODE_W, y + NODE_H - 21), style=Style(fill=RED if crit else INK, stroke="none"), z=1)
            diag.text(str(day(s.start)), size=11, color=GREY).at(x + 8, y + 11, anchor="left_center")
            diag.text(str(day(s.finish)), size=11, color=GREY).at(x + NODE_W - 8, y + 11, anchor="right_center")
            diag.text(f"**{tid}  {name}**", size=12).at(x + NODE_W / 2, y + 33, anchor="center")
            diag.text(f"{dur} d", size=11, color=GREY).at(x + NODE_W / 2, y + 48, anchor="center")
            diag.text(str(day(s.latest_start)), size=11, color=GREY).at(x + 8, y + NODE_H - 11, anchor="left_center")
            diag.text(str(day(s.latest_finish)), size=11, color=GREY).at(x + NODE_W - 8, y + NODE_H - 11, anchor="right_center")
            diag.text(f"slack {s.slack}", size=11, color=RED if crit else GREY).at(
                x + NODE_W / 2, y + NODE_H - 11, anchor="center")

        ly = Y0 + 2 * ROW_H + NODE_H + 28
        diag.text("Corners: early start | early finish above, late start | late finish below, in days from project start.",
                  size=11, color="#4B5563").at(X0, ly, anchor="left_center")
        path = " > ".join(sched.critical_path)
        total = (sched.finish - sched.start).days
        diag.caption(
            f"**Figure 11:** PERT network of {len(PLAN)} activities, {total} days. "
            f"Critical path {path} (zero slack); activities off it, such as F, have slack",
            small_caps=True, max_width=900,
        )
    return diag


def build_diagram(output_dir: Path | str = "examples/project_management") -> Path:
    return render_all(diagram(), output_dir, "11_pert_network")["svg"]


if __name__ == "__main__":
    dest = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("examples/project_management")
    build_diagram(dest)
