"""Example architecture: Order-to-Cash (O2C) Business Process (BUSINESS_PROCESS domain)."""
from __future__ import annotations

import sys
from pathlib import Path

from iiot_diagrams import Diagram, Edge, Group, Shape


def build_diagram(output_dir: Path | str = "output/business_process") -> Path:
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    svg_file = out / "01_order_to_cash.svg"
    png_file = out / "01_order_to_cash.png"
    readme_file = out / "01_order_to_cash_README.md"

    with Diagram("Order-to-Cash (O2C) Business Process", theme="emerald") as diag:
        with diag.group("Customer Realm") as g_1:
            customer = diag.add(Shape("customer", "Purchasing Customer", icon="user", channel="B2B Ecommerce"))

        with diag.group("Sales Processing") as g_2:
            order_entry = diag.add(Shape("order_entry", "Order Intake & Validation", icon="document", validation="SKU Availability"))

        with diag.group("Finance & Risk") as g_3:
            credit_check = diag.add(Shape("credit_check", "Credit Limit Approval", icon="decision", rule="Automated Scorecard"))
            invoice = diag.add(Shape("invoice", "ERP Accounts Receivable", icon="document", terms="Net 30 Invoicing"))
            invoice.below(credit_check, margin=30)

        with diag.group("Fulfillment") as g_4:
            warehouse = diag.add(Shape("warehouse", "Warehouse Pick & Pack", icon="workflow", wms="Robotic Automated Storage"))
            shipping = diag.add(Shape("shipping", "Freight Logistics Carrier", icon="router", tracking="EDI 214 Carrier Status"))
            shipping.below(warehouse, margin=30)

        # Arrange groups in horizontal sequence
        g_2.right_of(g_1, margin=50)
        g_3.right_of(g_2, margin=50)
        g_4.right_of(g_3, margin=50)

        # Establish inter-element connections with protocol annotations
        customer >> diag.edge("Submit Purchase Order", style="solid") >> order_entry
        order_entry >> diag.edge("Credit Request", style="solid") >> credit_check
        credit_check >> diag.edge("Release Order", style="solid") >> warehouse
        warehouse >> diag.edge("Dispatch Cargo", style="solid") >> shipping
        shipping >> diag.edge("Proof of Delivery", style="solid") >> invoice
        invoice >> diag.edge("Send Invoice", style="dashed") >> customer

        diag.render_svg(svg_file)
        diag.render_png(png_file)
        diag.generate_readme("01_order_to_cash.svg", readme_file)

    return svg_file


if __name__ == "__main__":
    dest = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("output/business_process")
    build_diagram(dest)
