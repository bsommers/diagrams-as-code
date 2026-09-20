"""Example architecture: AGV Fleet Telemetry & Traffic Management (IIOT domain)."""
from __future__ import annotations

import sys
from pathlib import Path

from diagrams_as_code import Diagram, Edge, Group, Shape


def build_diagram(output_dir: Path | str = "output/iiot") -> Path:
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    svg_file = out / "08_automated_guided_vehicle_fleet.svg"
    png_file = out / "08_automated_guided_vehicle_fleet.png"
    readme_file = out / "08_automated_guided_vehicle_fleet_README.md"

    with Diagram("AGV Fleet Telemetry & Traffic Management", theme="emerald") as diag:
        with diag.group("AGV Vehicles") as g_1:
            agv_1 = diag.add(Shape("agv_1", "AGV Unit 01 (Forklift)", icon="robot", battery="LiFePO4 48V"))
            agv_2 = diag.add(Shape("agv_2", "AGV Unit 02 (Tugger)", icon="robot", payload="1000kg"))
            agv_2.below(agv_1, margin=30)

        with diag.group("Facility Mesh") as g_2:
            ap_mesh = diag.add(Shape("ap_mesh", "Industrial Wi-Fi 6 APs", icon="router", coverage="Plant-wide"))

        with diag.group("Fleet Control") as g_3:
            fleet_srv = diag.add(Shape("fleet_srv", "Fleet Traffic Manager", icon="server", algo="Dynamic Routing"))
            hmi_disp = diag.add(Shape("hmi_disp", "Dispatcher Console", icon="hmi", view="Realtime Floor Map"))
            hmi_disp.below(fleet_srv, margin=30)

        # Position starting group
        g_1.at(60.0, 80.0)

        # Arrange groups in horizontal sequence
        g_2.right_of(g_1, margin=80)
        g_3.right_of(g_2, margin=80)

        # Establish inter-element connections with protocol annotations
        agv_1 >> diag.edge("Wi-Fi Telemetry", style="solid") >> ap_mesh
        agv_2 >> diag.edge("Wi-Fi Telemetry", style="solid") >> ap_mesh
        ap_mesh >> diag.edge("MQTT / UDP", style="solid") >> fleet_srv
        fleet_srv >> diag.edge("WebSocket UI", style="solid") >> hmi_disp

    # Render outputs after diagram context resolves layout constraints
    diag.render_svg(svg_file)
    diag.render_png(png_file)
    diag.generate_readme("08_automated_guided_vehicle_fleet.svg", readme_file)

    return svg_file


if __name__ == "__main__":
    dest = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("output/iiot")
    build_diagram(dest)
