"""Physical query plan for a join-aggregate-top-N query (DATABASE domain).

The optimiser's chosen plan is a tree of operators; rows flow upward from the
scans at the leaves to the result at the root. Each operator shows its
estimated row count and cumulative cost. Operators that must consume their
whole input before emitting a row (hash build, aggregate, sort) are drawn
with a double border: they split the plan into pipelines.
"""
from __future__ import annotations

import sys
from pathlib import Path

from diagrams_as_code import Diagram, Style
from diagrams_as_code.output import render_all

W, H = 236.0, 58.0
CX = 330.0                 # x of the spine of the tree
OP = Style(fill="#FFFFFF", font_size=12)
BLOCKING = Style(fill="#ECECEF", font_size=12, double=3)
SCAN = Style(fill="#DADCE2", font_size=12)
FLOW = {"routing": "direct", "width": 1.2, "head": "triangle", "arrow_size": 0.8}
SMALL = 11.0

SQL = (
    "**SELECT** c.region, **SUM**(o.total_cents)\n"
    "**FROM** customers c\n"
    "**JOIN** orders o **ON** o.customer_id = c.customer_id\n"
    "**WHERE** o.placed_at >= '2026-01-01'\n"
    "**GROUP BY** c.region\n"
    "**ORDER BY** 2 **DESC LIMIT** 10;"
)


def diagram() -> Diagram:
    with Diagram("Physical Query Plan Tree for a Join and Top-N", theme="paper") as diag:
        def op(title: str, detail: str, x: float, y: float, style: Style = OP):
            return diag.shape(f"**{title}**\n{detail}", W, H, style=style).at(x, y, anchor="top_center")

        def rows(text: str, x: float, y: float, anchor: str = "left_center") -> None:
            diag.text(text, size=SMALL, padding=2).at(x, y, anchor=anchor)

        limit = op("Limit", "rows = 10 · cost 4210", CX, 60)
        sort = op("Sort  (top-N heapsort)", "key: sum DESC · cost 4209", CX, 160, BLOCKING)
        agg = op("HashAggregate", "group by c.region · cost 4190", CX, 260, BLOCKING)
        join = op("Hash Join", "o.customer_id = c.customer_id", CX, 360)
        scan_o = op("Index Scan on orders", "idx_orders_placed_at", CX - 150, 480, SCAN)
        build = op("Hash", "build side, 12 MB", CX + 150, 480, BLOCKING)
        scan_c = op("Seq Scan on customers", "50 000 rows, 640 pages", CX + 150, 590, SCAN)

        sort.anchor("top", 0.5) >> diag.edge(**FLOW) >> limit.anchor("bottom", 0.5)
        agg.anchor("top", 0.5) >> diag.edge(**FLOW) >> sort.anchor("bottom", 0.5)
        join.anchor("top", 0.5) >> diag.edge(**FLOW) >> agg.anchor("bottom", 0.5)
        scan_o.anchor("top", 0.5) >> diag.edge(**FLOW) >> join.anchor("bottom", 0.2)
        build.anchor("top", 0.5) >> diag.edge(**FLOW) >> join.anchor("bottom", 0.8)
        scan_c.anchor("top", 0.5) >> diag.edge(**FLOW) >> build.anchor("bottom", 0.5)

        rows("10 rows", CX + 8, 138)
        rows("12 groups", CX + 8, 238)
        rows("$\\approx 1.2 \\times 10^{5}$ rows", CX + 8, 338)
        rows("*probe*  $\\sigma = 0.08$", CX - 126, 440, "right_center")
        rows("*build*", CX + 132, 440)
        rows("$5 \\times 10^{4}$ rows", CX + 150 + 8, 568)

        diag.text("**Query**", size=13).at(640, 60)
        diag.text(SQL, size=12, line_height=1.45).at(640, 84)
        diag.text(
            "**Reading the plan**\n"
            "Rows flow upward, from the leaf scans to the root.\n"
            "Cost is cumulative and in arbitrary units:\n"
            "$C_{\\mathrm{join}} = C_{\\mathrm{build}} + C_{\\mathrm{probe}} + c_{t} \\cdot N_{\\mathrm{out}}$\n"
            "Selectivity $\\sigma$ is the fraction of *orders* that\n"
            "pass the date predicate on the index.",
            size=12, line_height=1.45,
        ).at(640, 250)
        diag.text(
            "Double border: blocking operator. It reads its whole\n"
            "input before emitting a row, so the plan runs as three\n"
            "pipelines: build, probe-and-aggregate, sort-and-limit.",
            size=12, font="serif", italic=True, line_height=1.45,
        ).at(640, 430)
        diag.caption(
            "**Figure 9:** Physical plan chosen by a cost-based optimiser; arrows show the direction rows flow",
            small_caps=True,
        )
    return diag


def build_diagram(output_dir: Path | str = "output/database") -> Path:
    return render_all(diagram(), output_dir, "09_query_plan_tree")["svg"]


if __name__ == "__main__":
    dest = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("output/database")
    build_diagram(dest)
