"""Example architecture: Global Supply Chain RFQ & Sourcing (BUSINESS_PROCESS domain)."""
from __future__ import annotations

import sys
from pathlib import Path

from iiot_diagrams import Diagram, Edge, Group, Shape


def build_diagram(output_dir: Path | str = "output/business_process") -> Path:
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    svg_file = out / "08_supply_chain_rfq_fulfillment.svg"
    png_file = out / "08_supply_chain_rfq_fulfillment.png"
    readme_file = out / "08_supply_chain_rfq_fulfillment_README.md"

    with Diagram("Global Supply Chain RFQ & Sourcing", theme="emerald") as diag:
        with diag.group("Supply Planning") as g_1:
            demand_plan = diag.add(Shape("demand_plan", "Material Demand Forecast", icon="analytics", horizon="Quarterly Plan"))

        with diag.group("Procurement") as g_2:
            rfq_portal = diag.add(Shape("rfq_portal", "Global Supplier RFQ Portal", icon="document", suppliers="Global Tier 1 Vendors"))
            bid_eval = diag.add(Shape("bid_eval", "Multi-Criteria Bid Scoring", icon="decision", criteria="Price, Quality, Lead Time"))
            bid_eval.below(rfq_portal, margin=30)

        with diag.group("Logistics Operations") as g_3:
            freight = diag.add(Shape("freight", "Ocean & Air Freight Booking", icon="router", incoterms="FOB Port of Origin"))
            customs = diag.add(Shape("customs", "Customs Broker Clearance", icon="shield", tariff="Harmonized Code Verified"))
            customs.below(freight, margin=30)

        with diag.group("Warehouse Fulfillment") as g_4:
            dc_intake = diag.add(Shape("dc_intake", "Central Distribution Center", icon="storage_array", pallet="Automated AS/RS Intake"))

        # Arrange groups in horizontal sequence
        g_2.right_of(g_1, margin=50)
        g_3.right_of(g_2, margin=50)
        g_4.right_of(g_3, margin=50)

        # Establish inter-element connections with protocol annotations
        demand_plan >> diag.edge("Trigger Requisition", style="solid") >> rfq_portal
        rfq_portal >> diag.edge("Compile Bids", style="solid") >> bid_eval
        bid_eval >> diag.edge("Award Contract & Ship", style="solid") >> freight
        freight >> diag.edge("Present Bill of Lading", style="solid") >> customs
        customs >> diag.edge("Release Cargo to Racks", style="solid") >> dc_intake

        diag.render_svg(svg_file)
        diag.render_png(png_file)
        diag.generate_readme("08_supply_chain_rfq_fulfillment.svg", readme_file)

    return svg_file


if __name__ == "__main__":
    dest = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("output/business_process")
    build_diagram(dest)
