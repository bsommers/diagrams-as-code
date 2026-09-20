"""Example architecture: Continuous SOC2 & ISO 27001 Audit Process (BUSINESS_PROCESS domain)."""
from __future__ import annotations

import sys
from pathlib import Path

from iiot_diagrams import Diagram, Edge, Group, Shape


def build_diagram(output_dir: Path | str = "output/business_process") -> Path:
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    svg_file = out / "05_regulatory_compliance_audit.svg"
    readme_file = out / "05_regulatory_compliance_audit_README.md"

    with Diagram("Continuous SOC2 & ISO 27001 Audit Process", theme="blueprint") as diag:
        with diag.group("Audit Boundary") as g_1:
            cloud_env = diag.add(Shape("cloud_env", "AWS / Azure Infrastructure", icon="cloud", accounts="12 Production Accounts"))

        with diag.group("Evidence Engine") as g_2:
            evidence_bot = diag.add(Shape("evidence_bot", "Automated Evidence Collector", icon="agent", engine="Vanta / Drata"))

        with diag.group("Compliance Matrix") as g_3:
            sec_controls = diag.add(Shape("sec_controls", "Access & Encryption Controls", icon="shield", framework="SOC 2 Type II"))

        with diag.group("Audit Team") as g_4:
            auditor = diag.add(Shape("auditor", "Independent External Auditor", icon="user", firm="Big 4 Accounting Firm"))
            remediation = diag.add(Shape("remediation", "Engineering Remediation Task", icon="workflow", ticket="Jira Security Task"))
            remediation.below(auditor, margin=30)

        with diag.group("Final Deliverable") as g_5:
            attestation = diag.add(Shape("attestation", "Formal Attestation Report", icon="document", validity="12 Months"))

        # Arrange groups in horizontal sequence
        g_2.right_of(g_1, margin=50)
        g_3.right_of(g_2, margin=50)
        g_4.right_of(g_3, margin=50)
        g_5.right_of(g_4, margin=50)

        # Establish inter-element connections with protocol annotations
        cloud_env >> diag.edge("Read API Configs", style="solid") >> evidence_bot
        evidence_bot >> diag.edge("Evaluate Pass/Fail", style="solid") >> sec_controls
        sec_controls >> diag.edge("Present Evidence Log", style="solid") >> auditor
        sec_controls >> diag.edge("Flag Deviation", style="dashed") >> remediation
        auditor >> diag.edge("Issue Clean Opinion", style="solid") >> attestation

        diag.render_svg(svg_file)
        diag.generate_readme("05_regulatory_compliance_audit.svg", readme_file)

    return svg_file


if __name__ == "__main__":
    dest = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("output/business_process")
    build_diagram(dest)
