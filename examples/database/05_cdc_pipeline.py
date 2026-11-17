"""Example architecture: Change Data Capture Pipeline from WAL to Kafka (DATABASE domain).

Committed transactions in the source database are written to the
write-ahead log. Debezium reads them through a logical replication slot,
registers each table's Avro schema, and publishes one change event per row
to a Kafka topic per table. Sink connectors fan the stream out to search,
the warehouse, the lake and cache invalidation; records that fail to
convert go to a dead-letter topic.
"""
from __future__ import annotations

import sys
from pathlib import Path

from diagrams_as_code import Diagram, Shape
from diagrams_as_code.output import render_all


def diagram() -> Diagram:
    with Diagram("Change Data Capture Pipeline from WAL to Kafka", theme="dracula") as diag:
        with diag.group("Source OLTP") as g_src:
            app = diag.add(Shape("app", "Checkout Service", icon="server", width=160, lang="Go"))
            db = diag.add(Shape("db", "PostgreSQL 16 Primary", icon="database", width=160, wal_level="logical"))
            wal = diag.add(Shape("wal", "WAL + Replication Slot", icon="document", width=160, plugin="pgoutput"))
            db.below(app, margin=70)
            wal.below(db, margin=70)

        with diag.group("Capture (Kafka Connect)") as g_cap:
            debezium = diag.add(Shape("debezium", "Debezium Source Connector", icon="workflow", width=190,
                                      snapshot="initial, then streaming"))
            registry = diag.add(Shape("registry", "Schema Registry", icon="document", width=190,
                                      compatibility="BACKWARD"))
            registry.below(debezium, margin=70)

        with diag.group("Event Streaming") as g_kafka:
            topic = diag.add(Shape("topic", "orders.public.orders", icon="queue", width=190,
                                   partitions="12, key = order_id"))
            dlq = diag.add(Shape("dlq", "Dead-Letter Topic", icon="queue", width=190, retention="14 d"))
            dlq.below(topic, margin=70)

        with diag.group("Sink Connectors") as g_sink:
            search = diag.add(Shape("search", "Search Index", icon="analytics", width=170, mode="upsert by key"))
            dwh = diag.add(Shape("dwh", "Cloud Warehouse", icon="storage", width=170, load="micro-batch 1 min"))
            lake = diag.add(Shape("lake", "Data Lake (Iceberg)", icon="storage", width=170, format="Parquet"))
            cache = diag.add(Shape("cache", "Cache Invalidator", icon="serverless", width=170, target="Redis"))
            dwh.below(search, margin=40)
            lake.below(dwh, margin=40)
            cache.below(lake, margin=40)

        g_src.at(60.0, 80.0)
        g_cap.at(380.0, 160.0)
        g_kafka.at(720.0, 160.0)
        g_sink.at(1060.0, 80.0)

        app >> diag.edge("INSERT / UPDATE") >> db
        db >> diag.edge("commit") >> wal
        wal >> diag.edge("logical decoding") >> debezium
        debezium >> diag.edge("register schema", style="dashed") >> registry
        debezium >> diag.edge("change events") >> topic
        diag.fan_out(topic, [search, dwh, lake, cache], trunk=50)
        topic.anchor("bottom", 0.5) >> diag.edge("poison records", style="dashed") >> dlq.anchor("top", 0.5)

        diag.text(
            "Event envelope: **before**, **after**, **op** (c/u/d), **source.lsn**, **ts_ms**.\n"
            "The slot holds WAL until Debezium acknowledges the LSN, so lag shows up as disk use on the primary.",
            size=12, line_height=1.4,
        ).at(380.0, 470.0)
    return diag


def build_diagram(output_dir: Path | str = "output/database") -> Path:
    return render_all(diagram(), output_dir, "05_cdc_pipeline")["svg"]


if __name__ == "__main__":
    dest = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("output/database")
    build_diagram(dest)
