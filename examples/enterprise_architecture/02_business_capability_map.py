"""Example architecture: Insurance Business Capability Map Heatmap (ENTERPRISE_ARCHITECTURE domain).

A three-tier capability map: level-1 domains as columns, level-2 capability
groups inside them and level-3 capabilities as boxes, shaded by assessed
maturity. Shared enabling capabilities sit along the bottom and support the
domain above them.
"""
from __future__ import annotations

import sys
from pathlib import Path

from diagrams_as_code import Diagram, Style
from diagrams_as_code.output import render_all

#: Maturity heat: strong, adequate, weak.
HEAT = {
    "strong": Style(fill="#D4EFDA", stroke="#3C8D53"),
    "adequate": Style(fill="#FBEBC4", stroke="#B8860B"),
    "weak": Style(fill="#F6D0CC", stroke="#B03A2E"),
}

#: Level-1 domain -> level-2 group -> [(level-3 capability, maturity)].
CAPABILITIES: dict[str, dict[str, list[tuple[str, str]]]] = {
    "Customer Engagement": {
        "Distribution": [("Broker Mgmt", "strong"), ("Direct Sales", "adequate")],
        "Service": [("Omnichannel\nContact", "weak"), ("Self-Service", "adequate")],
    },
    "Product & Underwriting": {
        "Product Design": [("Product\nConfiguration", "adequate"), ("Rating &\nPricing", "strong")],
        "Underwriting": [("Risk\nAssessment", "strong"), ("Referral Mgmt", "weak")],
    },
    "Policy & Claims": {
        "Policy Admin": [("Issuance", "strong"), ("Endorsements", "adequate")],
        "Claims": [("First Notice\nof Loss", "weak"), ("Settlement", "adequate")],
    },
    "Finance & Risk": {
        "Finance": [("Billing &\nCollections", "adequate"), ("General\nLedger", "strong")],
        "Risk & Compliance": [("Solvency II\nReporting", "weak"), ("Reinsurance", "adequate")],
    },
}

ENABLERS = ("Customer Master Data", "Document Management", "Workflow & Rules", "Enterprise Data Platform")

L3_W, L3_H = 128.0, 50.0
L3_GAP = 16.0
COL_W = 2 * L3_W + L3_GAP + 2 * 22.0 + 2 * 25.0  # two boxes, inner and outer padding
COL_GAP = 40.0
X0, Y0 = 60.0, 80.0


def diagram() -> Diagram:
    with Diagram("Insurance Business Capability Map with Maturity Heatmap", theme="iiot_light") as diag:
        bottoms = []
        for col, (domain, groups) in enumerate(CAPABILITIES.items()):
            x = X0 + 25.0 + 22.0 + col * (COL_W + COL_GAP)
            with diag.group(domain, padding=25):
                y = Y0 + 35.0 + 35.0
                last = None
                for l2, caps in groups.items():
                    with diag.group(l2, padding=22, header_height=32):
                        for i, (cap, heat) in enumerate(caps):
                            last = diag.shape(
                                cap, L3_W, L3_H, style=HEAT[heat],
                                metadata={"level": "L3", "domain": domain, "group": l2, "maturity": heat},
                            ).at(x + i * (L3_W + L3_GAP), y)
                    y += L3_H + 22.0 + 32.0 + 22.0 + 18.0
                bottoms.append(last)

        enabler_y = Y0 + 2 * (L3_H + 22.0 + 32.0 + 22.0 + 18.0) + 35.0 + 35.0 + 60.0
        with diag.group("Shared Enablers", padding=25):
            enablers = []
            for col, name in enumerate(ENABLERS):
                x = X0 + col * (COL_W + COL_GAP) + COL_W / 2 - 115.0
                enablers.append(diag.shape(
                    name, 230.0, 50.0, icon="database" if "Data" in name else "workflow",
                    metadata={"level": "L1", "type": "Enabling"},
                ).at(x, enabler_y))

        for enabler, top in zip(enablers, bottoms):
            # Leave the enabler under the right-hand capability so the line runs straight up.
            frac = (115.0 + (L3_W + L3_GAP) / 2) / 230.0
            enabler.anchor("top", frac) >> diag.edge("supports", style="dashed") >> top.anchor("bottom", 0.5)

        lx = enablers[-1].bounds.right + 25.0 - 14.0 - 3 * 120.0 - 2 * 14.0
        legend_y = enabler_y + 50.0 + 25.0 + 40.0 + 32.0
        with diag.group("Maturity", padding=14, header_height=30):
            for i, (name, style) in enumerate(HEAT.items()):
                diag.shape(name.capitalize(), 120.0, 32.0, style=style,
                           metadata={"legend": "maturity"}).at(lx + i * 134.0, legend_y)
    return diag


def build_diagram(output_dir: Path | str = "examples/enterprise_architecture") -> Path:
    return render_all(diagram(), output_dir, "02_business_capability_map")["svg"]


if __name__ == "__main__":
    dest = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("examples/enterprise_architecture")
    build_diagram(dest)
