"""An incident timeline on a time axis: detect, respond, mitigate, resolve.

The axis is built by hand: minute offsets from 14:00 UTC become x positions, the
coloured bar is the sequence of response phases, and each event hangs off the bar
on a leader line, alternating above and below on two levels so the labels do not
collide. The four summary metrics are computed from the event times in the script.
"""
from __future__ import annotations

import sys
from pathlib import Path

from diagrams_as_code import Diagram, Style
from diagrams_as_code.output import render_all

X0, PX_PER_MIN = 110.0, 13.2
BAR_Y, BAR_H = 360.0, 40.0
CARD_W, CARD_H = 158.0, 52.0
INK = "#1F2F57"

START = 14 * 60  # 14:00, minutes since midnight


def hhmm(text: str) -> int:
    h, m = text.split(":")
    return int(h) * 60 + int(m) - START


# (time, title, kind)
EVENTS = [
    ("14:02", "Deploy v2.31 reaches 100%", "cause"),
    ("14:07", "5xx rate passes 5%: customer impact begins", "impact"),
    ("14:12", "Burn-rate alert pages on-call", "detect"),
    ("14:15", "On-call acknowledges", "detect"),
    ("14:20", "SEV2 declared, comms lead joins", "respond"),
    ("14:31", "Cause found: bad config in v2.31", "respond"),
    ("14:38", "Rollback to v2.30 started", "respond"),
    ("14:46", "Error rate back under 0.1%", "resolve"),
    ("15:10", "Incident resolved after watch window", "resolve"),
    ("15:25", "Blameless review scheduled", "resolve"),
]
FILL = {"cause": "#F2C7C0", "impact": "#F2C7C0", "detect": "#F6E2A8", "respond": "#BCD3EE", "resolve": "#BFE3C0"}
PHASES = [
    ("14:00", "14:07", "Healthy", "#E4E6EC"),
    ("14:07", "14:12", "Silent", "#E3A9A0"),
    ("14:12", "14:31", "Triage and diagnose", "#EBCB6A"),
    ("14:31", "14:46", "Mitigate", "#8FB3DE"),
    ("14:46", "15:10", "Watch window", "#9FD3A2"),
    ("15:10", "15:30", "Follow-up", "#E4E6EC"),
]


def x_of(t: str) -> float:
    return X0 + hhmm(t) * PX_PER_MIN


def diagram() -> Diagram:
    with Diagram("Incident timeline: checkout 5xx after a bad deploy", theme="paper") as diag:
        # Phase bar.
        for start, end, name, fill in PHASES:
            w = (hhmm(end) - hhmm(start)) * PX_PER_MIN - 1.0
            diag.shape(name if w < 80 else f"{name}\n{start}-{end}", w, BAR_H, fit_label=False,
                       style=Style(fill=fill, stroke=INK, radius=0, shadow=False, font_size=10)).at(
                x_of(start), BAR_Y)
        diag.text("**14:00**", size=11).at(X0, BAR_Y + BAR_H + 8, anchor="top_center")
        diag.text("**15:30**", size=11).at(X0 + 90 * PX_PER_MIN, BAR_Y + BAR_H + 8, anchor="top_center")

        above = [e for i, e in enumerate(EVENTS) if i % 2 == 0]
        below = [e for i, e in enumerate(EVENTS) if i % 2 == 1]
        for side, group in ((-1, above), (1, below)):
            for k, (t, title, kind) in enumerate(group):
                level = k % 2
                x = x_of(t)
                if side < 0:
                    top = BAR_Y - 40 - CARD_H - level * (CARD_H + 22)
                    edge_a, edge_b = (x, top + CARD_H), (x, BAR_Y - 11)
                else:
                    top = BAR_Y + BAR_H + 40 + level * (CARD_H + 22)
                    edge_a, edge_b = (x, BAR_Y + BAR_H + 11), (x, top)
                diag.connect(edge_a, edge_b, routing="direct", arrow_head=False, width=1.1, color="#5A6478")
                diag.shape(f"**{t}** {title}", CARD_W, CARD_H, fit_label=False,
                           style=Style(fill=FILL[kind], stroke=INK, radius=6, shadow=False, font_size=11)).at(
                    min(max(x - CARD_W / 2, 30.0), X0 + 90 * PX_PER_MIN - CARD_W + 40), top)
                dot_y = BAR_Y - 6 if side < 0 else BAR_Y + BAR_H + 6
                diag.shape("", 10, 10, fit_label=False,
                           style=Style(fill=INK, stroke="#FFFFFF", stroke_width=1.5, radius=5, shadow=False)).at(
                    x, dot_y, anchor="center")

        # Metrics derived from the event times.
        impact, alert, ack = hhmm("14:07"), hhmm("14:12"), hhmm("14:15")
        mitigated, resolved = hhmm("14:46"), hhmm("15:10")
        rows = [
            ("Time to detect", f"{alert - impact} min", "impact to alert"),
            ("Time to acknowledge", f"{ack - alert} min", "alert to on-call"),
            ("Time to mitigate", f"{mitigated - impact} min", "impact to rollback done"),
            ("Time to resolve", f"{resolved - impact} min", "impact to closed"),
        ]
        ty, cols = BAR_Y + BAR_H + 40 + 2 * (CARD_H + 22) + 30, (190.0, 90.0, 190.0)
        diag.text("**Response metrics**", size=13).at(X0, ty - 10, anchor="bottom_left")
        for r, row in enumerate(rows):
            for c, text in enumerate(row):
                diag.shape(f"**{text}**" if c == 1 else text, cols[c], 26, fit_label=False,
                           style=Style(fill="#FFFFFF" if r % 2 else "#EEF1F7", stroke="#C9CFDB", radius=0,
                                       shadow=False, font_size=12)).at(X0 + sum(cols[:c]), ty + r * 26)
        diag.caption("**Figure:** One incident from deploy to review; times are UTC, phases are coloured on the axis",
                     small_caps=True)
    return diag


def build_diagram(output_dir: Path | str = "examples/devops") -> Path:
    return render_all(diagram(), output_dir, "09_incident_timeline")["svg"]


if __name__ == "__main__":
    dest = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("examples/devops")
    build_diagram(dest)
