"""Example architecture: ISA-95 Functional Hierarchy, Levels 0 to 4 (MANUFACTURING domain).

The ISA-95 (IEC 62264) model splits a plant into five levels, each working on
its own time scale. Level 4 plans the business in months to days; level 3
runs manufacturing operations in shifts to minutes; level 2 supervises in
seconds; level 1 senses and manipulates the process in milliseconds; level 0
is the process itself. Orders flow down the stack and actual production data
flows back up; the level 3 to 4 boundary is the one IEC 62264 standardises
(B2MML messages).
"""
from __future__ import annotations

import sys
from pathlib import Path

from diagrams_as_code import Diagram
from diagrams_as_code.output import render_all

WIDTH = 780.0  # every band the same width
W, H, GAP = 170.0, 60.0, 70.0
LEVELS = [
    ("Level 4: Business Planning & Logistics", "Months, weeks, days",
     [("PLM", "document"), ("Supply Chain Planning", "analytics"), ("ERP", "server")]),
    ("Level 3: Manufacturing Operations Management", "Days, shifts, hours, minutes",
     [("Quality / LIMS", "shield_check"), ("Plant Historian", "historian"), ("MES / Dispatch", "server")]),
    ("Level 2: Monitoring & Supervisory Control", "Hours, minutes, seconds",
     [("Operator HMI", "hmi"), ("Batch Sequencer", "workflow"), ("SCADA", "scada")]),
    ("Level 1: Sensing & Manipulation", "Seconds, milliseconds",
     [("Safety PLC", "shield"), ("DCS Controller", "plc"), ("PLC", "plc")]),
    ("Level 0: Physical Production Process", "Continuous",
     [("Robots", "robot"), ("Drives & Valves", "gateway"), ("Sensors & Actuators", "sensor")]),
]
FLOWS = [
    ("production schedule (B2MML)", "production performance"),
    ("work orders, recipes", "actuals, genealogy"),
    ("setpoints, sequences", "tags, alarms"),
    ("outputs", "I/O signals"),
]


def diagram() -> Diagram:
    with Diagram("ISA-95 Functional Hierarchy, Levels 0 to 4", theme="iiot_light") as diag:
        rows = []
        bands = []
        for title, timescale, items in LEVELS:
            with diag.band(title, notes=[f"*{timescale}*"], min_width=WIDTH, note_width=130) as band:
                shapes = [diag.shape(name, W, H, icon=icon) for name, icon in items]
                for left, right in zip(shapes, shapes[1:]):
                    right.right_of(left, margin=GAP)
            rows.append(shapes)
            bands.append(band)
        rows[0][0].at(90, 110)
        for upper, lower in zip(bands, bands[1:]):
            lower.below(upper, margin=50)

        # Down the right-hand column go orders, and data comes back up beside them,
        # clear of the band titles on the left.
        for (down, up), upper, lower in zip(FLOWS, rows, rows[1:]):
            upper[2].anchor("bottom", 0.25) >> diag.edge(down) >> lower[2].anchor("top", 0.25)
            lower[2].anchor("top", 0.75) >> diag.edge(up) >> upper[2].anchor("bottom", 0.75)

    return diag


def build_diagram(output_dir: Path | str = "output/manufacturing") -> Path:
    return render_all(diagram(), output_dir, "07_isa95_levels")["svg"]


if __name__ == "__main__":
    dest = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("output/manufacturing")
    build_diagram(dest)
