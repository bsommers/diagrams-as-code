"""Example architecture: Home Loan Value Stream to Capability Cross-Map (ENTERPRISE_ARCHITECTURE domain).

A value stream drawn as chevrons from the triggering stakeholder to the value
they receive. Under each stage are the level-2 capabilities that enable it;
the bars below span the stages a cross-cutting capability serves. Capabilities
the bank lacks today are drawn with a dashed outline.
"""
from __future__ import annotations

import sys
from pathlib import Path

from diagrams_as_code import Diagram, Style
from diagrams_as_code.output import render_all

STAGES = ("Explore Options", "Apply", "Assess & Approve", "Settle", "Service Loan")
CAPS: tuple[tuple[tuple[str, bool], ...], ...] = (
    (("Product Comparison", False), ("Affordability Calculator", False), ("Broker Channel Mgmt", False)),
    (("Digital Application", False), ("Identity Verification", True), ("Consent Management", True)),
    (("Credit Decisioning", False), ("Property Valuation", False), ("Exception Underwriting", False)),
    (("Settlement Booking", False), ("Funds Disbursement", False), ("Title Registration", True)),
    (("Repayment Collection", False), ("Hardship Support", False), ("Refinance Retention", True)),
)
SPANS = (
    ("Customer Information Management", 0, 4, 0),
    ("Document & Evidence Management", 1, 2, 1),
    ("Collateral Management", 3, 4, 1),
)

CHEV_W, CHEV_H, NOTCH = 240.0, 70.0, 24.0
PITCH = CHEV_W - NOTCH + 8.0
X0, Y0 = 300.0, 60.0
CAP_W, CAP_H, CAP_GAP = 184.0, 46.0, 18.0
CAP_Y = Y0 + CHEV_H + 60.0
SPAN_Y = CAP_Y + 3 * (CAP_H + CAP_GAP) + 40.0

GAP_STYLE = Style(dash="5,3", fill="#FFFFFF")
HAVE_STYLE = Style(fill="#E6E6E6")


def chevron(x: float, first: bool) -> list[tuple[float, float]]:
    pts = [(x, Y0), (x + CHEV_W - NOTCH, Y0), (x + CHEV_W, Y0 + CHEV_H / 2),
           (x + CHEV_W - NOTCH, Y0 + CHEV_H), (x, Y0 + CHEV_H)]
    if not first:
        pts.append((x + NOTCH, Y0 + CHEV_H / 2))
    return pts


def column_centre(i: int) -> float:
    return X0 + i * PITCH + (CHEV_W + (NOTCH if i else 0.0)) / 2


def diagram() -> Diagram:
    with Diagram("Value Stream to Capability Cross-Map: Acquire a Home Loan", theme="monochrome") as diag:
        buyer = diag.shape("**Home Buyer**\ntriggering stakeholder", 160.0, CHEV_H, icon="user",
                           metadata={"role": "Triggering stakeholder"}).at(40.0, Y0)
        for i, stage in enumerate(STAGES):
            diag.polygon(chevron(X0 + i * PITCH, i == 0), f"**{i + 1}. {stage}**",
                         style=Style(fill="#CFCFCF", stroke_width=1.2))
        end_x = X0 + (len(STAGES) - 1) * PITCH + CHEV_W + 100.0
        value = diag.shape("**Home owned**\nvalue proposition", 170.0, CHEV_H, icon="key",
                           metadata={"role": "Value item"}).at(end_x, Y0)

        diag.text("**Enabling**\n**capabilities**\n*(level 2)*", size=13).at(40.0, CAP_Y)
        tops = []
        for i, column in enumerate(CAPS):
            x = column_centre(i) - CAP_W / 2
            for row, (name, gap) in enumerate(column):
                cap = diag.shape(
                    name, CAP_W, CAP_H, style=GAP_STYLE if gap else HAVE_STYLE,
                    metadata={"stage": STAGES[i], "status": "Gap" if gap else "In place"},
                ).at(x, CAP_Y + row * (CAP_H + CAP_GAP))
                if row == 0:
                    tops.append(cap)

        diag.text("**Cross-stage**\n**capabilities**", size=13).at(40.0, SPAN_Y)
        for name, first, last, row in SPANS:
            left = column_centre(first) - CAP_W / 2
            right = column_centre(last) + CAP_W / 2
            diag.shape(name, right - left, CAP_H, style=HAVE_STYLE,
                       metadata={"stages": f"{first + 1}-{last + 1}", "status": "In place"}).at(
                left, SPAN_Y + row * (CAP_H + CAP_GAP))

        diag.connect(buyer, (X0, Y0 + CHEV_H / 2), label="triggers", routing="direct", head="open")
        last_tip = X0 + (len(STAGES) - 1) * PITCH + CHEV_W
        diag.connect((last_tip, Y0 + CHEV_H / 2), value, label="delivers", routing="direct", head="open")
        for i, cap in enumerate(tops):
            diag.connect((column_centre(i), Y0 + CHEV_H), cap, routing="direct", style="dashed",
                         width=0.9, head="open", arrow_size=0.8)

        diag.text("**Legend**", size=13).at(end_x, CAP_Y)
        diag.shape("In place", 130.0, 34.0, style=HAVE_STYLE, metadata={"legend": "status"}).at(end_x, CAP_Y + 34.0)
        diag.shape("Gap (to build)", 130.0, 34.0, style=GAP_STYLE, metadata={"legend": "status"}).at(end_x, CAP_Y + 84.0)
    return diag


def build_diagram(output_dir: Path | str = "output/enterprise_architecture") -> Path:
    return render_all(diagram(), output_dir, "07_value_stream_capability_map")["svg"]


if __name__ == "__main__":
    dest = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("output/enterprise_architecture")
    build_diagram(dest)
