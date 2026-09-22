"""Example architecture: Zero Trust Network Access (ZTNA) Architecture (CYBERSECURITY domain)."""
from __future__ import annotations

import sys
from pathlib import Path

from diagrams_as_code import Diagram, Edge, Group, Shape
from diagrams_as_code.output import render_all


def diagram() -> Diagram:
    with Diagram("Zero Trust Network Access (ZTNA) Architecture", theme="high_contrast") as diag:
        with diag.group("Endpoint Tier") as g_1:
            employee = diag.add(Shape("employee", "Remote Employee", icon="user", auth="MFA Challenge"))
            device = diag.add(Shape("device", "Managed Laptop", icon="laptop", posture="EDR Healthy"))
            device.below(employee, margin=30)

        with diag.group("Control Plane") as g_2:
            idp = diag.add(Shape("idp", "Enterprise IdP", icon="key", protocol="OIDC / FIDO2"))
            ztna_broker = diag.add(Shape("ztna_broker", "ZTNA Policy Broker", icon="shield_check", eval="Continuous Trust"))
            ztna_broker.below(idp, margin=30)

        with diag.group("Application Enclave") as g_3:
            app_gw = diag.add(Shape("app_gw", "Private App Gateway", icon="gateway", tunnel="WireGuard"))
            corp_crm = diag.add(Shape("corp_crm", "Corporate CRM", icon="server", access="Microsegmented"))
            corp_crm.below(app_gw, margin=30)

        # Position starting group
        g_1.at(60.0, 80.0)

        # Arrange groups in horizontal sequence
        g_2.right_of(g_1, margin=80)
        g_3.right_of(g_2, margin=80)

        # Establish inter-element connections with protocol annotations
        employee >> diag.edge("Sign-In Request", style="solid") >> idp
        device >> diag.edge("Posture State", style="solid") >> ztna_broker
        idp >> diag.edge("Identity Assertion", style="solid") >> ztna_broker
        ztna_broker >> diag.edge("Session Grant", style="solid") >> app_gw
        app_gw >> diag.edge("Local Proxy", style="solid") >> corp_crm

    return diag


def build_diagram(output_dir: Path | str = "output/cybersecurity") -> Path:
    return render_all(diagram(), output_dir, "03_zero_trust_ztna")["svg"]


if __name__ == "__main__":
    dest = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("output/cybersecurity")
    build_diagram(dest)
