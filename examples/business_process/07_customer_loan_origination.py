"""Example architecture: Digital Consumer Loan Origination (BUSINESS_PROCESS domain)."""
from __future__ import annotations

import sys
from pathlib import Path

from iiot_diagrams import Diagram, Edge, Group, Shape


def build_diagram(output_dir: Path | str = "output/business_process") -> Path:
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    svg_file = out / "07_customer_loan_origination.svg"
    readme_file = out / "07_customer_loan_origination_README.md"

    with Diagram("Digital Consumer Loan Origination", theme="monochrome") as diag:
        with diag.group("Customer Portal") as g_1:
            applicant = diag.add(Shape("applicant", "Loan Applicant", icon="user", credit="Consumer Retail"))

        with diag.group("Underwriting Core") as g_2:
            kyc_aml = diag.add(Shape("kyc_aml", "Identity Verification (KYC)", icon="shield", api="Socure / Persona"))
            credit_score = diag.add(Shape("credit_score", "Credit Bureau Pull", icon="analytics", bureau="FICO 8 Pull"))
            credit_score.below(kyc_aml, margin=30)
            rule_engine = diag.add(Shape("rule_engine", "Automated Decision Engine", icon="decision", dti="Max 40% Debt-to-Income"))
            rule_engine.below(credit_score, margin=30)

        with diag.group("Contract Stage") as g_3:
            esign = diag.add(Shape("esign", "DocuSign Digital Promissory Note", icon="document", signature="Cryptographic E-Sign"))

        with diag.group("Disbursement") as g_4:
            ach_wire = diag.add(Shape("ach_wire", "Core Banking ACH Disbursement", icon="storage", rail="Same-Day ACH"))

        # Arrange groups in horizontal sequence
        g_2.right_of(g_1, margin=50)
        g_3.right_of(g_2, margin=50)
        g_4.right_of(g_3, margin=50)

        # Establish inter-element connections with protocol annotations
        applicant >> diag.edge("Submit Application", style="solid") >> kyc_aml
        kyc_aml >> diag.edge("Verify Identity", style="solid") >> credit_score
        credit_score >> diag.edge("Feed Credit Data", style="solid") >> rule_engine
        rule_engine >> diag.edge("Generate Approved Terms", style="solid") >> esign
        esign >> diag.edge("Executed Signature", style="solid") >> ach_wire
        ach_wire >> diag.edge("Fund Account", style="dashed") >> applicant

        diag.render_svg(svg_file)
        diag.generate_readme("07_customer_loan_origination.svg", readme_file)

    return svg_file


if __name__ == "__main__":
    dest = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("output/business_process")
    build_diagram(dest)
