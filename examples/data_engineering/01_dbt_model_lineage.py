"""dbt model lineage DAG across staging, intermediate and mart layers (DATA ENGINEERING domain).

Sources are declared in YAML and read through source(); staging models
rename and cast one source table each; intermediate models join and reshape;
marts are the wide, business-named tables that BI and reverse-ETL read.
ref() calls are what dbt turns into this directed acyclic graph, so the
build order and the blast radius of a change both fall out of it.
"""
from __future__ import annotations

import sys
from pathlib import Path

from diagrams_as_code import Diagram, Style
from diagrams_as_code.output import render_all

SRC = Style(fill="#E8E8EE")
STG = Style(fill="#DCEBFA")
INT = Style(fill="#FBEFCB")
MART = Style(fill="#D5EFD9")
EXPO = Style(fill="#F6D9DD")


def diagram() -> Diagram:
    with Diagram("dbt Model Lineage DAG", theme="paper", layout="auto", direction="LR",
                 rank_gap=70, node_gap=26) as diag:
        s_orders = diag.shape("raw.orders", 150, 46, kind="cylinder", style=SRC)
        s_cust = diag.shape("raw.customers", 150, 46, kind="cylinder", style=SRC)
        s_pay = diag.shape("raw.payments", 150, 46, kind="cylinder", style=SRC)
        s_ses = diag.shape("raw.web_sessions", 150, 46, kind="cylinder", style=SRC)

        stg_orders = diag.shape("stg_orders", 150, 46, style=STG)
        stg_cust = diag.shape("stg_customers", 150, 46, style=STG)
        stg_pay = diag.shape("stg_payments", 150, 46, style=STG)
        stg_ses = diag.shape("stg_sessions", 150, 46, style=STG)

        int_pay = diag.shape("int_order_payments", 170, 46, style=INT)
        int_ses = diag.shape("int_customer_sessions", 170, 46, style=INT)

        fct = diag.shape("fct_orders", 150, 46, style=MART)
        dim = diag.shape("dim_customers", 150, 46, style=MART)
        mrr = diag.shape("fct_daily_revenue", 160, 46, style=MART)

        dash = diag.shape("Revenue dashboard", 160, 46, icon="dashboard", style=EXPO)
        ml = diag.shape("Churn model features", 160, 46, icon="model", style=EXPO)

        s_orders >> diag.edge() >> stg_orders
        s_cust >> diag.edge() >> stg_cust
        s_pay >> diag.edge() >> stg_pay
        s_ses >> diag.edge() >> stg_ses
        stg_orders >> diag.edge() >> int_pay
        stg_pay >> diag.edge() >> int_pay
        stg_ses >> diag.edge() >> int_ses
        stg_cust >> diag.edge() >> int_ses
        int_pay >> diag.edge() >> fct
        stg_cust >> diag.edge() >> dim
        int_ses >> diag.edge() >> dim
        fct >> diag.edge() >> mrr
        mrr >> diag.edge() >> dash
        dim >> diag.edge() >> ml
        fct >> diag.edge() >> ml

        diag.caption(
            "**Legend:** grey = sources, blue = staging (view), amber = intermediate (ephemeral/view), "
            "green = marts (table/incremental), red = exposures.\n"
            "dbt build --select +fct_orders+ runs every upstream and downstream node of one model.",
            small_caps=False,
        )
    return diag


def build_diagram(output_dir: Path | str = "examples/data_engineering") -> Path:
    return render_all(diagram(), output_dir, "01_dbt_model_lineage")["svg"]


if __name__ == "__main__":
    dest = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("examples/data_engineering")
    build_diagram(dest)
