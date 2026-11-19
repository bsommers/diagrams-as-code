"""Example architecture: C4 Container View of Internet Banking (ENTERPRISE_ARCHITECTURE domain).

A C4 level-2 view that opens up the internet banking system: the client
applications, the API gateway, the domain services and their own databases,
and the event bus that feeds notifications and fraud scoring. Systems outside
the boundary are kept to the left and right.
"""
from __future__ import annotations

import sys
from pathlib import Path

from diagrams_as_code import Diagram, Port
from diagrams_as_code.output import render_all

W, H = 210.0, 84.0
C1, C2, C3 = 400.0, 700.0, 1000.0
EXT_L, EXT_R = 60.0, 1320.0
Y_USER, Y_CLIENT, Y_GW, Y_SVC, Y_DATA = 40.0, 220.0, 380.0, 540.0, 710.0


def box(diag: Diagram, title: str, tech: str, desc: str, x: float, y: float, **opts):
    return diag.shape(f"**{title}**\n[{tech}]\n{desc}", W, H, metadata={"c4": tech}, **opts).at(x, y)


def diagram() -> Diagram:
    with Diagram("C4 Container View: Internet Banking System", theme="nord") as diag:
        # Wide enough that its two lines drop straight onto the client apps.
        cx = (C2 + C3 + W) / 2 - 200.0
        customer = diag.shape("**Personal Customer**\n[Person]\nUses web and mobile banking", 400.0, H,
                              icon="user", metadata={"c4": "Person"}).at(cx, Y_USER)

        with diag.group("Internet Banking System [Software System]", padding=32):
            spa = box(diag, "Single-Page App", "Container: React", "Banking UI in browser", C2, Y_CLIENT, icon="laptop")
            mobile = box(diag, "Mobile App", "Container: Swift / Kotlin", "Banking on the phone", C3, Y_CLIENT, icon="mobile")
            gateway = box(diag, "API Gateway", "Container: Kong", "Auth, quotas, routing", C2, Y_GW, icon="api_gateway")
            accounts = box(diag, "Accounts Service", "Container: Java / Spring", "Balances, statements", C1, Y_SVC, icon="container")
            payments = box(diag, "Payments Service", "Container: Go", "Transfers, standing orders", C2, Y_SVC, icon="container")
            bus = box(diag, "Event Bus", "Container: Kafka", "Domain events", C3, Y_SVC, icon="queue")
            accounts_db = diag.shape("**Accounts Cache**\n[PostgreSQL]", W, H, kind="cylinder",
                                     metadata={"c4": "Container: Database"}).at(C1, Y_DATA)
            payments_db = diag.shape("**Payments Ledger**\n[PostgreSQL]", W, H, kind="cylinder",
                                     metadata={"c4": "Container: Database"}).at(C2, Y_DATA)
            notifier = box(diag, "Notification Worker", "Container: Node.js", "Builds e-mails", C3, Y_DATA, icon="serverless")

        mainframe = box(diag, "Core Banking", "External: Mainframe", "System of record", EXT_L, Y_SVC, icon="database")
        fraud = box(diag, "Fraud Scoring", "External: SaaS", "Real-time risk score", EXT_R, Y_SVC, icon="shield_check")
        email = box(diag, "E-mail Service", "External: SaaS", "Sends e-mail", EXT_R, Y_DATA, icon="message")

        customer.anchor("bottom", (C2 + W / 2 - cx) / 400.0) >> diag.edge("HTTPS") >> spa.anchor("top", 0.5)
        customer.anchor("bottom", (C3 + W / 2 - cx) / 400.0) >> diag.edge("HTTPS") >> mobile.anchor("top", 0.5)
        spa >> diag.edge("JSON / HTTPS", source_port=Port.SOUTH, target_port=Port.NORTH) >> gateway
        mobile.anchor("bottom", 0.5) >> diag.edge("JSON / HTTPS") >> gateway.anchor("right", 0.5)
        gateway.anchor("left", 0.5) >> diag.edge("REST") >> accounts.anchor("top", 0.5)
        gateway >> diag.edge("REST", source_port=Port.SOUTH, target_port=Port.NORTH) >> payments
        accounts >> diag.edge("reads / writes", source_port=Port.SOUTH, target_port=Port.NORTH) >> accounts_db
        payments >> diag.edge("reads / writes", source_port=Port.SOUTH, target_port=Port.NORTH) >> payments_db
        accounts >> diag.edge("MQ") >> mainframe
        payments >> diag.edge("publishes") >> bus
        bus >> diag.edge("payment events") >> fraud
        bus >> diag.edge("subscribes", source_port=Port.SOUTH, target_port=Port.NORTH) >> notifier
        notifier >> diag.edge("SMTP") >> email
    return diag


def build_diagram(output_dir: Path | str = "examples/enterprise_architecture") -> Path:
    return render_all(diagram(), output_dir, "04_c4_container_view")["svg"]


if __name__ == "__main__":
    dest = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("examples/enterprise_architecture")
    build_diagram(dest)
