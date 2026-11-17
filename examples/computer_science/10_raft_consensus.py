"""Raft consensus: leader election as a state machine, and log replication on five servers.

The upper panel is the role each server plays. A follower that hears nothing
for an election timeout becomes a candidate, increments its term and asks for
votes; a majority makes it leader, and any message with a higher term sends it
back to follower. The lower panel is the replicated log after the leader of
term 3 has sent some entries: each cell is one entry, labelled with the term in
which it was created. The commit index is computed in the script as the
highest index that a majority stores and whose entry is from the current term.
"""
from __future__ import annotations

import sys
from pathlib import Path

from diagrams_as_code import Diagram, Style
from diagrams_as_code.output import render_all

LOGS = {
    "S1": [1, 1, 1, 2, 3, 3, 3],
    "S2": [1, 1, 1, 2, 3, 3, 3],
    "S3": [1, 1, 1, 2, 3],
    "S4": [1, 1, 1, 2, 3, 3],
    "S5": [1, 1, 1, 2],
}
LEADER, TERM = "S1", 3
TERM_FILL = {1: "#81A1C1", 2: "#A3BE8C", 3: "#EBCB8B"}
INK = "#ECEFF4"
ACCENT = "#88C0D0"
W, H = 150.0, 54.0
ROLE = Style(radius=H / 2, font_size=14)
LEAD = Style(radius=H / 2, font_size=14, double=4)
LINE = {"width": 1.3}
LABEL = {"size": 12, "padding": 2}
CELL_W, CELL_H, LOG_X, LOG_Y, LOG_PITCH = 52.0, 32.0, 290.0, 420.0, 44.0


def commit_index() -> int:
    """Highest N stored by a majority whose entry was written in the current term."""
    majority = len(LOGS) // 2 + 1
    best = 0
    for n in range(1, max(map(len, LOGS.values())) + 1):
        holders = sum(1 for log in LOGS.values() if len(log) >= n)
        if holders >= majority and LOGS[LEADER][n - 1] == TERM:
            best = n
    return best


def diagram() -> Diagram:
    committed = commit_index()
    with Diagram("Raft leader election and log replication", theme="nord") as diag:

        def label(body: str, x: float, y: float, anchor: str = "bottom_center", align: str = "center"):
            return diag.text(body, align=align, **LABEL).at(x, y, anchor=anchor)

        # ---- (a) roles
        with diag.band("(a) Leader election: the role of one server", min_width=900):
            y = 170.0
            follower = diag.shape("**Follower**", W, H, style=ROLE).at(190, y, anchor="center")
            candidate = diag.shape("**Candidate**", W, H, style=ROLE).at(500, y, anchor="center")
            leader = diag.shape("**Leader**", W, H, style=LEAD).at(810, y, anchor="center")
            label("*election timeout*\n$term \\gets term + 1$, vote for self", 345, y - 6)
            label("*votes from a majority*\n$\\geq \\lfloor n/2 \\rfloor + 1 = 3$", 655, y - 6)
            label("*split vote: timeout*\nnew election", 500, y - 80)
            label("*sees current leader or a higher term*", 345, y + 64, "top_center")
            label("*sees a higher term*: step down", 500, y + 104, "top_center")
            label("start", 60, y - 4)
        diag.connect((40, y), follower.anchor("left", 0.5), routing="direct", **LINE)
        follower.anchor("right", 0.5) >> diag.edge(**LINE) >> candidate.anchor("left", 0.5)
        candidate.anchor("right", 0.5) >> diag.edge(**LINE) >> leader.anchor("left", 0.5)
        diag.connect(candidate.anchor("top", 0.3), candidate.anchor("top", 0.7), routing="spline",
                     via=[(475, y - 58), (500, y - 72), (525, y - 58)], **LINE)
        diag.connect(candidate.anchor("bottom", 0.3), follower.anchor("bottom", 0.7), routing="spline",
                     via=[(420, y + 58), (300, y + 58)], **LINE)
        diag.connect(leader.anchor("bottom", 0.5), follower.anchor("bottom", 0.3), routing="spline",
                     via=[(760, y + 98), (500, y + 100), (230, y + 98)], **LINE)

        # ---- (b) logs
        with diag.band("(b) Log replication in term 3", min_width=900):
            boxes = {}
            for row, (name, log) in enumerate(LOGS.items()):
                ry = LOG_Y + row * LOG_PITCH
                tag = f"**{name}** leader" if name == LEADER else name
                boxes[name] = diag.shape(tag, 100, CELL_H, style=Style(font_size=12, double=3 if name == LEADER else 0)).at(
                    LOG_X - 130, ry)
                for i, term in enumerate(log):
                    diag.shape(str(term), CELL_W, CELL_H, fit_label=False,
                               style=Style(fill=TERM_FILL[term], text_color="#2E3440", radius=0, shadow=False,
                                           stroke="#2E3440", font_size=13)).at(LOG_X + i * CELL_W, ry)
            for i in range(max(map(len, LOGS.values()))):
                diag.text(str(i + 1), size=11, color="#D8DEE9").at(LOG_X + (i + 0.5) * CELL_W, LOG_Y - 6,
                                                                    anchor="bottom_center")
            diag.text("log index", size=11, italic=True, color="#D8DEE9").at(LOG_X - 30, LOG_Y - 6,
                                                                              anchor="bottom_right")
            # Commit index: a dashed rule after the last committed entry.
            cx = LOG_X + committed * CELL_W
            bottom = LOG_Y + (len(LOGS) - 1) * LOG_PITCH + CELL_H + 12
            diag.polyline([(cx, LOG_Y - 4), (cx, bottom)], style=Style(stroke=ACCENT, stroke_width=1.6, dash="5,4"),
                          obstacle=False)
            diag.text(f"$\\mathit{{commitIndex}} = {committed}$", size=12, color=ACCENT).at(cx, bottom + 4,
                                                                                           anchor="top_center")
            notes_x = LOG_X + 7 * CELL_W + 36
            diag.text(
                "Entry 6 is on S1, S2 and S4: a majority,\nand from term 3, so it is committed and\n"
                "entries 1-5 with it. Entry 7 is on two\nservers only. S5 lags; the leader retries\n"
                "with a lower *nextIndex* until the logs\nmatch, then sends the missing entries.",
                size=12, font="serif", italic=True,
            ).at(notes_x, LOG_Y)
            legend_y = LOG_Y + 4 * LOG_PITCH - 6
            for k, (term, fill) in enumerate(TERM_FILL.items()):
                diag.shape(f"term {term}", 64, 24, fit_label=False,
                           style=Style(fill=fill, text_color="#2E3440", radius=0, shadow=False, font_size=11)).at(
                    notes_x + k * 74, legend_y)
            label("AppendEntries", LOG_X - 130 - 34, LOG_Y + 2 * LOG_PITCH + CELL_H / 2, "right_center", "right")
        followers = [boxes[n] for n in LOGS if n != LEADER]
        diag.fan_out(boxes[LEADER].anchor("left", 0.5), [f.anchor("left", 0.5) for f in followers], trunk=24,
                     width=1.2, color=ACCENT)

        diag.caption("**Figure 10:** Raft roles and transitions, and a replicated log with its commit index",
                     small_caps=True)
    return diag


def build_diagram(output_dir: Path | str = "output/computer_science") -> Path:
    return render_all(diagram(), output_dir, "10_raft_consensus")["svg"]


if __name__ == "__main__":
    dest = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("output/computer_science")
    build_diagram(dest)
