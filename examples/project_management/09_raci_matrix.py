"""A RACI matrix: who is Responsible, Accountable, Consulted and Informed per task.

Roles run across, tasks down. The script checks the two RACI rules before it
draws anything: every task has exactly one Accountable role and at least one
Responsible role. The rightmost column counts the Consulted and Informed roles
per task, and the footer totals each role's load (R and A), so an overloaded role
shows up as a long row of R. A combined ``A/R`` means one role both owns and does.
"""
from __future__ import annotations

import sys
from pathlib import Path

from diagrams_as_code import Diagram
from diagrams_as_code.output import render_all
from diagrams_as_code.style import Style
from diagrams_as_code.text.metrics import text_width

ROLES = ["Sponsor", "Product mgr", "Tech lead", "Developer", "QA", "Ops"]

# phase -> (task, assignments in ROLES order; "" = no involvement)
PLAN = {
    "Initiate": [
        ("Approve business case", ["A", "R", "C", "", "", "I"]),
        ("Define scope and requirements", ["I", "A/R", "C", "C", "C", ""]),
    ],
    "Build": [
        ("Design architecture", ["", "C", "A/R", "C", "I", "C"]),
        ("Implement features", ["", "I", "A", "R", "C", ""]),
        ("Write and run test plan", ["", "I", "C", "C", "A/R", ""]),
    ],
    "Release": [
        ("Go / no-go decision", ["A", "R", "C", "I", "C", "C"]),
        ("Deploy to production", ["I", "I", "A", "C", "C", "R"]),
        ("Operate and monitor", ["I", "I", "C", "C", "", "A/R"]),
    ],
}
COLOURS = {  # letter -> (fill, ink)
    "R": ("#4F81BD", "#FFFFFF"),
    "A": ("#C0392B", "#FFFFFF"),
    "C": ("#F2D16B", "#4A3B00"),
    "I": ("#D5DAE1", "#3F4753"),
}

ROW_H, COL_W = 34, 92
X0, Y0 = 40, 40


def rect(x0, y0, x1, y1):
    return [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]


def validate() -> None:
    for phase, tasks in PLAN.items():
        for task, cells in tasks:
            assert len(cells) == len(ROLES), task
            letters = [c.replace("/", "") for c in cells]
            accountable = sum("A" in c for c in letters)
            responsible = sum("R" in c for c in letters)
            assert accountable == 1, f"{task}: {accountable} accountable roles"
            assert responsible >= 1, f"{task}: nobody responsible"


def diagram() -> Diagram:
    validate()
    tasks = [(ph, t, c) for ph, items in PLAN.items() for t, c in items]
    label_w = max(text_width(t, 13) for _, t, _ in tasks) + 36
    stat_w = 96
    grid_x = X0 + label_w
    stat_x = grid_x + len(ROLES) * COL_W
    top = Y0 + 44

    with Diagram("RACI matrix", theme="pastel_light") as diag:
        # Header.
        diag.polygon(rect(X0, Y0, stat_x + stat_w, top), style=Style(fill="#2F3B52", stroke="none"), z=-2)
        diag.text("**Task**", size=13, color="#FFFFFF").at(X0 + 12, Y0 + 22, anchor="left_center")
        for j, role in enumerate(ROLES):
            diag.text(f"**{role}**", size=12, color="#FFFFFF").at(grid_x + j * COL_W + COL_W / 2, Y0 + 22, anchor="center")
        diag.text("**C / I count**", size=12, color="#FFFFFF").at(stat_x + stat_w / 2, Y0 + 22, anchor="center")

        r_load = [0] * len(ROLES)
        a_load = [0] * len(ROLES)
        y = top
        last_phase = None
        for ph, task, cells in tasks:
            if ph != last_phase:
                diag.polygon(rect(X0, y, stat_x + stat_w, y + 24), style=Style(fill="#E4E8EF", stroke="none"), z=-2)
                diag.text(f"**{ph}**", size=12, color="#2F3B52").at(X0 + 12, y + 12, anchor="left_center")
                y += 24
                last_phase = ph
            diag.polygon(rect(X0, y, stat_x + stat_w, y + ROW_H), style=Style(fill="none", stroke="#D3D8E0", stroke_width=0.8), z=-3)
            diag.text(task, size=13).at(X0 + 24, y + ROW_H / 2, anchor="left_center")
            for j, cell in enumerate(cells):
                if not cell:
                    continue
                parts = cell.split("/")
                cx = grid_x + j * COL_W + COL_W / 2
                w = 26
                total = len(parts) * w + (len(parts) - 1) * 4
                for k, letter in enumerate(parts):
                    fill, ink = COLOURS[letter]
                    bx = cx - total / 2 + k * (w + 4)
                    diag.polygon(rect(bx, y + 5, bx + w, y + ROW_H - 5),
                                 style=Style(fill=fill, stroke="none"), z=1)
                    diag.text(f"**{letter}**", size=13, color=ink, z=3).at(bx + w / 2, y + ROW_H / 2, anchor="center")
                    if letter == "R":
                        r_load[j] += 1
                    if letter == "A":
                        a_load[j] += 1
            c_n = sum("C" in c for c in cells)
            i_n = sum("I" in c for c in cells)
            diag.text(f"{c_n} C  /  {i_n} I", size=12, color="#4B5563").at(stat_x + stat_w / 2, y + ROW_H / 2, anchor="center")
            y += ROW_H

        # Footer: load per role.
        for label, series, dy in (("Responsible (R)", r_load, 0), ("Accountable (A)", a_load, 26)):
            fy = y + 10 + dy
            diag.text(f"**{label}**", size=12).at(X0 + 12, fy + 11, anchor="left_center")
            for j, n in enumerate(series):
                diag.text(f"**{n}**", size=13, color="#C0392B" if n == max(series) and n > 0 else "#2F3B52").at(
                    grid_x + j * COL_W + COL_W / 2, fy + 11, anchor="center")
        busiest = ROLES[max(range(len(ROLES)), key=lambda j: (r_load[j], -j))]

        ly = y + 10 + 26 + 40
        lx = X0
        for letter, word in (("R", "Responsible: does the work"), ("A", "Accountable: owns the outcome, one per task"),
                             ("C", "Consulted: two-way input"), ("I", "Informed: one-way updates")):
            fill, ink = COLOURS[letter]
            diag.polygon(rect(lx, ly - 9, lx + 22, ly + 9), style=Style(fill=fill, stroke="none"), z=1)
            diag.text(f"**{letter}**", size=12, color=ink, z=3).at(lx + 11, ly, anchor="center")
            diag.text(word, size=11).at(lx + 30, ly, anchor="left_center")
            lx += 30 + text_width(word, 11) + 26

        diag.caption(
            f"**Figure 9:** RACI matrix, {len(tasks)} tasks and {len(ROLES)} roles; each task has exactly one "
            f"Accountable role, and {busiest} carries the most Responsible work ({max(r_load)} tasks)",
            small_caps=True, max_width=900,
        )
    return diag


def build_diagram(output_dir: Path | str = "examples/project_management") -> Path:
    return render_all(diagram(), output_dir, "09_raci_matrix")["svg"]


if __name__ == "__main__":
    dest = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("examples/project_management")
    build_diagram(dest)
