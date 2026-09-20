"""Example architecture: Global Anycast Authoritative DNS Network (NETWORK_ENGINEERING domain)."""
from __future__ import annotations

import sys
from pathlib import Path

from iiot_diagrams import Diagram, Edge, Group, Shape


def build_diagram(output_dir: Path | str = "output/network_engineering") -> Path:
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    svg_file = out / "10_dns_anycast_authoritative_mesh.svg"
    png_file = out / "10_dns_anycast_authoritative_mesh.png"
    readme_file = out / "10_dns_anycast_authoritative_mesh_README.md"

    with Diagram("Global Anycast Authoritative DNS Network", theme="cyber_slate") as diag:
        with diag.group("Global Client Query Ingress") as g_1:
            client_query = diag.add(Shape("client_query", "Global DNS Clients", icon="user", ip="Query 192.0.2.1"))

        with diag.group("US-East PoP") as g_2:
            rtr_us = diag.add(Shape("rtr_us", "BGP Router US-East", icon="core_router", asn="AS 64512 Anycast"))
            dns_us = diag.add(Shape("dns_us", "Authoritative BIND US", icon="server", engine="Knot / BIND9"))
            dns_us.below(rtr_us, margin=30)

        with diag.group("EU-Central PoP") as g_3:
            rtr_eu = diag.add(Shape("rtr_eu", "BGP Router EU-Central", icon="core_router", asn="AS 64512 Anycast"))
            dns_eu = diag.add(Shape("dns_eu", "Authoritative BIND EU", icon="server", engine="Knot / BIND9"))
            dns_eu.below(rtr_eu, margin=30)

        with diag.group("Control Plane") as g_4:
            master_db = diag.add(Shape("master_db", "Hidden Master Database", icon="database", sync="TSIG AXFR / IXFR"))

        # Arrange groups in horizontal sequence
        g_2.right_of(g_1, margin=50)
        g_3.right_of(g_2, margin=50)
        g_4.right_of(g_3, margin=50)

        # Establish inter-element connections with protocol annotations
        client_query >> diag.edge("Lowest Latency Route", style="solid") >> rtr_us
        client_query >> diag.edge("Lowest Latency Route", style="solid") >> rtr_eu
        rtr_us >> diag.edge("Local Forward", style="solid") >> dns_us
        rtr_eu >> diag.edge("Local Forward", style="solid") >> dns_eu
        master_db >> diag.edge("Zone Replication", style="solid") >> dns_us
        master_db >> diag.edge("Zone Replication", style="solid") >> dns_eu

        diag.render_svg(svg_file)
        diag.render_png(png_file)
        diag.generate_readme("10_dns_anycast_authoritative_mesh.svg", readme_file)

    return svg_file


if __name__ == "__main__":
    dest = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("output/network_engineering")
    build_diagram(dest)
