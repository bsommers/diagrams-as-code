"""Example architecture: ITSM Enterprise Change Advisory Board (CAB) (BUSINESS_PROCESS domain)."""
from __future__ import annotations

import sys
from pathlib import Path

from iiot_diagrams import Diagram, Edge, Group, Shape


def build_diagram(output_dir: Path | str = "output/business_process") -> Path:
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    svg_file = out / "10_enterprise_change_management.svg"
    readme_file = out / "10_enterprise_change_management_README.md"

    with Diagram("ITSM Enterprise Change Advisory Board (CAB)", theme="blueprint") as diag:
        with diag.group("RFC Initiation") as g_1:
            engineer = diag.add(Shape("engineer", "Systems Engineer", icon="user", role="Cloud Platform Lead"))
            rfc_doc = diag.add(Shape("rfc_doc", "Request for Change (RFC)", icon="document", type="Critical Kernel Patch"))
            rfc_doc.below(engineer, margin=30)

        with diag.group("Governance Gates") as g_2:
            risk_calc = diag.add(Shape("risk_calc", "Risk & Impact Matrix", icon="decision", score="Severity High / Low Risk"))
            cab_board = diag.add(Shape("cab_board", "Change Advisory Board (CAB)", icon="user", quorum="Security, Network, Product Leads"))
            cab_board.below(risk_calc, margin=30)

        with diag.group("Execution Phase") as g_3:
            maint_window = diag.add(Shape("maint_window", "Maintenance Window Execution", icon="terminal", schedule="Sunday 02:00 UTC"))

        with diag.group("Verification") as g_4:
            health_verify = diag.add(Shape("health_verify", "Automated Post-Change Health Check", icon="shield", test="Synthetic Smoke Tests"))
            rollback = diag.add(Shape("rollback", "Automated Rollback Safeguard", icon="workflow", trigger="P99 Latency Regression"))
            rollback.below(health_verify, margin=30)

        # Arrange groups in horizontal sequence
        g_2.right_of(g_1, margin=50)
        g_3.right_of(g_2, margin=50)
        g_4.right_of(g_3, margin=50)

        # Establish inter-element connections with protocol annotations
        engineer >> diag.edge("Draft RFC Proposal", style="solid") >> rfc_doc
        rfc_doc >> diag.edge("Calculate Impact Score", style="solid") >> risk_calc
        risk_calc >> diag.edge("Present to CAB Review", style="solid") >> cab_board
        cab_board >> diag.edge("Approve Execution Window", style="solid") >> maint_window
        maint_window >> diag.edge("Run Post-Change Verification", style="solid") >> health_verify
        health_verify >> diag.edge("Abnormal Signals Detected", style="dashed") >> rollback

        diag.render_svg(svg_file)
        diag.generate_readme("10_enterprise_change_management.svg", readme_file)

    return svg_file


if __name__ == "__main__":
    dest = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("output/business_process")
    build_diagram(dest)
