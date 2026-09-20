"""Example architecture: Global Edge CDN & Origin Distribution (CLOUD domain)."""
from __future__ import annotations

import sys
from pathlib import Path

from diagrams_as_code import Diagram, Edge, Group, Shape


def build_diagram(output_dir: Path | str = "output/cloud") -> Path:
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    svg_file = out / "03_cdn_multi_region_edge.svg"
    png_file = out / "03_cdn_multi_region_edge.png"
    readme_file = out / "03_cdn_multi_region_edge_README.md"

    with Diagram("Global Edge CDN & Origin Distribution", theme="nord") as diag:
        with diag.group("Global Users") as g_1:
            user_na = diag.add(Shape("user_na", "North America Clients", icon="user", latency="<15ms"))
            user_eu = diag.add(Shape("user_eu", "Europe Clients", icon="user", latency="<20ms"))
            user_eu.below(user_na, margin=30)

        with diag.group("Routing Tier") as g_2:
            dns = diag.add(Shape("dns", "Route 53 Global DNS", icon="dns", routing="Geolocation"))

        with diag.group("Edge Infrastructure") as g_3:
            cdn = diag.add(Shape("cdn", "CloudFront CDN Edge", icon="cdn", cache="TTL 86400s"))
            waf = diag.add(Shape("waf", "AWS WAF Perimeter", icon="firewall", rules="OWASP Top 10"))
            waf.below(cdn, margin=30)

        with diag.group("Origin Tier") as g_4:
            s3_static = diag.add(Shape("s3_static", "S3 Static Assets", icon="storage", bucket="prod-web-assets"))
            alb_api = diag.add(Shape("alb_api", "Regional API Origin", icon="api_gateway", vpc="us-east-1 VPC"))
            alb_api.below(s3_static, margin=30)

        # Position starting group
        g_1.at(60.0, 80.0)

        # Arrange groups in horizontal sequence
        g_2.right_of(g_1, margin=50)
        g_3.right_of(g_2, margin=50)
        g_4.right_of(g_3, margin=50)

        # Establish inter-element connections with protocol annotations
        user_na >> diag.edge("DNS Query", style="solid") >> dns
        user_eu >> diag.edge("DNS Query", style="solid") >> dns
        dns >> diag.edge("Anycast IP", style="solid") >> cdn
        cdn >> diag.edge("Filter Threats", style="dashed") >> waf
        cdn >> diag.edge("Static Cache", style="solid") >> s3_static
        cdn >> diag.edge("API Forward", style="solid") >> alb_api

    # Render outputs after diagram context resolves layout constraints
    diag.render_svg(svg_file)
    diag.render_png(png_file)
    diag.generate_readme("03_cdn_multi_region_edge.svg", readme_file)

    return svg_file


if __name__ == "__main__":
    dest = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("output/cloud")
    build_diagram(dest)
