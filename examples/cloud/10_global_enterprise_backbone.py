"""Example architecture: Global Enterprise Multi-Region Network Backbone (CLOUD domain)."""
from __future__ import annotations

import sys
from pathlib import Path

from diagrams_as_code import Diagram, Edge, Group, Shape


def build_diagram(output_dir: Path | str = "output/cloud") -> Path:
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    svg_file = out / "10_global_enterprise_backbone.svg"
    png_file = out / "10_global_enterprise_backbone.png"
    readme_file = out / "10_global_enterprise_backbone_README.md"

    with Diagram("Global Enterprise Multi-Region Network Backbone", theme="blueprint") as diag:
        with diag.group("Americas Region") as g_1:
            us_dc = diag.add(Shape("us_dc", "Americas On-Prem DC", icon="router", location="Chicago, IL"))
            us_vpc = diag.add(Shape("us_vpc", "AWS US-East VPC", icon="vpc", cidr="10.10.0.0/16"))
            us_vpc.below(us_dc, margin=30)

        with diag.group("Europe Region") as g_2:
            eu_dc = diag.add(Shape("eu_dc", "Europe On-Prem DC", icon="router", location="Frankfurt, DE"))
            eu_vpc = diag.add(Shape("eu_vpc", "AWS EU-Central VPC", icon="vpc", cidr="10.20.0.0/16"))
            eu_vpc.below(eu_dc, margin=30)

        with diag.group("Asia-Pacific Region") as g_3:
            ap_vpc = diag.add(Shape("ap_vpc", "AWS AP-East VPC", icon="vpc", cidr="10.30.0.0/16"))

        with diag.group("Global Core") as g_4:
            cloud_wan = diag.add(Shape("cloud_wan", "AWS Cloud WAN Backbone", icon="cloud", bgp="ASN 64512"))

        with diag.group("Governance") as g_5:
            sec_hub = diag.add(Shape("sec_hub", "Security Hub & Audit", icon="shield", audit="Real-Time CIS"))

        # Position starting group
        g_1.at(60.0, 80.0)

        # Arrange groups in horizontal sequence
        g_2.right_of(g_1, margin=50)
        g_3.right_of(g_2, margin=50)
        g_4.right_of(g_3, margin=50)
        g_5.right_of(g_4, margin=50)

        # Establish inter-element connections with protocol annotations
        us_dc >> diag.edge("DirectConnect 10G", style="solid") >> us_vpc
        eu_dc >> diag.edge("DirectConnect 10G", style="solid") >> eu_vpc
        us_vpc >> diag.edge("Core Route", style="solid") >> cloud_wan
        eu_vpc >> diag.edge("Core Route", style="solid") >> cloud_wan
        ap_vpc >> diag.edge("Core Route", style="solid") >> cloud_wan
        cloud_wan >> diag.edge("VPC Flow Logs", style="dashed") >> sec_hub

    # Render outputs after diagram context resolves layout constraints
    diag.render_svg(svg_file)
    diag.render_png(png_file)
    diag.generate_readme("10_global_enterprise_backbone.svg", readme_file)

    return svg_file


if __name__ == "__main__":
    dest = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("output/cloud")
    build_diagram(dest)
