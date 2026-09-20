"""Example architecture: Dual-Homed Industrial Edge Gateway (COMPUTER domain)."""
from __future__ import annotations

import sys
from pathlib import Path

from diagrams_as_code import Diagram, Edge, Group, Shape


def build_diagram(output_dir: Path | str = "output/computer") -> Path:
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    svg_file = out / "04_dual_homed_edge_gateway.svg"
    png_file = out / "04_dual_homed_edge_gateway.png"
    readme_file = out / "04_dual_homed_edge_gateway_README.md"

    with Diagram("Dual-Homed Industrial Edge Gateway", theme="cyber_slate") as diag:
        with diag.group("OT Factory Floor") as g_1:
            field_sensors = diag.add(Shape("field_sensors", "RS-485 Modbus RTU Slaves", icon="sensor", baud="115200 bps"))

        with diag.group("Edge Demarcation") as g_2:
            edge_ipc = diag.add(Shape("edge_ipc", "Rugged Industrial PC Gateway", icon="laptop", os="Debian Linux Real-Time"))

        with diag.group("Network Interfaces") as g_3:
            ot_nic = diag.add(Shape("ot_nic", "Isolated OT Ethernet Port", icon="router", ip="192.168.100.1 (Airgapped)"))
            it_nic = diag.add(Shape("it_nic", "Encrypted IT Ethernet Port", icon="router", ip="10.0.50.25 (Corporate LAN)"))
            it_nic.below(ot_nic, margin=30)

        with diag.group("Corporate IT Network") as g_4:
            corp_server = diag.add(Shape("corp_server", "Enterprise SCADA Host", icon="server", database="PostgreSQL Timescale"))

        # Position starting group
        g_1.at(60.0, 80.0)

        # Arrange groups in horizontal sequence
        g_2.right_of(g_1, margin=50)
        g_3.right_of(g_2, margin=50)
        g_4.right_of(g_3, margin=50)

        # Establish inter-element connections with protocol annotations
        field_sensors >> diag.edge("Serial RS-485", style="solid") >> edge_ipc
        edge_ipc >> diag.edge("Internal Bus", style="dashed") >> ot_nic
        edge_ipc >> diag.edge("Firewall NAT", style="dashed") >> it_nic
        it_nic >> diag.edge("TLS MQTT / Sparkplug", style="solid") >> corp_server

    # Render outputs after diagram context resolves layout constraints
    diag.render_svg(svg_file)
    diag.render_png(png_file)
    diag.generate_readme("04_dual_homed_edge_gateway.svg", readme_file)

    return svg_file


if __name__ == "__main__":
    dest = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("output/computer")
    build_diagram(dest)
