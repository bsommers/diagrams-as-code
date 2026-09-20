#!/usr/bin/env python3
"""Example 01: IIoT Architecture Slide Recreation.

Recreates mock-up.txt and diagram-architecture-slide.py using the new
directed placement engine with hierarchical group flow and orthogonal routing.
"""
from __future__ import annotations

from pathlib import Path
import sys
from iiot_diagrams import Diagram, Port


def generate_mockup_slide(output_dir: Path | str = "output") -> Diagram:
    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    diag = Diagram(
        "IIoT Client Reference UNS",
        width=1200,
        height=700,
        theme="iiot_dark_gold",
    )

    with diag:
        # Column 1: On-Premise Site (Baltimore)
        with diag.group(
            "On-Premise (Baltimore)", padding=30.0, header_height=40.0
        ) as plant:
            asset = diag.shape(
                "Asset / PLC",
                width=150.0,
                height=70.0,
                kind="box",
                icon="sensor",
                metadata={
                    "equipment": "Allen-Bradley PLC",
                    "protocol": "OPC UA / Modbus",
                    "layer": "Physical Automation",
                },
            ).at(60.0, 100.0)

            edge = diag.shape(
                "IIoT Edge",
                width=150.0,
                height=70.0,
                kind="box",
                icon="gateway",
                metadata={
                    "role": "Edge Gateway",
                    "software": "Edge MQTT Publisher",
                    "layer": "Edge Processing",
                },
            ).below(asset, margin=100.0)

            # Raw internal OT data flow
            asset >> diag.edge(
                label="Modbus/TCP",
                source_port=Port.SOUTH,
                target_port=Port.NORTH,
            ) >> edge

        # Column 2: IIoT Cloud Managed Cluster
        with diag.group(
            "IIoT Cloud (Managed)", padding=30.0, header_height=40.0
        ) as cloud:
            cloud_broker = diag.shape(
                "Central Broker",
                width=160.0,
                height=70.0,
                kind="server_rack",
                icon="broker",
                metadata={
                    "service": "Enterprise UNS Broker",
                    "provider": "Managed Cloud",
                    "qos": "QoS 1 TLS",
                },
            )

        cloud.right_of(plant, margin=80.0, align="top")

        # Column 3: Remote Monitoring & Visualization
        with diag.group(
            "Remote Monitoring", padding=30.0, header_height=40.0
        ) as monitoring:
            dashboard = diag.shape(
                "Grafana Executive View",
                width=170.0,
                height=70.0,
                kind="box",
                icon="dashboard",
                metadata={
                    "app": "Grafana Cloud",
                    "audience": "Operations & Executives",
                },
            )

        monitoring.right_of(cloud, margin=80.0, align="top")

        # Edge-to-Cloud Bridge connection with protocol badge
        edge >> diag.edge(
            label="Secure MQTT Bridge",
            source_port=Port.EAST,
            target_port=Port.WEST,
        ) >> cloud_broker

        # Cloud-to-Monitoring subscription flow
        cloud_broker >> diag.edge(
            label="Subscribe: #",
            source_port=Port.EAST,
            target_port=Port.WEST,
        ) >> dashboard

    svg_path = out_dir / "mockup_slide.svg"
    png_path = out_dir / "mockup_slide.png"
    readme_path = out_dir / "mockup_slide_README.md"

    diag.render_svg(svg_path)
    diag.render_png(png_path)
    diag.generate_readme(
        image_file="mockup_slide.svg",
        output_path=readme_path,
        include_connections=True,
    )

    print(f"Generated: {svg_path}")
    print(f"Generated: {png_path}")
    print(f"Generated: {readme_path}")
    return diag


if __name__ == "__main__":
    out_dir = sys.argv[1] if len(sys.argv) > 1 else "output"
    generate_mockup_slide(out_dir)
