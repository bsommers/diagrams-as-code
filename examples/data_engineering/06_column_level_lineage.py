"""Column-level lineage from raw tables to a revenue mart (DATA ENGINEERING domain).

Table-level lineage says that fct_daily_revenue depends on raw.orders. Column
lineage says which columns feed which: amount_cents is divided by 100 and
summed into revenue_usd, order_id is counted, ts is truncated to a date, and
customers.country_code reaches the mart only through a join on customer_id.
"""
from __future__ import annotations

import sys
from pathlib import Path

from diagrams_as_code import Diagram, Style
from diagrams_as_code.output import render_all

COL = Style(fill="#FFFFFF", font_size=11)
KEY = Style(fill="#FBEFCB", font_size=11)
OUT = Style(fill="#D5EFD9", font_size=11)
TABLE = Style(fill="#F1F3F8")
CW, CH, PITCH = 220.0, 30.0, 42.0
XS = (50.0, 430.0, 810.0)
LINE = {"routing": "direct", "width": 1.3}


def table(diag: Diagram, name: str, x: float, y: float, cols: list[tuple[str, Style]]) -> dict[str, object]:
    out = {}
    with diag.group(name, padding=14, header_height=30, style=TABLE):
        for i, (label, style) in enumerate(cols):
            out[label.split("\n")[0].split(" ")[0]] = diag.shape(label, CW, CH, style=style, fit_label=False).at(
                x, y + i * PITCH)
    return out


def diagram() -> Diagram:
    with Diagram("Column-Level Lineage", theme="paper") as diag:
        raw_o = table(diag, "raw.orders", XS[0], 110, [
            ("order_id", COL), ("customer_id", KEY), ("amount_cents", COL), ("ts", COL)])
        raw_c = table(diag, "raw.customers", XS[0], 330, [
            ("id", KEY), ("country_code", COL)])
        stg_o = table(diag, "stg_orders", XS[1], 110, [
            ("order_id", COL), ("customer_id", KEY), ("amount_usd = amount_cents / 100", COL),
            ("ordered_at = cast(ts)", COL)])
        stg_c = table(diag, "stg_customers", XS[1], 330, [
            ("customer_id = id", KEY), ("country = upper(country_code)", COL)])
        fct = table(diag, "fct_daily_revenue", XS[2], 110, [
            ("order_count = count(order_id)", OUT), ("country (via join)", OUT),
            ("revenue_usd = sum(amount_usd)", OUT), ("order_date = date(ordered_at)", OUT)])

        r = [raw_o["order_id"], raw_o["customer_id"], raw_o["amount_cents"], raw_o["ts"]]
        s = [stg_o["order_id"], stg_o["customer_id"], stg_o["amount_usd"], stg_o["ordered_at"]]
        for a, b in zip(r, s):
            a.anchor("right", 0.5) >> diag.edge(**LINE) >> b.anchor("left", 0.5)
        raw_c["id"].anchor("right", 0.5) >> diag.edge(**LINE) >> stg_c["customer_id"].anchor("left", 0.5)
        raw_c["country_code"].anchor("right", 0.5) >> diag.edge(**LINE) >> stg_c["country"].anchor("left", 0.5)

        f = [fct["order_count"], fct["country"], fct["revenue_usd"], fct["order_date"]]
        stg_o["order_id"].anchor("right", 0.5) >> diag.edge(**LINE) >> f[0].anchor("left", 0.5)
        stg_c["country"].anchor("right", 0.5) >> diag.edge(**LINE) >> f[1].anchor("left", 0.5)
        stg_o["amount_usd"].anchor("right", 0.5) >> diag.edge(**LINE) >> f[2].anchor("left", 0.5)
        stg_o["ordered_at"].anchor("right", 0.5) >> diag.edge(**LINE) >> f[3].anchor("left", 0.5)

        diag.text(
            "Amber columns are the join key (customer_id = id). The join does not copy customer_id into the mart,\n"
            "but it decides which country each order gets, so it is lineage for country (a filter/join dependency).\n"
            "A change to raw.orders.amount_cents therefore reaches only revenue_usd, not order_count or country.",
            size=12, line_height=1.4,
        ).at(50, 460)
    return diag


def build_diagram(output_dir: Path | str = "examples/data_engineering") -> Path:
    return render_all(diagram(), output_dir, "06_column_level_lineage")["svg"]


if __name__ == "__main__":
    dest = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("examples/data_engineering")
    build_diagram(dest)
