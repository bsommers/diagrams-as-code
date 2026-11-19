"""Example architecture: Enterprise Integration Architecture (ENTERPRISE_ARCHITECTURE domain).

The integration reference architecture of a mid-size enterprise: API
management at the edge, an iPaaS for orchestrated API calls, an event
streaming backbone for change data, and the legacy ESB with managed file
transfer kept for the mainframe and EDI partners.
"""
from __future__ import annotations

import sys
from pathlib import Path

from diagrams_as_code import Diagram, Port
from diagrams_as_code.output import render_all

W, H = 200.0, 72.0
COL = [60.0, 390.0, 720.0, 1050.0]
ROW = [100.0, 230.0, 360.0, 490.0, 620.0]


def node(diag: Diagram, label: str, col: int, row: int, icon: str, **meta: str):
    return diag.shape(label, W, H, icon=icon, metadata=meta).at(COL[col], ROW[row])


def diagram() -> Diagram:
    with Diagram("Enterprise Integration Architecture: API, Event and ESB Patterns", theme="blueprint") as diag:
        with diag.group("Consumers & Partners"):
            web = node(diag, "**Web & Mobile Apps**", 0, 1, "mobile", pattern="API consumer")
            partner = node(diag, "**Partner APIs**\nmarketplaces, brokers", 0, 2, "cloud", pattern="API consumer")
            edi = node(diag, "**EDI Trading Partners**\nX12 / EDIFACT", 0, 4, "document", pattern="File exchange")

        with diag.group("API Management"):
            oauth = node(diag, "**Authorisation Server**\nOAuth 2.0 / OIDC", 1, 0, "key", product="Okta")
            gateway = node(diag, "**API Gateway**\nrate limits, keys", 1, 1, "api_gateway", product="Apigee X")
            mft = node(diag, "**Managed File Transfer**\nSFTP / AS2", 1, 4, "storage", product="GoAnywhere")

        with diag.group("Integration Platform"):
            ipaas = node(diag, "**iPaaS**\nprocess & system APIs", 2, 1, "workflow", product="MuleSoft Anypoint")
            kafka = node(diag, "**Event Streaming**\ndomain topics", 2, 2, "queue", product="Confluent Cloud")
            esb = node(diag, "**Legacy ESB**\ncontainment only", 2, 4, "broker", product="IBM App Connect", lifecycle="Tolerate")

        with diag.group("Systems of Record"):
            crm = node(diag, "**Salesforce CRM**", 3, 1, "cloud", domain="Customer")
            erp = node(diag, "**SAP S/4HANA**", 3, 2, "server", domain="Finance & Supply")
            lake = node(diag, "**Enterprise Data Lake**", 3, 3, "storage", domain="Analytics")
            mainframe = node(diag, "**z/OS Mainframe**\nCICS policy admin", 3, 4, "database", domain="Policy")

        web >> diag.edge("REST / HTTPS") >> gateway
        partner.anchor("right", 0.5) >> diag.edge("REST + mTLS") >> gateway.anchor("bottom", 0.3)
        gateway >> diag.edge("token check", source_port=Port.NORTH, target_port=Port.SOUTH) >> oauth
        gateway >> diag.edge("routes") >> ipaas
        ipaas >> diag.edge("Bulk API") >> crm
        ipaas >> diag.edge("publish", source_port=Port.SOUTH, target_port=Port.NORTH) >> kafka
        erp >> diag.edge("CDC events") >> kafka
        kafka.anchor("bottom", 0.7) >> diag.edge("sink connector") >> lake.anchor("left", 0.5)
        edi >> diag.edge("AS2 / SFTP") >> mft
        mft >> diag.edge("file events") >> esb
        esb >> diag.edge("IBM MQ") >> mainframe
    return diag


def build_diagram(output_dir: Path | str = "examples/enterprise_architecture") -> Path:
    return render_all(diagram(), output_dir, "06_integration_architecture")["svg"]


if __name__ == "__main__":
    dest = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("examples/enterprise_architecture")
    build_diagram(dest)
