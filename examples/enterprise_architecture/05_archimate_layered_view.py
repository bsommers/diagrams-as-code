"""Example architecture: ArchiMate Layered View of Claims Handling (ENTERPRISE_ARCHITECTURE domain).

The classic ArchiMate layered view as a paper figure. The business layer holds
the actor, the business service and the process that realises it; the
application layer serves the process steps; the technology layer serves the
applications. Each layer is a band filled with its ArchiMate colour, solid
lines with open heads are serving relations and dashed lines are realisation.
"""
from __future__ import annotations

import sys
from pathlib import Path

from diagrams_as_code import Diagram, Style
from diagrams_as_code.output import render_all

W, H = 150.0, 56.0
X = [80.0 + 180.0 * i for i in range(5)]
Y_BUS, Y_APP, Y_TECH = 100.0, 270.0, 440.0
BAND_W = X[-1] + W - X[0] + 40.0

BUSINESS = Style(fill="#FFFFB5")
APPLICATION = Style(fill="#B5FFFF")
TECHNOLOGY = Style(fill="#C9E7B7")
SERVES = {"head": "open", "width": 1.0}
REALISES = {"head": "triangle", "style": "dashed", "width": 1.0}


def diagram() -> Diagram:
    with Diagram("ArchiMate Layered View: Insurance Claims Handling", theme="paper") as diag:
        with diag.band("Business layer", notes=["Who acts and what", "the customer is offered."],
                       min_width=BAND_W, child_style=BUSINESS):
            customer = diag.shape("*Business actor*\n**Customer**", W, H, metadata={"archimate": "Business Actor"}).at(X[0], Y_BUS)
            service = diag.shape("*Business service*\n**Claim Settlement**", W, H, metadata={"archimate": "Business Service"}).at(X[1], Y_BUS)
            register = diag.shape("*Process step*\n**Register**", W, H, metadata={"archimate": "Business Process"}).at(X[2], Y_BUS)
            assess = diag.shape("*Process step*\n**Assess**", W, H, metadata={"archimate": "Business Process"}).at(X[3], Y_BUS)
            pay = diag.shape("*Process step*\n**Pay**", W, H, metadata={"archimate": "Business Process"}).at(X[4], Y_BUS)

        with diag.band("Application layer", notes=["Software that automates", "each process step."],
                       min_width=BAND_W, child_style=APPLICATION):
            claim_file = diag.shape("*Data object*\n**Claim File**", W, H, metadata={"archimate": "Data Object"}).at(X[0], Y_APP)
            portal = diag.shape("*App component*\n**Customer Portal**", W, H, metadata={"archimate": "Application Component"}).at(X[1], Y_APP)
            claims = diag.shape("*App component*\n**Claims Admin System**", W + 180.0, H, metadata={"archimate": "Application Component"}).at(X[2], Y_APP)
            payments = diag.shape("*App component*\n**Payment Engine**", W, H, metadata={"archimate": "Application Component"}).at(X[4], Y_APP)

        with diag.band("Technology layer", notes=["Platforms the", "applications run on."],
                       min_width=BAND_W, child_style=TECHNOLOGY):
            internet = diag.shape("*Network*\n**Internet / CDN**", W, H, metadata={"archimate": "Communication Network"}).at(X[0], Y_TECH)
            k8s = diag.shape("*Node*\n**Kubernetes Cluster**", W, H, metadata={"archimate": "Node"}).at(X[1], Y_TECH)
            oracle = diag.shape("*System software*\n**Oracle 19c RAC**", W + 180.0, H, metadata={"archimate": "System Software"}).at(X[2], Y_TECH)
            swift = diag.shape("*Node*\n**SWIFT Gateway**", W, H, metadata={"archimate": "Node"}).at(X[4], Y_TECH)

        # Business layer: the actor uses the service, the process realises it.
        customer >> diag.edge(**SERVES) >> service
        register >> diag.edge(**REALISES) >> service
        register >> diag.edge(**SERVES, arrow_size=0.8) >> assess
        assess >> diag.edge(**SERVES, arrow_size=0.8) >> pay

        # Application layer serves the process steps above it.
        # Columns under a band title attach right of centre to stay clear of it.
        portal.anchor("top", 0.85) >> diag.edge(**SERVES) >> service.anchor("bottom", 0.85)
        portal >> diag.edge(head="open", style="dashed", width=1.0, arrow_size=0.8) >> claim_file
        claims.anchor("top", 75.0 / 330.0) >> diag.edge(**SERVES) >> register.anchor("bottom", 0.5)
        claims.anchor("top", 255.0 / 330.0) >> diag.edge(**SERVES) >> assess.anchor("bottom", 0.5)
        payments >> diag.edge(**SERVES) >> pay

        # Technology layer serves the applications.
        k8s.anchor("top", 0.85) >> diag.edge(**SERVES) >> portal.anchor("bottom", 0.85)
        internet >> diag.edge(**SERVES) >> k8s
        oracle >> diag.edge(**SERVES) >> claims
        swift >> diag.edge(**SERVES) >> payments

        diag.caption(
            "**Figure 1:** ArchiMate layered view; open heads serve, dashed lines realise or access",
            small_caps=True,
        )
    return diag


def build_diagram(output_dir: Path | str = "output/enterprise_architecture") -> Path:
    return render_all(diagram(), output_dir, "05_archimate_layered_view")["svg"]


if __name__ == "__main__":
    dest = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("output/enterprise_architecture")
    build_diagram(dest)
