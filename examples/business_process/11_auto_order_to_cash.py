"""Example architecture: Auto-Laid-Out Order to Cash (BUSINESS_PROCESS domain)."""
from __future__ import annotations

import sys
from pathlib import Path

from diagrams_as_code import Diagram
from diagrams_as_code.output import render_all


def diagram() -> Diagram:
    with Diagram("Auto-Laid-Out Order to Cash", theme="pastel_light", layout="auto") as diag:
        order_received = diag.shape("Order Received")
        credit_check = diag.shape("Credit Check", kind="diamond")
        fulfil_order = diag.shape("Fulfil Order")
        invoice = diag.shape("Invoice")
        payment_received = diag.shape("Payment Received")
        collections = diag.shape("Collections")

        order_received >> diag.edge() >> credit_check
        credit_check >> diag.edge("approved") >> fulfil_order
        credit_check >> diag.edge("rejected") >> collections
        fulfil_order >> diag.edge() >> invoice
        invoice >> diag.edge() >> payment_received
        invoice >> diag.edge("overdue") >> collections

    return diag


def build_diagram(output_dir: Path | str = "output/business_process") -> Path:
    return render_all(diagram(), output_dir, "11_auto_order_to_cash")["svg"]


if __name__ == "__main__":
    dest = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("output/business_process")
    build_diagram(dest)
