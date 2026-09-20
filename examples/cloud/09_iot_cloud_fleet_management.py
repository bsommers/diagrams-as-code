"""Example architecture: Cloud IoT Fleet Telemetry & Management (CLOUD domain)."""
from __future__ import annotations

import sys
from pathlib import Path

from diagrams_as_code import Diagram, Edge, Group, Shape


def build_diagram(output_dir: Path | str = "output/cloud") -> Path:
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    svg_file = out / "09_iot_cloud_fleet_management.svg"
    png_file = out / "09_iot_cloud_fleet_management.png"
    readme_file = out / "09_iot_cloud_fleet_management_README.md"

    with Diagram("Cloud IoT Fleet Telemetry & Management", theme="iiot_dark_gold") as diag:
        with diag.group("Edge Devices") as g_1:
            fleet = diag.add(Shape("fleet", "Connected Vehicle Fleet", icon="sensor", units="100k Vehicles"))

        with diag.group("IoT Ingest Tier") as g_2:
            iot_core = diag.add(Shape("iot_core", "AWS IoT Core Broker", icon="broker", protocol="MQTT v5"))

        with diag.group("Processing Tier") as g_3:
            rules = diag.add(Shape("rules", "IoT Rules Engine", icon="workflow", filter="SQL Evaluation"))

        with diag.group("Device State Tier") as g_4:
            shadow = diag.add(Shape("shadow", "Device Shadow Store", icon="database", format="JSON Delta"))

        with diag.group("Streaming Tier") as g_5:
            kinesis = diag.add(Shape("kinesis", "Kinesis Analytics", icon="queue", window="10s Tumbling"))

        with diag.group("Telemetry Storage") as g_6:
            timescale = diag.add(Shape("timescale", "TimescaleDB Cluster", icon="database", hypertables="Compressed"))

        with diag.group("Visualization") as g_7:
            dash = diag.add(Shape("dash", "Grafana Live Telemetry", icon="dashboard", refresh="1s Stream"))

        # Position starting group
        g_1.at(60.0, 80.0)

        # Arrange groups in horizontal sequence
        g_2.right_of(g_1, margin=50)
        g_3.right_of(g_2, margin=50)
        g_4.right_of(g_3, margin=50)
        g_5.right_of(g_4, margin=50)
        g_6.right_of(g_5, margin=50)
        g_7.right_of(g_6, margin=50)

        # Establish inter-element connections with protocol annotations
        fleet >> diag.edge("MQTT :8883", style="solid") >> iot_core
        iot_core >> diag.edge("Filter Topic", style="solid") >> rules
        rules >> diag.edge("Sync State", style="solid") >> shadow
        rules >> diag.edge("High Frequency Stream", style="solid") >> kinesis
        kinesis >> diag.edge("Batch Insert", style="solid") >> timescale
        timescale >> diag.edge("SQL Query", style="solid") >> dash

    # Render outputs after diagram context resolves layout constraints
    diag.render_svg(svg_file)
    diag.render_png(png_file)
    diag.generate_readme("09_iot_cloud_fleet_management.svg", readme_file)

    return svg_file


if __name__ == "__main__":
    dest = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("output/cloud")
    build_diagram(dest)
