"""Entity-relationship model of an online store (DATABASE domain).

Five tables with their column lists. Primary keys are marked **PK** and
foreign keys *FK*; each relationship line joins the foreign-key column to the
key it references and carries its cardinality at both ends (1 and 0..N), the
textual form of crow's-foot notation.
"""
from __future__ import annotations

import sys
from pathlib import Path

from diagrams_as_code import Diagram, Style
from diagrams_as_code.output import render_all

ROW = 18.0      # height of one column row
HEAD = 34.0     # room for the table name at the top of the box
W = 222.0
TABLE = Style(font_size=14)
LINE = {"routing": "orthogonal", "width": 1.3, "head": "none", "arrow_head": False}

# name -> (x, y, columns); columns are (name, type, key)
TABLES = {
    "customers": (60, 90, [
        ("customer_id", "bigint", "PK"), ("email", "varchar(255)", "UQ"),
        ("full_name", "varchar(120)", ""), ("created_at", "timestamptz", ""),
    ]),
    "orders": (400, 72, [
        ("order_id", "bigint", "PK"), ("customer_id", "bigint", "FK"),
        ("status", "order_status", ""), ("placed_at", "timestamptz", ""),
        ("total_cents", "integer", ""),
    ]),
    "order_items": (740, 72, [
        ("order_id", "bigint", "PK FK"), ("line_no", "smallint", "PK"),
        ("product_id", "bigint", "FK"), ("quantity", "integer", ""),
        ("unit_cents", "integer", ""),
    ]),
    "addresses": (60, 330, [
        ("address_id", "bigint", "PK"), ("customer_id", "bigint", "FK"),
        ("line1", "varchar(200)", ""), ("postcode", "varchar(16)", ""),
    ]),
    "products": (740, 330, [
        ("product_id", "bigint", "PK"), ("sku", "varchar(32)", "UQ"),
        ("title", "varchar(200)", ""), ("price_cents", "integer", ""),
    ]),
}


def row_fraction(table: str, column: str) -> float:
    """Where a column's row sits along the side of its table, top to bottom."""
    columns = TABLES[table][2]
    index = [c[0] for c in columns].index(column)
    height = HEAD + ROW * len(columns) + 10
    return (HEAD + ROW * index + ROW / 2 + 4) / height


def diagram() -> Diagram:
    with Diagram("Online Store Entity-Relationship Model", theme="iiot_light") as diag:
        boxes = {}
        for name, (x, y, columns) in TABLES.items():
            height = HEAD + ROW * len(columns) + 10
            box = diag.shape(f"**{name}**", W, height, label_position="top", style=TABLE,
                             fit_label=False, id=f"tbl_{name}").at(x, y)
            keys = "\n".join(f"**{k}**" if k.startswith("PK") else (f"*{k}*" if k else " ")
                             for _, _, k in columns)
            names = "\n".join(c for c, _, _ in columns)
            types = "\n".join(t for _, t, _ in columns)
            style = {"size": 12, "line_height": ROW / 12}
            diag.text(keys, **style).inside(box, "top_left", 10, HEAD)
            diag.text(names, **style).inside(box, "top_left", 56, HEAD)
            diag.text(types, color="#5A6478", **style).inside(box, "top_left", 138, HEAD)
            boxes[name] = box
        cust, orders, items = boxes["customers"], boxes["orders"], boxes["order_items"]
        addr, prod = boxes["addresses"], boxes["products"]

        def card(text: str, x: float, y: float, anchor: str) -> None:
            diag.text(f"**{text}**", size=12, color="#B03A2E").at(x, y, anchor=anchor)

        def note(text: str, x: float, y: float, anchor: str) -> None:
            diag.text(f"*{text}*", size=12, color="#5A6478").at(x, y, anchor=anchor)

        def row_y(table: str, column: str) -> float:
            x, y, columns = TABLES[table]
            return y + (HEAD + ROW * len(columns) + 10) * row_fraction(table, column)

        # customers 1 -- 0..N orders, joined on orders.customer_id
        cust.anchor("right", row_fraction("customers", "customer_id")) >> diag.edge(**LINE) >> \
            orders.anchor("left", row_fraction("orders", "customer_id"))
        y = row_y("orders", "customer_id")
        card("1", 288, y - 3, "bottom_left")
        card("0..N", 394, y - 3, "bottom_right")
        note("places", 341, y + 4, "top_center")

        # orders 1 -- 1..N order_items, joined on order_items.order_id
        orders.anchor("right", row_fraction("orders", "order_id")) >> diag.edge(**LINE) >> \
            items.anchor("left", row_fraction("order_items", "order_id"))
        y = row_y("order_items", "order_id")
        card("1", 628, y - 3, "bottom_left")
        card("1..N", 734, y - 3, "bottom_right")
        note("contains", 681, y + 4, "top_center")

        # products 1 -- 0..N order_items, joined on order_items.product_id
        items.anchor("bottom", 0.5) >> diag.edge(**LINE) >> prod.anchor("top", 0.5)
        bottom = 72 + HEAD + ROW * 5 + 10
        card("0..N", 862, bottom + 6, "top_left")
        card("1", 862, 324, "bottom_left")
        note("sold as", 849, (bottom + 330) / 2, "right_center")

        # customers 1 -- 0..N addresses, joined on addresses.customer_id
        cust.anchor("bottom", 0.5) >> diag.edge(**LINE) >> addr.anchor("top", 0.5)
        bottom = 90 + HEAD + ROW * 4 + 10
        card("1", 182, bottom + 6, "top_left")
        card("0..N", 182, 324, "bottom_left")
        note("ships to", 169, (bottom + 330) / 2, "right_center")

        diag.text(
            "**PK** primary key    *FK* foreign key    *UQ* unique\n"
            "Read each end: one customer places 0..N orders;\n"
            "every order contains at least one item.",
            size=12, color="#5A6478", line_height=1.4,
        ).at(345, 300)
    return diag


def build_diagram(output_dir: Path | str = "output/database") -> Path:
    return render_all(diagram(), output_dir, "01_entity_relationship_model")["svg"]


if __name__ == "__main__":
    dest = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("output/database")
    build_diagram(dest)
