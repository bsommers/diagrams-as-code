"""Example architecture: High Availability Broker Cluster (IIOT domain)."""
from __future__ import annotations

import sys
from pathlib import Path

from diagrams_as_code import Diagram, Edge, Group, Shape
from diagrams_as_code.output import render_all


def diagram() -> Diagram:
    with Diagram("High Availability Broker Cluster", theme="iiot_dark_gold") as diag:
        with diag.group("Production Ingress") as g_1:
            lb = diag.add(Shape("lb", "Load Balancer", icon="load_balancer", algorithm="Round Robin", vip="10.0.0.10"))

        with diag.group("IIoT HA Cluster") as g_2:
            node1 = diag.add(Shape("node1", "Broker Node 1", icon="broker", role="Active", zone="Zone A"))
            node2 = diag.add(Shape("node2", "Broker Node 2", icon="broker", role="Active", zone="Zone B"))
            node2.below(node1, margin=30)
            node3 = diag.add(Shape("node3", "Broker Node 3", icon="broker", role="Active", zone="Zone C"))
            node3.below(node2, margin=30)

        with diag.group("Storage & Analytics") as g_3:
            db = diag.add(Shape("db", "Clustered Database", icon="database", engine="PostgreSQL 16", ha="Multi-AZ"))

        # Position starting group
        g_1.at(60.0, 80.0)

        # Arrange groups in horizontal sequence
        g_2.right_of(g_1, margin=80)
        g_3.right_of(g_2, margin=80)

        # Establish inter-element connections with protocol annotations
        lb >> diag.edge("TCP :1883", style="solid") >> node1
        lb >> diag.edge("TCP :1883", style="solid") >> node2
        lb >> diag.edge("TCP :1883", style="solid") >> node3
        node1 >> diag.edge("Event Store", style="solid") >> db
        node2 >> diag.edge("Event Store", style="solid") >> db
        node3 >> diag.edge("Event Store", style="solid") >> db

    return diag


def build_diagram(output_dir: Path | str = "output/iiot") -> Path:
    return render_all(diagram(), output_dir, "02_high_availability_broker")["svg"]


if __name__ == "__main__":
    dest = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("output/iiot")
    build_diagram(dest)
