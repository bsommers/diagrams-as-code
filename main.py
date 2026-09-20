#!/usr/bin/env python3
"""Main entry point for IIoT Diagrams-as-Code.

Demonstrates the directed diagrams placement engine, hierarchical auto-bounding groups,
custom vector shapes, Manhattan orthogonal routing, and automated Bill of Materials generation.
"""
from __future__ import annotations

import sys
from pathlib import Path
from diagrams_as_code import Diagram, Port


def generate_main_architecture(output_dir: Path | str = "output") -> Diagram:
    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    diag = Diagram(
        "IIoT Reference Architecture",
        width=1200,
        height=700,
        theme="iiot_dark_gold",
    )

    with diag:
        # Edge Tier Group
        with diag.group("Plant Floor (Edge Tier)", padding=30.0, header_height=40.0) as plant:
            plc = diag.shape(
                "Automation PLC",
                width=150.0,
                height=65.0,
                kind="box",
                icon="sensor",
                metadata={"vendor": "Siemens S7-1500", "protocol": "OPC UA"},
            ).at(60.0, 100.0)

            edge = diag.shape(
                "IIoT Edge Gateway",
                width=150.0,
                height=65.0,
                kind="box",
                icon="gateway",
                metadata={"software": "Node-RED / Ignition Edge", "specs": "4-Core IPC"},
            ).below(plc, margin=80.0)

            plc >> diag.edge(
                label="OPC UA / Modbus",
                source_port=Port.SOUTH,
                target_port=Port.NORTH,
            ) >> edge

        # Cloud Platform Group
        with diag.group("Cloud Platform (UNS Tier)", padding=30.0, header_height=40.0) as cloud:
            broker = diag.shape(
                "Enterprise MQTT Broker",
                width=160.0,
                height=65.0,
                kind="server_rack",
                icon="broker",
                metadata={"engine": "Enterprise MQTT Broker Cluster", "ha": "3-Node Multi-AZ"},
            )

            db = diag.shape(
                "Time-Series Database",
                width=160.0,
                height=65.0,
                kind="database",
                icon="database",
                metadata={"engine": "InfluxDB Enterprise", "retention": "365 Days"},
            ).below(broker, margin=80.0)

            broker >> diag.edge(
                label="Historian Ingest",
                source_port=Port.SOUTH,
                target_port=Port.NORTH,
            ) >> db

        cloud.right_of(plant, margin=80.0, align="top")

        # Enterprise Monitoring Group
        with diag.group("Enterprise Operations", padding=30.0, header_height=40.0) as ops:
            scada = diag.shape(
                "Executive Dashboard",
                width=160.0,
                height=65.0,
                kind="box",
                icon="dashboard",
                metadata={"platform": "Grafana Enterprise", "kpis": "OEE / MTBF / Scada"},
            )

        ops.right_of(cloud, margin=80.0, align="top")

        # Inter-group data connections
        edge >> diag.edge(
            label="Secure TLS Bridge",
            source_port=Port.EAST,
            target_port=Port.WEST,
        ) >> broker

        broker >> diag.edge(
            label="Analytics Stream",
            source_port=Port.EAST,
            target_port=Port.WEST,
        ) >> scada

    svg_file = out_dir / "main_architecture.svg"
    png_file = out_dir / "main_architecture.png"
    readme_file = out_dir / "main_README.md"

    diag.render_svg(svg_file)
    diag.render_png(png_file)
    diag.generate_readme(
        image_file="main_architecture.svg",
        output_path=readme_file,
        include_connections=True,
    )

    print(f"Generated: {svg_file}")
    print(f"Generated: {png_file}")
    print(f"Generated: {readme_file}")

    return diag


def main() -> int:
    out_dir = sys.argv[1] if len(sys.argv) > 1 else "output"
    generate_main_architecture(out_dir)
    return 0


if __name__ == "__main__":
    sys.exit(main())
