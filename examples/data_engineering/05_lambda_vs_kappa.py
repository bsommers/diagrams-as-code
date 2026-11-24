"""Lambda versus Kappa architecture (DATA ENGINEERING domain).

Lambda keeps two code paths: a batch layer recomputes views from an immutable
master dataset and a speed layer covers the recent gap; the serving layer
merges both at query time. Kappa keeps one path: a long-retention log is the
system of record, one stream job maintains the view, and a fix or new logic
is deployed as a second job that replays the log into a new table.
"""
from __future__ import annotations

import sys
from pathlib import Path

from diagrams_as_code import Diagram, Style
from diagrams_as_code.output import render_all

BATCH = Style(fill="#DCEBFA", font_size=12)
SPEED = Style(fill="#FBEFCB", font_size=12)
SERVE = Style(fill="#D5EFD9", font_size=12)
NEUTRAL = Style(fill="#FFFFFF", font_size=12)
ARROW = {"routing": "orthogonal", "width": 1.4}
W, H = 170.0, 54.0


def diagram() -> Diagram:
    with Diagram("Lambda versus Kappa Architecture", theme="paper") as diag:
        with diag.band("Lambda: batch layer + speed layer", notes=["Two codebases must", "agree on the logic."],
                       min_width=900):
            src = diag.shape("Event sources", W, H, icon="server").at(60, 100)
            master = diag.shape("**Master dataset**\nimmutable, object store", W, H, style=BATCH).at(290, 90)
            batch = diag.shape("**Batch views**\nSpark, recomputed nightly", W, H, style=BATCH).at(520, 90)
            fast = diag.shape("**Speed layer**\nFlink, incremental", W, H, style=SPEED).at(290, 190)
            rt = diag.shape("**Realtime views**\nlast few hours only", W, H, style=SPEED).at(520, 190)
            serve = diag.shape("**Serving layer**\nmerge batch + realtime", W, H, style=SERVE).at(760, 140)
            q1 = diag.shape("Queries", 100, H, icon="dashboard").at(990, 140)
            diag.fan_out(src, [master, fast], trunk=40, **ARROW)
            master >> diag.edge("batch", **ARROW) >> batch
            fast >> diag.edge("stream", **ARROW) >> rt
            diag.fan_in([batch, rt], serve, trunk=40, **ARROW)
            serve >> diag.edge(**ARROW) >> q1

        with diag.band("Kappa: one log, one stream job", notes=["Reprocess by replaying", "the log, not a batch job."],
                       min_width=900):
            src2 = diag.shape("Event sources", W, H, icon="server").at(60, 380)
            log = diag.shape("**Kafka log**\nretained or tiered", W, H, style=BATCH).at(290, 380)
            v1 = diag.shape("**Stream job v1**\nserving traffic", W, H, style=SPEED).at(520, 340)
            v2 = diag.shape("**Stream job v2**\nreplay from offset 0", W, H, style=SPEED, dash="5,3").at(520, 420)
            t1 = diag.shape("Table v1", 110, H, kind="cylinder", style=SERVE).at(780, 340)
            t2 = diag.shape("Table v2", 110, H, kind="cylinder", style=SERVE).at(780, 420)
            q2 = diag.shape("Queries", 100, H, icon="dashboard").at(990, 380)
            src2 >> diag.edge(**ARROW) >> log
            diag.fan_out(log, [v1, v2], trunk=40, **ARROW)
            v1 >> diag.edge(**ARROW) >> t1
            v2 >> diag.edge(**ARROW) >> t2
            t1 >> diag.edge(**ARROW) >> q2
            t2 >> diag.edge("swap when caught up", style="dashed", **ARROW) >> q2
    return diag


def build_diagram(output_dir: Path | str = "examples/data_engineering") -> Path:
    return render_all(diagram(), output_dir, "05_lambda_vs_kappa")["svg"]


if __name__ == "__main__":
    dest = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("examples/data_engineering")
    build_diagram(dest)
