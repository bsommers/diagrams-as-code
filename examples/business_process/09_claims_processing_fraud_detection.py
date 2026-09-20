"""Example architecture: Insurance Claims Processing & AI Fraud Scoring (BUSINESS_PROCESS domain)."""
from __future__ import annotations

import sys
from pathlib import Path

from iiot_diagrams import Diagram, Edge, Group, Shape


def build_diagram(output_dir: Path | str = "output/business_process") -> Path:
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    svg_file = out / "09_claims_processing_fraud_detection.svg"
    readme_file = out / "09_claims_processing_fraud_detection_README.md"

    with Diagram("Insurance Claims Processing & AI Fraud Scoring", theme="crimson") as diag:
        with diag.group("First Notice of Loss") as g_1:
            claimant = diag.add(Shape("claimant", "Policyholder Claimant", icon="user", type="Auto Accident Claim"))

        with diag.group("Claim Intake") as g_2:
            ocr_docs = diag.add(Shape("ocr_docs", "OCR Document Processing", icon="document", engine="AWS Textract"))

        with diag.group("Risk Analysis") as g_3:
            fraud_ai = diag.add(Shape("fraud_ai", "AI Fraud Probability Scoring", icon="brain", model="XGBoost Anomaly Model"))
            siu_review = diag.add(Shape("siu_review", "Special Investigation Unit (SIU)", icon="shield", action="Manual Forensic Audit"))
            siu_review.below(fraud_ai, margin=30)

        with diag.group("Settlement") as g_4:
            adjuster = diag.add(Shape("adjuster", "Claims Adjuster Settlement", icon="user", authority="Authorized Settlement"))
            payment = diag.add(Shape("payment", "Direct Bank Claim Reimbursement", icon="storage", rail="Instant Push-to-Card"))
            payment.below(adjuster, margin=30)

        # Arrange groups in horizontal sequence
        g_2.right_of(g_1, margin=50)
        g_3.right_of(g_2, margin=50)
        g_4.right_of(g_3, margin=50)

        # Establish inter-element connections with protocol annotations
        claimant >> diag.edge("Upload Police Report & Photos", style="solid") >> ocr_docs
        ocr_docs >> diag.edge("Structured Claim Features", style="solid") >> fraud_ai
        fraud_ai >> diag.edge("High Risk Anomaly Flag (>0.85)", style="dashed") >> siu_review
        fraud_ai >> diag.edge("Normal Risk Clearance (<0.20)", style="solid") >> adjuster
        siu_review >> diag.edge("Cleared Post Investigation", style="dashed") >> adjuster
        adjuster >> diag.edge("Approve Settlement Amount", style="solid") >> payment
        payment >> diag.edge("Disburse Funds", style="solid") >> claimant

        diag.render_svg(svg_file)
        diag.generate_readme("09_claims_processing_fraud_detection.svg", readme_file)

    return svg_file


if __name__ == "__main__":
    dest = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("output/business_process")
    build_diagram(dest)
