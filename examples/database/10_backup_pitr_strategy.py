"""Example architecture: Backup and Point-in-Time Recovery Strategy (DATABASE domain).

A weekly full and daily differential base backup, plus a continuous archive
of every WAL segment, make it possible to restore the database to any
moment inside the retention window. Backups are encrypted with keys held in
a KMS, locked against deletion, and copied to a second region. A weekly job
proves the backups work by restoring one. The strip at the bottom shows how
a recovery to just before an incident is assembled.
"""
from __future__ import annotations

import sys
from pathlib import Path

from diagrams_as_code import Diagram, Shape, Style
from diagrams_as_code.output import render_all

AXIS_Y, AXIS_X0, AXIS_X1 = 660.0, 120.0, 1180.0
MARK = Style(fill="#38BDF8", radius=6, stroke="#38BDF8")
INCIDENT = Style(fill="#F87171", radius=6, stroke="#F87171")


def diagram() -> Diagram:
    with Diagram("Backup and Point-in-Time Recovery Strategy", theme="cyber_slate") as diag:
        with diag.group("Production  us-east-1") as g_prod:
            primary = diag.add(Shape("primary", "Primary Database", icon="database", width=170, size="2.4 TB"))
            agent = diag.add(Shape("agent", "Backup Agent", icon="server", width=170, tool="pgBackRest"))
            agent.below(primary, margin=80)

        with diag.group("Backup Repository  (object storage)") as g_repo:
            wal = diag.add(Shape("wal", "WAL Archive", icon="storage", width=170, segment="16 MB"))
            base = diag.add(Shape("base", "Base Backups", icon="storage_array", width=170,
                                  schedule="full Sun, diff daily"))
            base.below(wal, margin=80)

        with diag.group("DR Region  us-west-2") as g_dr:
            copy = diag.add(Shape("copy", "Replicated Repository", icon="storage", width=190, lag="< 15 min"))

        with diag.group("Protection") as g_sec:
            kms = diag.add(Shape("kms", "KMS Key", icon="key", width=140, rotation="yearly"))
            lock = diag.add(Shape("lock", "Object Lock", icon="lock", width=140, retention="35 days"))
            lock.right_of(kms, margin=40)

        with diag.group("Recovery") as g_rec:
            restore = diag.add(Shape("restore", "Restore Host", icon="server", width=170, target="recovery_target_time"))
            recovered = diag.add(Shape("recovered", "Recovered Database", icon="database", width=170))
            verify = diag.add(Shape("verify", "Weekly Restore Test", icon="shield_check", width=170))
            recovered.right_of(restore, margin=60)
            verify.below(restore, margin=50)

        with diag.group("Observability") as g_obs:
            monitor = diag.add(Shape("monitor", "Archive Lag Alerts", icon="dashboard", width=170,
                                     alert="WAL lag > 5 min"))

        g_prod.at(60.0, 80.0)
        g_repo.at(420.0, 80.0)
        g_dr.at(800.0, 80.0)
        g_obs.at(60.0, 400.0)
        g_sec.at(390.0, 400.0)
        g_rec.at(800.0, 260.0)

        primary >> diag.edge("archive_command") >> wal
        primary >> diag.edge("backup stream") >> agent
        agent >> diag.edge("zstd + AES-256") >> base
        wal >> diag.edge("replicate", style="dashed") >> copy
        base.anchor("right", 0.25) >> diag.edge("replicate", style="dashed") >> copy.anchor("bottom", 0.5)
        kms.anchor("top", 0.5) >> diag.edge("data keys", style="dotted") >> base.anchor("bottom", 0.25)
        lock.anchor("top", 0.5) >> diag.edge("WORM", style="dotted") >> base.anchor("bottom", 0.75)
        base.anchor("right", 0.75) >> diag.edge("base + WAL") >> restore.anchor("left", 0.5)
        restore >> diag.edge("promote") >> recovered
        verify >> diag.edge("restore + checksums", style="dotted") >> restore
        agent >> diag.edge("backup + WAL lag", style="dotted") >> monitor

        # Timeline strip: what a recovery to 14:31:59 on Thursday is assembled from.
        axis = Style(stroke="#94A3B8", stroke_width=1.5)
        diag.polyline([(AXIS_X0, AXIS_Y), (AXIS_X1, AXIS_Y)], style=axis)
        days = ["Sun", "Mon", "Tue", "Wed", "Thu"]
        step = 220.0
        for i, day in enumerate(days):
            x = AXIS_X0 + i * step
            diag.shape("", 12, 12, style=MARK, fit_label=False).at(x, AXIS_Y, anchor="center")
            kind = "full" if i == 0 else "diff"
            diag.text(f"**{day}** 01:00\n{kind} backup", size=11, align="center").at(
                x, AXIS_Y + 14, anchor="top_center")
        x_thu = AXIS_X0 + 4 * step
        x_inc = x_thu + step * 13.5 / 24      # 14:32 is 13.5 h after the Thursday backup
        diag.shape("", 12, 12, style=INCIDENT, fit_label=False).at(x_inc, AXIS_Y, anchor="center")
        diag.text("**14:32** bad\nmigration", size=11, align="center", color="#F87171").at(
            x_inc, AXIS_Y + 14, anchor="top_center")
        wal_line = Style(stroke="#38BDF8", stroke_width=4)
        diag.polyline([(x_thu + 8, AXIS_Y - 14), (x_inc - 8, AXIS_Y - 14)], style=wal_line)
        diag.text("replay WAL\nto **14:31:59**", size=11, align="center").at(
            (x_thu + x_inc) / 2, AXIS_Y - 22, anchor="bottom_center")
        diag.text(
            "**Recovering from Thursday's incident:** restore Sunday's full backup and Thursday's "
            "differential, then replay archived WAL up to the target time.",
            size=12,
        ).at(AXIS_X0, AXIS_Y - 76)
        diag.text(
            "**RPO** $\\leq$ one WAL segment or 60 s (archive_timeout)    "
            "**RTO** $\\approx$ restore 2.4 TB + replay up to 1 day of WAL",
            size=12, color="#94A3B8",
        ).at(AXIS_X0, AXIS_Y + 64)
    return diag


def build_diagram(output_dir: Path | str = "output/database") -> Path:
    return render_all(diagram(), output_dir, "10_backup_pitr_strategy")["svg"]


if __name__ == "__main__":
    dest = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("output/database")
    build_diagram(dest)
