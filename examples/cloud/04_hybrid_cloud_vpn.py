"""Example architecture: Hybrid Cloud IPSec & Transit Gateway (CLOUD domain)."""
from __future__ import annotations

import sys
from pathlib import Path

from diagrams_as_code import Diagram, Edge, Group, Shape


def build_diagram(output_dir: Path | str = "output/cloud") -> Path:
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    svg_file = out / "04_hybrid_cloud_vpn.svg"
    png_file = out / "04_hybrid_cloud_vpn.png"
    readme_file = out / "04_hybrid_cloud_vpn_README.md"

    with Diagram("Hybrid Cloud IPSec & Transit Gateway", theme="solarized_light") as diag:
        with diag.group("Corporate On-Prem") as g_1:
            onprem_gw = diag.add(Shape("onprem_gw", "Corporate VPN Gateway", icon="router", device="Cisco ASA"))
            onprem_srv = diag.add(Shape("onprem_srv", "Active Directory Server", icon="server", role="Identity Provider"))
            onprem_srv.below(onprem_gw, margin=30)

        with diag.group("Secure Interconnect") as g_2:
            ipsec = diag.add(Shape("ipsec", "Dual IPSec VPN Tunnels", icon="firewall", encryption="AES-256"))

        with diag.group("AWS Cloud Network") as g_3:
            tgw = diag.add(Shape("tgw", "AWS Transit Gateway", icon="vpc", asn="64512"))

        with diag.group("Spoke VPCs") as g_4:
            prod_vpc = diag.add(Shape("prod_vpc", "Production VPC", icon="vpc", cidr="10.100.0.0/16"))
            stage_vpc = diag.add(Shape("stage_vpc", "Staging VPC", icon="vpc", cidr="10.200.0.0/16"))
            stage_vpc.below(prod_vpc, margin=30)

        # Position starting group
        g_1.at(60.0, 80.0)

        # Arrange groups in horizontal sequence
        g_2.right_of(g_1, margin=80)
        g_3.right_of(g_2, margin=80)
        g_4.right_of(g_3, margin=80)

        # Establish inter-element connections with protocol annotations
        onprem_srv >> diag.edge("Local LAN", style="solid") >> onprem_gw
        onprem_gw >> diag.edge("IPSec Tunnel", style="solid") >> ipsec
        ipsec >> diag.edge("BGP Peering", style="solid") >> tgw
        tgw >> diag.edge("Attachment A", style="solid") >> prod_vpc
        tgw >> diag.edge("Attachment B", style="solid") >> stage_vpc

    # Render outputs after diagram context resolves layout constraints
    diag.render_svg(svg_file)
    diag.render_png(png_file)
    diag.generate_readme("04_hybrid_cloud_vpn.svg", readme_file)

    return svg_file


if __name__ == "__main__":
    dest = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("output/cloud")
    build_diagram(dest)
