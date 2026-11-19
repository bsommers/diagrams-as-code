"""Example architecture: Range-Sharded Document Database Cluster (DATABASE domain).

Applications talk only to stateless query routers. The routers cache the
chunk map held by a three-member config server replica set and send each
query to the shard that owns its key range, or scatter it to every shard
when the filter lacks the shard key. Every shard is itself a three-member
replica set; the balancer migrates chunks between shards to even them out.
"""
from __future__ import annotations

import sys
from pathlib import Path

from diagrams_as_code import Diagram, Shape
from diagrams_as_code.output import render_all

RANGES = ("[MinKey, 3M)", "[3M, 7M)", "[7M, MaxKey)")


def diagram() -> Diagram:
    with Diagram("Range-Sharded Document Database Cluster", theme="blueprint") as diag:
        with diag.group("Applications") as g_app:
            web = diag.add(Shape("web", "Web API Pods", icon="kubernetes", width=150, driver="v6 driver"))
            batch = diag.add(Shape("batch", "Analytics Jobs", icon="workflow", width=150, read_pref="secondary"))
            batch.below(web, margin=60)

        with diag.group("Query Routers") as g_router:
            mongos_a = diag.add(Shape("mongos_a", "mongos A", icon="router", width=140, state="stateless"))
            mongos_b = diag.add(Shape("mongos_b", "mongos B", icon="router", width=140, state="stateless"))
            mongos_b.below(mongos_a, margin=60)

        with diag.group("Config Server Replica Set") as g_cfg:
            cfg = [
                diag.add(Shape(f"cfg{i}", f"cfg-{i}", kind="cylinder", width=90, height=64, role=role))
                for i, role in enumerate(("primary", "secondary", "secondary"), start=1)
            ]
            cfg[1].right_of(cfg[0], margin=30)
            cfg[2].right_of(cfg[1], margin=30)

        shards = []
        groups = []
        for n in range(1, 4):
            with diag.group(f"Shard {n}   user_id {RANGES[n - 1]}") as g_shard:
                primary = diag.add(Shape(f"s{n}p", "Primary", icon="database", width=120, shard=f"rs{n}"))
                sec1 = diag.add(Shape(f"s{n}s1", "Secondary", icon="database", width=120, shard=f"rs{n}"))
                sec2 = diag.add(Shape(f"s{n}s2", "Secondary", icon="database", width=120, shard=f"rs{n}"))
                sec1.right_of(primary, margin=60)
                sec2.right_of(sec1, margin=60)
            shards.append((primary, sec1, sec2))
            groups.append(g_shard)

        g_app.at(60.0, 120.0)
        g_router.at(330.0, 120.0)
        g_cfg.at(330.0, 470.0)
        for n, g in enumerate(groups):
            g.at(720.0, 60.0 + n * 175.0)

        web >> diag.edge("queries") >> mongos_a
        batch >> diag.edge("queries") >> mongos_b

        # Both routers feed one bus that splits to the three shard primaries.
        bus = diag.point(610.0, 335.0, dot=True)
        mongos_a >> diag.edge(arrow_head=False) >> bus
        mongos_b >> diag.edge(arrow_head=False) >> bus
        for n, (primary, sec1, sec2) in enumerate(shards):
            bus >> diag.edge("targeted" if n == 0 else "") >> primary.anchor("left", 0.5)
            primary >> diag.edge("oplog", style="dashed") >> sec1
            sec1 >> diag.edge("oplog", style="dashed") >> sec2

        mongos_b.anchor("bottom", 0.5) >> diag.edge("chunk map", style="dotted") >> cfg[2].anchor("top", 0.5)
        cfg[0] >> diag.edge(style="dashed") >> cfg[1]
        cfg[1] >> diag.edge(style="dashed") >> cfg[2]

        diag.text(
            "**Balancer** (on the config primary) moves chunks of\n"
            "~128 MB between shards when their counts differ;\n"
            "routers refresh the chunk map after each migration.",
            size=12, line_height=1.4,
        ).at(720.0, 600.0)
    return diag


def build_diagram(output_dir: Path | str = "examples/database") -> Path:
    return render_all(diagram(), output_dir, "04_sharded_cluster")["svg"]


if __name__ == "__main__":
    dest = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("examples/database")
    build_diagram(dest)
