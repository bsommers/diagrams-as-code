"""Example architecture: Lakehouse Medallion Architecture, Bronze to Gold (DATABASE domain).

Raw data lands unchanged in the bronze layer as append-only tables. The
silver layer deduplicates, types and conforms it, enforcing quality
expectations; the gold layer holds business-level aggregates and marts
served to BI, machine learning and reverse ETL. One catalog governs access
and lineage across all three layers, and an orchestrator schedules the jobs.
"""
from __future__ import annotations

import sys
from pathlib import Path

from diagrams_as_code import Diagram, Shape
from diagrams_as_code.output import render_all

TABLE = {"kind": "cylinder", "width": 180, "height": 78}
BOX = {"width": 160, "height": 78}
ROW_GAP = 40


def diagram() -> Diagram:
    with Diagram("Lakehouse Medallion Architecture, Bronze to Gold", theme="emerald") as diag:
        with diag.group("Sources") as g_src:
            iot = diag.add(Shape("iot", "Device Events", icon="sensor", **BOX, rate="40k msg/s"))
            oltp = diag.add(Shape("oltp", "OLTP CDC Feed", icon="database", **BOX, via="Debezium"))
            saas = diag.add(Shape("saas", "CRM SaaS API", icon="cloud", **BOX, cadence="hourly"))

        with diag.group("Ingestion") as g_ing:
            stream = diag.add(Shape("stream", "Streaming Ingest", icon="queue", **BOX, trigger="continuous"))
            cdc = diag.add(Shape("cdc", "CDC Ingest", icon="queue", **BOX, trigger="continuous"))
            batch = diag.add(Shape("batch", "Batch Loader", icon="workflow", **BOX, trigger="hourly"))

        with diag.group("Bronze  (raw, append-only)") as g_bronze:
            b_events = diag.add(Shape("b_events", "bronze.events_raw", **TABLE, format="Delta"))
            b_orders = diag.add(Shape("b_orders", "bronze.orders_cdc", **TABLE, format="Delta"))
            b_crm = diag.add(Shape("b_crm", "bronze.crm_accounts", **TABLE, format="JSON in Delta"))

        with diag.group("Silver  (cleaned, conformed)") as g_silver:
            s_events = diag.add(Shape("s_events", "silver.sessions", **TABLE, dedup="event_id"))
            s_orders = diag.add(Shape("s_orders", "silver.orders", **TABLE, merge="MERGE on order_id"))
            s_customers = diag.add(Shape("s_customers", "silver.customers", **TABLE, scd="type 2"))

        with diag.group("Gold  (business aggregates)") as g_gold:
            g_funnel = diag.add(Shape("g_funnel", "gold.conversion_daily", **TABLE, grain="day x channel"))
            g_revenue = diag.add(Shape("g_revenue", "gold.revenue_mart", **TABLE, grain="order line"))

        with diag.group("Consumers") as g_use:
            bi = diag.add(Shape("bi", "BI Dashboards", icon="dashboard", **BOX, tool="SQL warehouse"))
            ml = diag.add(Shape("ml", "ML Feature Store", icon="brain", **BOX, refresh="daily"))
            retl = diag.add(Shape("retl", "Reverse ETL to CRM", icon="api_gateway", **BOX, sync="15 min"))

        # Three lanes, one per source; every column shares the same rows.
        lanes = [
            (iot, stream, b_events, s_events, g_funnel, bi),
            (oltp, cdc, b_orders, s_orders, g_revenue, ml),
            (saas, batch, b_crm, s_customers, None, retl),
        ]
        for upper, lower in zip(lanes, lanes[1:]):
            for a, b in zip(upper, lower):
                if a is not None and b is not None:
                    b.below(a, margin=ROW_GAP)
        g_revenue.below(g_funnel, margin=ROW_GAP)

        with diag.group("Governance and Operations") as g_gov:
            catalog = diag.add(Shape("catalog", "Unified Catalog + Lineage", icon="shield", width=200,
                                     scope="all layers"))
            quality = diag.add(Shape("quality", "Data Quality Expectations", icon="shield_check", width=200,
                                     on_fail="quarantine row"))
            orch = diag.add(Shape("orch", "Job Orchestrator", icon="workflow", width=200, sla="gold by 06:00"))
            quality.right_of(catalog, margin=60)
            orch.right_of(quality, margin=60)

        g_src.at(60.0, 80.0)
        g_ing.at(330.0, 80.0)
        g_bronze.at(600.0, 80.0)
        g_silver.at(900.0, 80.0)
        g_gold.at(1200.0, 80.0)
        g_use.at(1500.0, 80.0)
        g_gov.at(630.0, 520.0)

        iot >> diag.edge() >> stream
        oltp >> diag.edge() >> cdc
        saas >> diag.edge() >> batch
        stream >> diag.edge("append") >> b_events
        cdc >> diag.edge("append") >> b_orders
        batch >> diag.edge("COPY INTO") >> b_crm
        b_events >> diag.edge("dedup") >> s_events
        b_orders >> diag.edge("MERGE") >> s_orders
        b_crm >> diag.edge("SCD2") >> s_customers
        s_events >> diag.edge("aggregate") >> g_funnel
        s_orders >> diag.edge("aggregate") >> g_revenue
        s_customers.anchor("right", 0.5) >> diag.edge("join") >> g_revenue.anchor("bottom", 0.5)
        g_funnel >> diag.edge() >> bi
        g_revenue >> diag.edge() >> ml
        g_revenue.anchor("right", 0.75) >> diag.edge() >> retl.anchor("left", 0.5)
        quality.anchor("top", 0.5) >> diag.edge("expectations", style="dotted") >> \
            s_customers.anchor("bottom", 0.5)
    return diag


def build_diagram(output_dir: Path | str = "examples/database") -> Path:
    return render_all(diagram(), output_dir, "06_lakehouse_medallion")["svg"]


if __name__ == "__main__":
    dest = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("examples/database")
    build_diagram(dest)
