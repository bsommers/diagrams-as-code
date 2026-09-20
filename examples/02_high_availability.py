#!/usr/bin/env python3
"""Example 02: IIoT High Availability UNS Architecture.

Recreates diagram-iiot-high-availability.py using the new directed placement engine
with load balancing, redundant cluster nodes, and dotted peer discovery.
"""
from __future__ import annotations

from pathlib import Path
import sys
from iiot_diagrams import Diagram, Port


def generate_high_availability(output_dir: Path | str = "output") -> Diagram:
    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    diag = Diagram(
        "IIoT High Availability UNS",
        width=1200,
        height=700,
        theme="iiot_dark_gold",
    )

    with diag:
        # Site 1: Production Plant (Baltimore)
        with diag.group(
            "Production Site (Baltimore)", padding=30.0, header_height=40.0
        ) as plant:
            sensors = diag.shape(
                "Plant Assets",
                width=140.0,
                height=60.0,
                kind="box",
                icon="sensor",
                metadata={"type": "Sensors & Actuators", "protocol": "Modbus/TCP"},
            ).at(60.0, 100.0)

            edge = diag.shape(
                "IIoT Edge",
                width=140.0,
                height=60.0,
                kind="box",
                icon="gateway",
                metadata={"role": "Edge Gateway", "tier": "Production Tier 1"},
            ).below(sensors, margin=80.0)

            # Local raw sensor ingestion
            sensors >> diag.edge(
                label="Raw Data",
                source_port=Port.SOUTH,
                target_port=Port.NORTH,
            ) >> edge

        # Ingress / Layer 4-7 Load Balancer
        lb = diag.shape(
            "Load Balancer",
            width=130.0,
            height=70.0,
            kind="diamond",
            icon="gateway",
            metadata={"type": "HAProxy / AWS NLB", "layer": "Transport"},
        ).right_of(plant, margin=80.0, align="center")

        # Control Plane HA Cluster with Redundant Nodes
        with diag.group(
            "IIoT HA Cluster (Control Plane)", padding=30.0, header_height=40.0
        ) as cluster:
            node1 = diag.shape(
                "Node 1",
                width=140.0,
                height=60.0,
                kind="server_rack",
                icon="broker",
                metadata={"role": "UNS Primary Leader", "cluster_id": "ha-cluster-01"},
            )
            node2 = diag.shape(
                "Node 2",
                width=140.0,
                height=60.0,
                kind="server_rack",
                icon="broker",
                metadata={"role": "UNS Replica Follower", "cluster_id": "ha-cluster-01"},
            ).below(node1, margin=30.0)
            node3 = diag.shape(
                "Node 3",
                width=140.0,
                height=60.0,
                kind="server_rack",
                icon="broker",
                metadata={"role": "UNS Replica Follower", "cluster_id": "ha-cluster-01"},
            ).below(node2, margin=30.0)

        cluster.right_of(lb, margin=80.0, align="center")

        # Edge to Load Balancer ingestion
        edge >> diag.edge(
            label="MQTT / TLS",
            source_port=Port.EAST,
            target_port=Port.WEST,
        ) >> lb

        # Load Balancer distributing ingress across all redundant nodes
        lb >> diag.edge(
            label="Round-Robin",
            source_port=Port.EAST,
            target_port=Port.WEST,
        ) >> [node1, node2, node3]

        # Inter-node peer discovery and consensus state sharing
        node1 >> diag.edge(
            label="Cluster Discovery",
            style="dotted",
            arrow_head=False,
            arrow_tail=False,
        ) >> node2

        node2 >> diag.edge(
            style="dotted",
            arrow_head=False,
            arrow_tail=False,
        ) >> node3

    svg_path = out_dir / "high_availability.svg"
    png_path = out_dir / "high_availability.png"
    readme_path = out_dir / "high_availability_README.md"

    diag.render_svg(svg_path)
    diag.render_png(png_path)
    diag.generate_readme(
        image_file="high_availability.svg",
        output_path=readme_path,
        include_connections=True,
    )

    print(f"Generated: {svg_path}")
    print(f"Generated: {png_path}")
    print(f"Generated: {readme_path}")
    return diag


if __name__ == "__main__":
    out_dir = sys.argv[1] if len(sys.argv) > 1 else "output"
    generate_high_availability(out_dir)
