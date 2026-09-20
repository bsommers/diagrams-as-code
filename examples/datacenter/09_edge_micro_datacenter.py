"""Example architecture: Modular Edge Micro-Datacenter Container (DATACENTER domain)."""
from __future__ import annotations

import sys
from pathlib import Path

from diagrams_as_code import Diagram, Edge, Group, Shape


def build_diagram(output_dir: Path | str = "output/datacenter") -> Path:
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    svg_file = out / "09_edge_micro_datacenter.svg"
    png_file = out / "09_edge_micro_datacenter.png"
    readme_file = out / "09_edge_micro_datacenter_README.md"

    with Diagram("Modular Edge Micro-Datacenter Container", theme="cyber_slate") as diag:
        with diag.group("Facilities Automation") as g_1:
            env_sensors = diag.add(Shape("env_sensors", "Environmental & Smoke Sensors", icon="sensor", detection="VESDA Laser Air"))
            fire_suppress = diag.add(Shape("fire_suppress", "Clean Agent Fire Extinguishing", icon="shield", agent="Novec 1230"))
            fire_suppress.below(env_sensors, margin=30)

        with diag.group("Critical Power") as g_2:
            ups_lithium = diag.add(Shape("ups_lithium", "Modular Lithium-Ion UPS (10kVA)", icon="ups", runtime="45 Minutes"))

        with diag.group("Compute & Virtualization") as g_3:
            hyperconverged = diag.add(Shape("hyperconverged", "3-Node Proxmox Micro-Cluster", icon="cluster", storage="Ceph Full Mesh"))

        with diag.group("Remote Management") as g_4:
            cellular_oob = diag.add(Shape("cellular_oob", "5G Out-of-Band Gateway", icon="router", failover="Dual SIM Cellular"))

        # Position starting group
        g_1.at(60.0, 80.0)

        # Arrange groups in horizontal sequence
        g_2.right_of(g_1, margin=50)
        g_3.right_of(g_2, margin=50)
        g_4.right_of(g_3, margin=50)

        # Establish inter-element connections with protocol annotations
        env_sensors >> diag.edge("Interlock Trigger", style="dashed") >> fire_suppress
        ups_lithium >> diag.edge("AC Power Feed", style="solid") >> hyperconverged
        hyperconverged >> diag.edge("Remote IPMI Console", style="solid") >> cellular_oob
        env_sensors >> diag.edge("Telemetry Telemetry", style="dashed") >> cellular_oob

    # Render outputs after diagram context resolves layout constraints
    diag.render_svg(svg_file)
    diag.render_png(png_file)
    diag.generate_readme("09_edge_micro_datacenter.svg", readme_file)

    return svg_file


if __name__ == "__main__":
    dest = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("output/datacenter")
    build_diagram(dest)
