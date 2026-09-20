"""Example architecture: Simple VPC Web Application (CLOUD domain)."""
from __future__ import annotations

import sys
from pathlib import Path

from diagrams_as_code import Diagram, Edge, Group, Shape


def build_diagram(output_dir: Path | str = "output/cloud") -> Path:
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    svg_file = out / "01_simple_vpc_web.svg"
    png_file = out / "01_simple_vpc_web.png"
    readme_file = out / "01_simple_vpc_web_README.md"

    with Diagram("Simple VPC Web Application", theme="blueprint") as diag:
        with diag.group("Public Zone") as g_1:
            client = diag.add(Shape("client", "Web Client", icon="mobile", type="Mobile/Browser"))

        with diag.group("Public Subnet") as g_2:
            alb = diag.add(Shape("alb", "Application LB", icon="api_gateway", layer="Layer 7", protocol="HTTPS"))

        with diag.group("Private App Subnet") as g_3:
            web1 = diag.add(Shape("web1", "Web Server 01", icon="server", cpu="2 vCPU", mem="4GB"))
            web2 = diag.add(Shape("web2", "Web Server 02", icon="server", cpu="2 vCPU", mem="4GB"))
            web2.below(web1, margin=30)

        with diag.group("Private DB Subnet") as g_4:
            db = diag.add(Shape("db", "Primary PostgreSQL", icon="database", engine="PostgreSQL 16", ha="Multi-AZ"))

        # Position starting group
        g_1.at(60.0, 80.0)

        # Arrange groups in horizontal sequence
        g_2.right_of(g_1, margin=50)
        g_3.right_of(g_2, margin=50)
        g_4.right_of(g_3, margin=50)

        # Establish inter-element connections with protocol annotations
        client >> diag.edge("HTTPS :443", style="solid") >> alb
        alb >> diag.edge("HTTP :8080", style="solid") >> web1
        alb >> diag.edge("HTTP :8080", style="solid") >> web2
        web1 >> diag.edge("TCP :5432", style="solid") >> db
        web2 >> diag.edge("TCP :5432", style="solid") >> db

    # Render outputs after diagram context resolves layout constraints
    diag.render_svg(svg_file)
    diag.render_png(png_file)
    diag.generate_readme("01_simple_vpc_web.svg", readme_file)

    return svg_file


if __name__ == "__main__":
    dest = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("output/cloud")
    build_diagram(dest)
