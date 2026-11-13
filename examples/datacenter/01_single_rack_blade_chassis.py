"""Example architecture: High-Density Blade Server Enclosure (DATACENTER domain)."""
from __future__ import annotations

import sys
from pathlib import Path

from diagrams_as_code import Diagram, Edge, Group, Shape
from diagrams_as_code.output import render_all


def diagram() -> Diagram:
    with Diagram("High-Density Blade Server Enclosure", theme="iiot_dark_gold") as diag:
        with diag.group("Rack Enclosure 42U") as g_1:
            tor1 = diag.add(Shape("tor1", "Top-of-Rack Switch A", icon="router", speed="100GbE Uplinks"))
            tor2 = diag.add(Shape("tor2", "Top-of-Rack Switch B", icon="router", speed="100GbE Uplinks"))
            tor2.below(tor1, margin=30)

        with diag.group("Blade Chassis 10U") as g_2:
            chassis_mgmt = diag.add(Shape("chassis_mgmt", "Chassis Management Module", icon="terminal", interface="IPMI / Redfish"))
            blade1 = diag.add(Shape("blade1", "Blade Compute Node 01", icon="server", specs="2x Xeon Gold, 512GB"))
            blade1.below(chassis_mgmt, margin=30)
            blade2 = diag.add(Shape("blade2", "Blade Compute Node 02", icon="server", specs="2x Xeon Gold, 512GB"))
            blade2.below(blade1, margin=30)
            blade3 = diag.add(Shape("blade3", "Blade Compute Node 03", icon="server", specs="2x Xeon Gold, 512GB"))
            blade3.below(blade2, margin=30)

        # Position starting group
        g_1.at(60.0, 80.0)

        # Arrange groups in horizontal sequence
        g_2.right_of(g_1, margin=190)

        # Establish inter-element connections with protocol annotations
        tor1 >> diag.edge("10GbE Fabric", style="solid") >> blade1
        tor2 >> diag.edge("10GbE Fabric Redundant", style="dashed") >> blade1
        tor1 >> diag.edge("10GbE Fabric", style="solid") >> blade2
        tor2 >> diag.edge("10GbE Fabric Redundant", style="dashed") >> blade2
        chassis_mgmt >> diag.edge("Telemetry Bus", style="dotted") >> blade1
        chassis_mgmt >> diag.edge("Telemetry Bus", style="dotted") >> blade2

    return diag


def build_diagram(output_dir: Path | str = "output/datacenter") -> Path:
    return render_all(diagram(), output_dir, "01_single_rack_blade_chassis")["svg"]


if __name__ == "__main__":
    dest = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("output/datacenter")
    build_diagram(dest)
