"""Example architecture: Multi-BU Cloud Landing Zone and Operating Model (ENTERPRISE_ARCHITECTURE domain).

An enterprise landing zone after an acquisition. The cloud centre of
excellence sets guardrails, platform engineering vends accounts into the
workloads organisational unit, the security and infrastructure units are
shared by every business unit, and the acquired unit's identity provider is
federated into the corporate directory so one set of permission sets governs
access everywhere.
"""
from __future__ import annotations

import sys
from pathlib import Path

from diagrams_as_code import Diagram, Port
from diagrams_as_code.output import render_all

W, H = 210.0, 70.0
C = [60.0, 390.0, 720.0, 1050.0, 1380.0]
R = [120.0, 295.0, 425.0, 650.0]


def block(diag: Diagram, label: str, col: int, row: int, icon: str, **meta: str):
    return diag.shape(label, W, H, icon=icon, metadata=meta).at(C[col], R[row])


def diagram() -> Diagram:
    with Diagram("Multi-Business-Unit Cloud Landing Zone and Operating Model", theme="cyber_slate") as diag:
        with diag.group("Operating Model"):
            ccoe = block(diag, "**Cloud Centre of Excellence**\npolicy and standards", 0, 0, "user", team="CCoE")
            platform = block(diag, "**Platform Engineering**\nlanding zone as code", 0, 1, "terminal", team="Platform")

        with diag.group("Management Account"):
            tower = block(diag, "**Control Tower**\npreventive guardrails", 1, 0, "shield_check", service="AWS Control Tower")
            vending = block(diag, "**Account Vending**\nAFT pipeline", 1, 1, "workflow", service="Account Factory for Terraform")
            finops = block(diag, "**FinOps & Budgets**\nshowback per BU", 1, 2, "analytics", service="Cost Explorer + CUR")

        with diag.group("Security OU"):
            logs = block(diag, "**Log Archive**\nimmutable, 7 years", 2, 0, "storage", account="log-archive")
            audit = block(diag, "**Security Tooling**\nGuardDuty, Security Hub", 3, 0, "siem", account="audit")

        with diag.group("Workloads OU: Retail and Wholesale BUs"):
            retail = block(diag, "**Retail BU: Prod**\n14 accounts", 2, 1, "vpc", bu="Retail", env="prod")
            block(diag, "**Wholesale BU: Prod**\n6 accounts (acquired)", 3, 1, "vpc", bu="Wholesale", env="prod")
            nonprod = block(diag, "**Retail BU: Non-prod**\n22 accounts", 2, 2, "vpc", bu="Retail", env="non-prod")
            data = block(diag, "**Shared Data Platform**\nlakehouse accounts", 3, 2, "storage", bu="Group Data", env="prod")

        with diag.group("Infrastructure OU"):
            hub = block(diag, "**Network Hub**\nTransit Gateway, egress", 2, 3, "router", account="network")
            block(diag, "**Shared Services**\nDNS, directory, CI runners", 3, 3, "dns", account="shared-services")

        with diag.group("Identity Federation"):
            okta = block(diag, "**Okta (Wholesale BU)**\nacquired directory", 4, 0, "key", idp="Okta")
            entra = block(diag, "**Microsoft Entra ID**\ncorporate directory", 4, 1, "key", idp="Entra ID")
            sso = block(diag, "**IAM Identity Center**\npermission sets", 4, 2, "lock", service="AWS IAM Identity Center")

        with diag.group("On-Premises"):
            dc = block(diag, "**Corporate Data Centre**\nSAP, mainframe", 0, 3, "server_rack", site="Dallas DC1")

        ccoe >> diag.edge("guardrails") >> tower
        ccoe >> diag.edge("standards", source_port=Port.SOUTH, target_port=Port.NORTH) >> platform
        platform >> diag.edge("Terraform") >> vending
        tower >> diag.edge("org trail") >> logs
        logs >> diag.edge("findings") >> audit
        vending >> diag.edge("vends accounts") >> retail
        nonprod >> diag.edge("cost & usage") >> finops
        dc >> diag.edge("Direct Connect 10G") >> hub
        # Right of centre, clear of the Infrastructure OU title.
        hub.anchor("top", 0.75) >> diag.edge("TGW attachments") >> nonprod.anchor("bottom", 0.75)
        okta >> diag.edge("federation", source_port=Port.SOUTH, target_port=Port.NORTH) >> entra
        entra >> diag.edge("SAML + SCIM", source_port=Port.SOUTH, target_port=Port.NORTH) >> sso
        sso >> diag.edge("permission sets") >> data
    return diag


def build_diagram(output_dir: Path | str = "output/enterprise_architecture") -> Path:
    return render_all(diagram(), output_dir, "10_cloud_landing_zone_operating_model")["svg"]


if __name__ == "__main__":
    dest = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("output/enterprise_architecture")
    build_diagram(dest)
