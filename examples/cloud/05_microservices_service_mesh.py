"""Example architecture: Microservices Service Mesh Architecture (CLOUD domain)."""
from __future__ import annotations

import sys
from pathlib import Path

from diagrams_as_code import Diagram, Edge, Group, Shape


def build_diagram(output_dir: Path | str = "output/cloud") -> Path:
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    svg_file = out / "05_microservices_service_mesh.svg"
    png_file = out / "05_microservices_service_mesh.png"
    readme_file = out / "05_microservices_service_mesh_README.md"

    with Diagram("Microservices Service Mesh Architecture", theme="nord") as diag:
        with diag.group("Edge Routing") as g_1:
            ingress = diag.add(Shape("ingress", "Ingress Envoy Gateway", icon="api_gateway", protocol="HTTP/2 gRPC"))

        with diag.group("Services Mesh") as g_2:
            auth_svc = diag.add(Shape("auth_svc", "Auth Microservice", icon="serverless", framework="Go / Gin"))
            catalog_svc = diag.add(Shape("catalog_svc", "Catalog Service", icon="server", framework="NestJS"))
            catalog_svc.below(auth_svc, margin=30)
            order_svc = diag.add(Shape("order_svc", "Order Service", icon="server", framework="Spring Boot"))
            order_svc.below(catalog_svc, margin=30)

        with diag.group("Data Layer") as g_3:
            redis = diag.add(Shape("redis", "Redis Session Cache", icon="storage", cluster="Redis 7"))
            db_orders = diag.add(Shape("db_orders", "Orders Database", icon="database", engine="Aurora Postgres"))
            db_orders.below(redis, margin=30)

        # Position starting group
        g_1.at(60.0, 80.0)

        # Arrange groups in horizontal sequence
        g_2.right_of(g_1, margin=80)
        g_3.right_of(g_2, margin=80)

        # Establish inter-element connections with protocol annotations
        ingress >> diag.edge("Validate JWT", style="solid") >> auth_svc
        ingress >> diag.edge("mTLS Route", style="solid") >> catalog_svc
        ingress >> diag.edge("mTLS Route", style="solid") >> order_svc
        auth_svc >> diag.edge("Cache Session", style="solid") >> redis
        order_svc >> diag.edge("Persist Order", style="solid") >> db_orders

    # Render outputs after diagram context resolves layout constraints
    diag.render_svg(svg_file)
    diag.render_png(png_file)
    diag.generate_readme("05_microservices_service_mesh.svg", readme_file)

    return svg_file


if __name__ == "__main__":
    dest = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("output/cloud")
    build_diagram(dest)
