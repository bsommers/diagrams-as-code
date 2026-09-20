"""Example architecture: Procure-to-Pay (P2P) Sourcing Process (BUSINESS_PROCESS domain)."""
from __future__ import annotations

import sys
from pathlib import Path

from diagrams_as_code import Diagram, Edge, Group, Shape


def build_diagram(output_dir: Path | str = "output/business_process") -> Path:
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    svg_file = out / "04_procure_to_pay.svg"
    png_file = out / "04_procure_to_pay.png"
    readme_file = out / "04_procure_to_pay_README.md"

    with Diagram("Procure-to-Pay (P2P) Sourcing Process", theme="iiot_dark_gold") as diag:
        with diag.group("Requisition") as g_1:
            requester = diag.add(Shape("requester", "Internal Department Lead", icon="user", dept="Engineering"))

        with diag.group("Approval Gates") as g_2:
            req_approval = diag.add(Shape("req_approval", "Manager Spend Approval", icon="decision", threshold="Under $50k Budget"))

        with diag.group("Procurement") as g_3:
            po_dispatch = diag.add(Shape("po_dispatch", "ERP Purchase Order (PO)", icon="document", system="SAP S/4HANA"))

        with diag.group("Vendor Domain") as g_4:
            vendor = diag.add(Shape("vendor", "Approved Enterprise Vendor", icon="user", terms="Net 45"))

        with diag.group("Accounting") as g_5:
            match_3way = diag.add(Shape("match_3way", "3-Way Match Verification", icon="shield", match="PO vs Receipt vs Invoice"))
            ap_disburse = diag.add(Shape("ap_disburse", "Accounts Payable Payment", icon="storage", method="Automated ACH Transfer"))
            ap_disburse.below(match_3way, margin=30)

        # Position starting group
        g_1.at(60.0, 80.0)

        # Arrange groups in horizontal sequence
        g_2.right_of(g_1, margin=50)
        g_3.right_of(g_2, margin=50)
        g_4.right_of(g_3, margin=50)
        g_5.right_of(g_4, margin=50)

        # Establish inter-element connections with protocol annotations
        requester >> diag.edge("Submit Requisition", style="solid") >> req_approval
        req_approval >> diag.edge("Authorize Spend", style="solid") >> po_dispatch
        po_dispatch >> diag.edge("Transmit PO", style="solid") >> vendor
        vendor >> diag.edge("Deliver Goods & Invoice", style="solid") >> match_3way
        match_3way >> diag.edge("Approve Payment", style="solid") >> ap_disburse

    # Render outputs after diagram context resolves layout constraints
    diag.render_svg(svg_file)
    diag.render_png(png_file)
    diag.generate_readme("04_procure_to_pay.svg", readme_file)

    return svg_file


if __name__ == "__main__":
    dest = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("output/business_process")
    build_diagram(dest)
