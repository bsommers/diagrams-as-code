"""Example architecture: C4 System Context for Retail Banking (ENTERPRISE_ARCHITECTURE domain).

A C4 level-1 view: the people who use the internet banking system and the
other systems it depends on, with the enterprise boundary drawn around what the
bank owns.
"""
from __future__ import annotations

import sys
from pathlib import Path

from diagrams_as_code import Diagram, Port
from diagrams_as_code.output import render_all

W, H = 230.0, 92.0


def diagram() -> Diagram:
    with Diagram("C4 System Context: Retail Internet Banking", theme="pastel_light") as diag:
        customer = diag.shape(
            "**Personal Customer**\n[Person]\nHolds current and savings accounts",
            W, H, icon="user", id="customer", metadata={"c4": "Person", "scope": "External"},
        ).at(380, 40)

        with diag.group("Big Bank plc: Enterprise Boundary", padding=30):
            banking = diag.shape(
                "**Internet Banking System**\n[Software System]\nView balances, make payments",
                W, H, icon="server", id="banking", metadata={"c4": "Software System", "owner": "Digital Channels"},
            ).at(380, 250)
            mainframe = diag.shape(
                "**Core Banking Mainframe**\n[Software System]\nAccounts, ledger, transactions",
                W, H, icon="database", id="mainframe", metadata={"c4": "Software System", "owner": "Core Platforms"},
            ).at(380, 440)
            staff = diag.shape(
                "**Customer Service Staff**\n[Person]\nAnswers customer queries",
                W, H, icon="user", id="staff", metadata={"c4": "Person", "scope": "Internal"},
            ).at(70, 440)

        idp = diag.shape(
            "**Open Banking Directory**\n[External System]\nThird-party provider registry",
            W, H, icon="key", id="idp", metadata={"c4": "External System", "provider": "OBIE"},
        ).at(860, 40)
        email = diag.shape(
            "**E-mail Service**\n[External System]\nTransactional e-mail (SaaS)",
            W, H, icon="message", id="email", metadata={"c4": "External System", "provider": "SendGrid"},
        ).at(860, 250)
        credit = diag.shape(
            "**Credit Bureau**\n[External System]\nCredit scores and checks",
            W, H, icon="analytics", id="credit", metadata={"c4": "External System", "provider": "Experian"},
        ).at(860, 440)

        customer >> diag.edge("views accounts, pays [HTTPS]", source_port=Port.SOUTH, target_port=Port.NORTH) >> banking
        banking >> diag.edge("reads / posts [XML over MQ]", source_port=Port.SOUTH, target_port=Port.NORTH) >> mainframe
        banking.anchor("right", 0.5) >> diag.edge("sends statements [SMTP]") >> email.anchor("left", 0.5)
        banking.anchor("right", 0.2) >> diag.edge("verifies TPPs [mTLS]", style="dashed") >> idp.anchor("bottom", 0.3)
        staff >> diag.edge("uses [3270]") >> mainframe
        mainframe >> diag.edge("checks credit [REST]") >> credit
    return diag


def build_diagram(output_dir: Path | str = "examples/enterprise_architecture") -> Path:
    return render_all(diagram(), output_dir, "01_c4_system_context")["svg"]


if __name__ == "__main__":
    dest = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("examples/enterprise_architecture")
    build_diagram(dest)
