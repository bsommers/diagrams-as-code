"""Example architecture: Enterprise Data Governance and Master Data Management (ENTERPRISE_ARCHITECTURE domain).

The operating model and the platform together. The governance organisation
sets the rules; the MDM hub matches customer and product records from the
source systems into golden records, applying the stewards' quality rules;
consumers read the golden records; and the catalogue records lineage and
classification for every published attribute.
"""
from __future__ import annotations

import sys
from pathlib import Path

from diagrams_as_code import Diagram, Port
from diagrams_as_code.output import render_all

W, H = 200.0, 70.0
A, B, C, D = 60.0, 390.0, 700.0, 1030.0


def diagram() -> Diagram:
    with Diagram("Enterprise Data Governance and Master Data Management", theme="emerald") as diag:
        with diag.group("Governance Organisation"):
            cdo = diag.shape("**Chief Data Officer**\naccountable executive", W, H, icon="user",
                             metadata={"raci": "Accountable"}).at(A, 90)
            council = diag.shape("**Data Governance Council**\nmonthly, cross-BU", W, H, icon="user",
                                 metadata={"raci": "Decides"}).at(B, 90)
            stewards = diag.shape("**Domain Data Stewards**\ncustomer, product, supplier", W, H, icon="user",
                                  metadata={"raci": "Responsible"}).at(C, 90)

        with diag.group("Source Systems"):
            sources = [
                diag.shape(f"**{name}**", W, 64.0, icon=icon, metadata={"domain": domain}).at(A, y)
                for name, icon, domain, y in (
                    ("Salesforce CRM", "cloud", "Customer", 270),
                    ("SAP S/4HANA", "server", "Product, Supplier", 370),
                    ("E-commerce Platform", "laptop", "Customer", 470),
                    ("Supplier Portal", "document", "Supplier", 570),
                )
            ]

        with diag.group("MDM Hub (Informatica)"):
            rules = diag.shape("**Data Quality Rules**\n312 active rules", W, H, icon="shield_check",
                               metadata={"component": "DQ engine"}).at(C, 270)
            match = diag.shape("**Match & Merge**\nfuzzy + deterministic", W, H, icon="workflow",
                               metadata={"component": "Matching"}).at(B, 400)
            golden = diag.shape("**Golden Records**\n4.1M parties, 220k SKUs", W, H, kind="cylinder",
                                metadata={"component": "Hub store"}).at(C, 400)
            workbench = diag.shape("**Stewardship Workbench**\nmerge exceptions", W, H, icon="dashboard",
                                   metadata={"component": "Data stewardship UI"}).at(B, 530)

        with diag.group("Consumers"):
            edw = diag.shape("**Enterprise Data Warehouse**", W, H, icon="database",
                             metadata={"access": "CDC"}).at(D, 530)
            apps = diag.shape("**Operational Apps**\nREST lookup", W, H, icon="api_gateway",
                              metadata={"access": "API"}).at(D, 400)

        with diag.group("Metadata & Policy"):
            catalog = diag.shape("**Data Catalogue**\nglossary and lineage", W, H, icon="document",
                                 metadata={"product": "Collibra"}).at(C, 720)
            policy = diag.shape("**Classification & Access**\nPII tags, masking", W, H, icon="lock",
                                metadata={"product": "Immuta"}).at(D, 720)

        cdo >> diag.edge("chairs") >> council
        council >> diag.edge("delegates") >> stewards
        stewards >> diag.edge("define", source_port=Port.SOUTH, target_port=Port.NORTH) >> rules
        diag.fan_in(sources, match, trunk=60.0, label="")
        match >> diag.edge("survivorship") >> golden
        rules >> diag.edge("validate", source_port=Port.SOUTH, target_port=Port.NORTH) >> golden
        match >> diag.edge("exceptions", source_port=Port.SOUTH, target_port=Port.NORTH) >> workbench
        golden >> diag.edge("publish") >> apps
        golden.anchor("right", 0.8) >> diag.edge("CDC") >> edw.anchor("left", 0.5)
        # Right of centre, clear of the title of the group it enters.
        golden.anchor("bottom", 0.8) >> diag.edge("lineage") >> catalog.anchor("top", 0.8)
        catalog >> diag.edge("tags") >> policy
    return diag


def build_diagram(output_dir: Path | str = "examples/enterprise_architecture") -> Path:
    return render_all(diagram(), output_dir, "09_data_governance_mdm")["svg"]


if __name__ == "__main__":
    dest = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("examples/enterprise_architecture")
    build_diagram(dest)
