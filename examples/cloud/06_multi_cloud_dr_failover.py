"""Example architecture: Multi-Cloud Active-Passive Disaster Recovery (CLOUD domain)."""
from __future__ import annotations

import sys
from pathlib import Path

from diagrams_as_code import Diagram, Edge, Group, Shape
from diagrams_as_code.output import render_all


def diagram() -> Diagram:
    with Diagram("Multi-Cloud Active-Passive Disaster Recovery", theme="nord") as diag:
        with diag.group("Traffic Routing") as g_1:
            dns_mgr = diag.add(Shape("dns_mgr", "Global Traffic Manager", icon="dns", check="5s Probe"))

        with diag.group("AWS Primary (Active)") as g_2:
            aws_alb = diag.add(Shape("aws_alb", "Primary AWS Ingress", icon="api_gateway", region="us-east-1"))
            aws_app = diag.add(Shape("aws_app", "AWS ECS Application", icon="container", platform="Fargate"))
            aws_app.below(aws_alb, margin=30)
            aws_db = diag.add(Shape("aws_db", "AWS Aurora Master", icon="database", ha="Multi-AZ"))
            aws_db.below(aws_app, margin=30)

        with diag.group("Azure Disaster Recovery") as g_3:
            azure_agw = diag.add(Shape("azure_agw", "Secondary Azure Gateway", icon="api_gateway", region="eastus2"))
            azure_app = diag.add(Shape("azure_app", "Azure Container App", icon="container", platform="Warm Standby"))
            azure_app.below(azure_agw, margin=30)
            azure_db = diag.add(Shape("azure_db", "Azure Postgres Replica", icon="database", role="Read Standby"))
            azure_db.below(azure_app, margin=30)

        # Position starting group
        g_1.at(60.0, 80.0)

        # Arrange groups in horizontal sequence
        g_2.right_of(g_1, margin=80)
        g_3.right_of(g_2, margin=80)

        # Establish inter-element connections with protocol annotations
        dns_mgr >> diag.edge("Active (Weight 100)", style="solid") >> aws_alb
        dns_mgr >> diag.edge("Standby (Weight 0)", style="dashed", clearance=45) >> azure_agw
        aws_alb >> diag.edge("Proxy Route", style="solid") >> aws_app
        aws_app >> diag.edge("SQL R/W", style="solid") >> aws_db
        azure_agw >> diag.edge("Failover Traffic", style="dashed") >> azure_app
        azure_app >> diag.edge("Read Query", style="dashed") >> azure_db
        aws_db >> diag.edge("Cross-Cloud Replication", style="dotted") >> azure_db

    return diag


def build_diagram(output_dir: Path | str = "output/cloud") -> Path:
    return render_all(diagram(), output_dir, "06_multi_cloud_dr_failover")["svg"]


if __name__ == "__main__":
    dest = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("output/cloud")
    build_diagram(dest)
