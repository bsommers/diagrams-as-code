"""Example architecture: Baltimore Plant to Managed Cloud (IIOT domain)."""
from __future__ import annotations

import sys
from pathlib import Path

from diagrams_as_code import Diagram, Edge, Group, Shape


def build_diagram(output_dir: Path | str = "output/iiot") -> Path:
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    svg_file = out / "01_baltimore_plant_to_cloud.svg"
    png_file = out / "01_baltimore_plant_to_cloud.png"
    readme_file = out / "01_baltimore_plant_to_cloud_README.md"

    with Diagram("Baltimore Plant to Managed Cloud", theme="iiot_dark_gold") as diag:
        with diag.group("On-Premise (Baltimore)") as g_1:
            plc = diag.add(Shape("plc", "Automation PLC", icon="sensor", vendor="Siemens S7-1500", protocol="Modbus"))
            edge = diag.add(Shape("edge", "IIoT Edge Gateway", icon="gateway", runtime="Node-RED", specs="IPC"))
            edge.below(plc, margin=30)

        with diag.group("IIoT Cloud (Managed)") as g_2:
            broker = diag.add(Shape("broker", "Central MQTT Broker", icon="broker", service="UNS Broker", qos="QoS 1"))

        with diag.group("Remote Monitoring") as g_3:
            dashboard = diag.add(Shape("dashboard", "Grafana Executive View", icon="dashboard", app="Grafana Cloud", kpis="OEE"))

        # Position starting group
        g_1.at(60.0, 80.0)

        # Arrange groups in horizontal sequence
        g_2.right_of(g_1, margin=80)
        g_3.right_of(g_2, margin=80)

        # Establish inter-element connections with protocol annotations
        plc >> diag.edge("Modbus TCP", style="solid") >> edge
        edge >> diag.edge("MQTT TLS", style="solid") >> broker
        broker >> diag.edge("Dashboard Stream", style="solid") >> dashboard

    # Render outputs after diagram context resolves layout constraints
    diag.render_svg(svg_file)
    diag.render_png(png_file)
    diag.generate_readme("01_baltimore_plant_to_cloud.svg", readme_file)

    return svg_file


if __name__ == "__main__":
    dest = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("output/iiot")
    build_diagram(dest)
