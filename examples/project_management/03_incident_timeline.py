"""A post-incident timeline: a database failover that went wrong, minute by minute.

Events are naive ``datetime`` values on one day; the ruler picks a minute step
whose labels fit. Detection and response events are flagged above the ruler,
customer-facing communication below it. The shaded spans mark the customer
impact and the degraded window. Labels stack so they never overlap, even where
five events land within ten minutes.
"""
from __future__ import annotations

import sys
from datetime import datetime
from pathlib import Path

from diagrams_as_code import Diagram
from diagrams_as_code.gantt import Timeline
from diagrams_as_code.output import render_all


def at(hhmm: str) -> datetime:
    h, m = (int(v) for v in hhmm.split(":"))
    return datetime(2026, 4, 14, h, m)


RESPONSE = [
    ("13:58", "Primary DB disk latency climbs"),
    ("14:02", "**Alert:** p99 latency > 2 s"),
    ("14:04", "On-call engineer paged"),
    ("14:07", "Incident declared, SEV-2"),
    ("14:09", "Automatic failover starts"),
    ("14:12", "Failover stalls: replica lag 40 s"),
    ("14:21", "Writes paused; manual promotion"),
    ("14:34", "Replica promoted to primary"),
    ("14:52", "Error rate back to baseline"),
    ("15:30", "Incident resolved"),
]
COMMS = [
    ("14:10", "Status page: investigating"),
    ("14:25", "Status page: writes paused"),
    ("14:40", "Status page: monitoring"),
    ("15:32", "Status page: resolved"),
]


def diagram() -> Diagram:
    with Diagram("Incident timeline", theme="nord") as diag:
        t = Timeline(diag, width=1000, origin=(40, 40), label_width=160)
        t.span(at("14:02"), at("14:52"), "Customer impact: failed writes", color="#BF616A")
        t.span(at("14:52"), at("15:30"), "Degraded: elevated latency", color="#EBCB8B")
        for hhmm, label in RESPONSE:
            t.event(at(hhmm), f"{hhmm} {label}")
        for hhmm, label in COMMS:
            t.event(at(hhmm), f"{hhmm} {label}", side="below", marker="diamond", color="#A3BE8C")
        t.draw()
        diag.caption(
            "**Figure 3:** Database failover incident, 14 April 2026: time to detect "
            "$t_d = 4$ min, time to mitigate $t_m = 50$ min",
            small_caps=True, max_width=900,
        )
    return diag


def build_diagram(output_dir: Path | str = "examples/project_management") -> Path:
    return render_all(diagram(), output_dir, "03_incident_timeline")["svg"]


if __name__ == "__main__":
    dest = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("examples/project_management")
    build_diagram(dest)
