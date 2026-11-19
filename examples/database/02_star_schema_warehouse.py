"""Star schema for a retail sales data warehouse (DATABASE domain).

One fact table at the grain of a single sales line sits at the centre. Each
foreign key points out to a denormalised dimension table; additive measures
stay on the fact. Dimension keys are surrogate keys, and the customer
dimension keeps history as a type-2 slowly changing dimension.
"""
from __future__ import annotations

import sys
from pathlib import Path

from diagrams_as_code import Diagram, Style
from diagrams_as_code.output import render_all

ROW, HEAD, W = 18.0, 34.0, 250.0
DIM = Style(font_size=14)
FACT = Style(font_size=15, fill="#FBEFD5", stroke_width=2.0)
LINE = {"width": 1.4, "head": "none", "arrow_head": False}

# name -> (x, y, columns, style); columns are (name, type, key)
TABLES = {
    "dim_date": (60, 60, [
        ("date_key", "int", "PK"), ("calendar_date", "date", ""), ("fiscal_week", "smallint", ""),
        ("fiscal_quarter", "char(6)", ""), ("is_holiday", "boolean", ""),
    ], DIM),
    "dim_product": (820, 60, [
        ("product_key", "int", "PK"), ("sku", "varchar(32)", ""), ("brand", "varchar(60)", ""),
        ("category", "varchar(60)", ""), ("unit_cost", "numeric(10,2)", ""),
    ], DIM),
    "fact_sales": (430, 210, [
        ("date_key", "int", "FK"), ("product_key", "int", "FK"), ("store_key", "int", "FK"),
        ("customer_key", "int", "FK"), ("promotion_key", "int", "FK"),
        ("quantity", "int", "M"), ("net_amount", "numeric(12,2)", "M"),
        ("discount_amount", "numeric(12,2)", "M"), ("gross_margin", "numeric(12,2)", "M"),
    ], FACT),
    "dim_store": (60, 400, [
        ("store_key", "int", "PK"), ("store_code", "char(8)", ""), ("city", "varchar(80)", ""),
        ("region", "varchar(40)", ""), ("square_metres", "int", ""),
    ], DIM),
    "dim_customer": (820, 400, [
        ("customer_key", "int", "PK"), ("customer_id", "bigint", "NK"), ("segment", "varchar(30)", ""),
        ("valid_from", "date", "SCD2"), ("valid_to", "date", "SCD2"),
    ], DIM),
    "dim_promotion": (450, 520, [
        ("promotion_key", "int", "PK"), ("promo_code", "varchar(20)", ""),
        ("channel", "varchar(20)", ""), ("discount_pct", "numeric(5,2)", ""),
    ], DIM),
}


def height(table: str) -> float:
    return HEAD + ROW * len(TABLES[table][2]) + 10


def frac(table: str, column: str) -> float:
    index = [c[0] for c in TABLES[table][2]].index(column)
    return (HEAD + ROW * index + ROW / 2 + 4) / height(table)


def diagram() -> Diagram:
    with Diagram("Retail Sales Star Schema Data Warehouse", theme="solarized_light") as diag:
        boxes = {}
        for name, (x, y, columns, style) in TABLES.items():
            label = f"**{name}**" + (" *fact, grain = sales line*" if name == "fact_sales" else "")
            box = diag.shape(label, W + (40 if name == "fact_sales" else 0), height(name),
                             label_position="top", style=style, fit_label=False, id=f"tbl_{name}").at(x, y)
            text = {"size": 12, "line_height": ROW / 12}
            keys = "\n".join(f"**{k}**" if k == "PK" else (f"*{k}*" if k else " ") for _, _, k in columns)
            diag.text(keys, **text).inside(box, "top_left", 10, HEAD)
            diag.text("\n".join(c for c, _, _ in columns), **text).inside(box, "top_left", 54, HEAD)
            diag.text("\n".join(t for _, t, _ in columns), color="#657B83", **text).inside(
                box, "top_left", 162, HEAD)
            boxes[name] = box
        fact = boxes["fact_sales"]

        boxes["dim_date"].anchor("right", frac("dim_date", "date_key")) >> diag.edge(**LINE) >> \
            fact.anchor("left", frac("fact_sales", "date_key"))
        boxes["dim_store"].anchor("right", frac("dim_store", "store_key")) >> diag.edge(**LINE) >> \
            fact.anchor("left", frac("fact_sales", "store_key"))
        boxes["dim_product"].anchor("left", frac("dim_product", "product_key")) >> diag.edge(**LINE) >> \
            fact.anchor("right", frac("fact_sales", "product_key"))
        boxes["dim_customer"].anchor("left", frac("dim_customer", "customer_key")) >> diag.edge(**LINE) >> \
            fact.anchor("right", frac("fact_sales", "customer_key"))
        fact.anchor("bottom", 0.5) >> diag.edge(**LINE) >> boxes["dim_promotion"].anchor("top", 0.5)

        diag.text(
            "**PK** surrogate key   *FK* foreign key   *M* additive measure\n"
            "*NK* natural key   *SCD2* type-2 history columns",
            size=12, color="#657B83", line_height=1.4,
        ).at(60, 560)
        diag.text(
            "Queries join the fact to the dimensions\n"
            "they filter or group by, then aggregate\n"
            "the measures: **SUM(net_amount)** by\n"
            "region and fiscal quarter.",
            size=12, color="#657B83", line_height=1.4,
        ).at(820, 560)
    return diag


def build_diagram(output_dir: Path | str = "examples/database") -> Path:
    return render_all(diagram(), output_dir, "02_star_schema_warehouse")["svg"]


if __name__ == "__main__":
    dest = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("examples/database")
    build_diagram(dest)
