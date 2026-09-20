"""Example architecture: 802.1X Network Access Control (NAC) & RADIUS (NETWORK_ENGINEERING domain)."""
from __future__ import annotations

import sys
from pathlib import Path

from diagrams_as_code import Diagram, Edge, Group, Shape


def build_diagram(output_dir: Path | str = "output/network_engineering") -> Path:
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    svg_file = out / "09_radius_802_1x_nac.svg"
    png_file = out / "09_radius_802_1x_nac.png"
    readme_file = out / "09_radius_802_1x_nac_README.md"

    with Diagram("802.1X Network Access Control (NAC) & RADIUS", theme="nord") as diag:
        with diag.group("Supplicant Endpoint") as g_1:
            supplicant = diag.add(Shape("supplicant", "Corporate Laptop", icon="laptop", auth="EAP-TLS Certificate"))

        with diag.group("Network Authenticator") as g_2:
            auth_sw = diag.add(Shape("auth_sw", "802.1X Access Switch", icon="switch", feature="Dynamic VLAN & ACLs"))

        with diag.group("Authentication Server") as g_3:
            radius_srv = diag.add(Shape("radius_srv", "FreeRADIUS / ISE Server", icon="server", protocol="RADIUS UDP 1812"))
            ca_ad = diag.add(Shape("ca_ad", "Active Directory & PKI", icon="database", check="LDAP / CRL Verification"))
            ca_ad.below(radius_srv, margin=30)

        with diag.group("Enforced Segments") as g_4:
            vlan_corp = diag.add(Shape("vlan_corp", "Corporate VLAN 100", icon="switch", subnet="10.100.0.0/24"))
            vlan_iso = diag.add(Shape("vlan_iso", "Quarantine VLAN 666", icon="switch", policy="Remediation Only"))
            vlan_iso.below(vlan_corp, margin=30)

        # Position starting group
        g_1.at(60.0, 80.0)

        # Arrange groups in horizontal sequence
        g_2.right_of(g_1, margin=50)
        g_3.right_of(g_2, margin=50)
        g_4.right_of(g_3, margin=50)

        # Establish inter-element connections with protocol annotations
        supplicant >> diag.edge("EAPoL-Start", style="solid") >> auth_sw
        auth_sw >> diag.edge("Access-Request", style="solid") >> radius_srv
        radius_srv >> diag.edge("Validate Cert", style="solid") >> ca_ad
        radius_srv >> diag.edge("Access-Accept", style="solid") >> auth_sw
        auth_sw >> diag.edge("Assign VLAN 100", style="solid") >> vlan_corp
        auth_sw >> diag.edge("Assign Quarantine", style="dashed") >> vlan_iso

    # Render outputs after diagram context resolves layout constraints
    diag.render_svg(svg_file)
    diag.render_png(png_file)
    diag.generate_readme("09_radius_802_1x_nac.svg", readme_file)

    return svg_file


if __name__ == "__main__":
    dest = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("output/network_engineering")
    build_diagram(dest)
