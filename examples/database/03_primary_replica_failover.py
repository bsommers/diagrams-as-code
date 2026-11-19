"""Example architecture: PostgreSQL Primary/Replica Replication with Automatic Failover (DATABASE domain).

A three-zone cluster: the primary streams WAL synchronously to a standby in a
second zone and asynchronously to a read replica in a third, and the standby
cascades to a disaster-recovery replica in another region. A consensus store
holds the leader lock; when the primary loses it, the synchronous standby is
promoted and the proxy follows the new leader.
"""
from __future__ import annotations

import sys
from pathlib import Path

from diagrams_as_code import Diagram, Shape
from diagrams_as_code.output import render_all


def diagram() -> Diagram:
    with Diagram("PostgreSQL Primary/Replica Replication with Automatic Failover", theme="nord") as diag:
        with diag.group("Application Tier") as g_app:
            app = diag.add(Shape("app", "Order Service", icon="server", width=150, pool="20 conns / pod"))
            reports = diag.add(Shape("reports", "Reporting API", icon="container", width=150, mode="read-only"))
            reports.below(app, margin=40)

        with diag.group("Routing") as g_proxy:
            proxy = diag.add(Shape("proxy", "HAProxy + PgBouncer", icon="load_balancer", width=170,
                                   ports=":5432 rw / :5433 ro"))

        with diag.group("Zone A") as g_a:
            primary = diag.add(Shape("primary", "Primary (leader)", icon="database", width=160,
                                     role="read-write"))
        with diag.group("Zone B") as g_b:
            standby = diag.add(Shape("standby", "Sync Standby", icon="database", width=160,
                                     synchronous_commit="remote_apply"))
        with diag.group("Zone C") as g_c:
            replica = diag.add(Shape("replica", "Async Read Replica", icon="database", width=160,
                                     hot_standby="on"))

        with diag.group("Failover Control") as g_ctl:
            dcs = diag.add(Shape("dcs", "Patroni + etcd Quorum", icon="cluster", width=170,
                                 ttl="30 s leader lock"))
        with diag.group("DR Region") as g_dr:
            dr = diag.add(Shape("dr", "DR Cascading Replica", icon="database", width=170,
                                lag_target="< 60 s"))

        g_ctl.at(745.0, 80.0)
        g_app.at(60.0, 300.0)
        g_proxy.at(330.0, 350.0)
        g_a.at(620.0, 300.0)
        g_b.at(920.0, 300.0)
        g_c.at(620.0, 540.0)
        g_dr.at(920.0, 540.0)

        app >> diag.edge("SQL") >> proxy
        reports >> diag.edge("SQL") >> proxy
        proxy >> diag.edge("writes :5432") >> primary
        proxy >> diag.edge("reads :5433") >> replica
        primary >> diag.edge("WAL sync") >> standby
        primary >> diag.edge("WAL async", style="dashed") >> replica
        standby >> diag.edge("cascade WAL", style="dashed") >> dr
        dcs.anchor("bottom", 0.25) >> diag.edge("leader lock", style="dotted") >> primary.anchor("top", 0.5)
        dcs.anchor("bottom", 0.75) >> diag.edge("promote on lock loss", style="dotted") >> \
            standby.anchor("top", 0.5)
    return diag


def build_diagram(output_dir: Path | str = "examples/database") -> Path:
    return render_all(diagram(), output_dir, "03_primary_replica_failover")["svg"]


if __name__ == "__main__":
    dest = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("examples/database")
    build_diagram(dest)
