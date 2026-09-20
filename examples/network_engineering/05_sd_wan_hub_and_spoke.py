"""Example architecture: Enterprise SD-WAN Hub-and-Spoke Topology (NETWORK_ENGINEERING domain)."""
from __future__ import annotations

import sys
from pathlib import Path

from diagrams_as_code import Diagram, Edge, Group, Shape


def build_diagram(output_dir: Path | str = "output/network_engineering") -> Path:
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    svg_file = out / "05_sd_wan_hub_and_spoke.svg"
    png_file = out / "05_sd_wan_hub_and_spoke.png"
    readme_file = out / "05_sd_wan_hub_and_spoke_README.md"

    with Diagram("Enterprise SD-WAN Hub-and-Spoke Topology", theme="emerald") as diag:
        with diag.group("SD-WAN Control Plane") as g_1:
            vmanage = diag.add(Shape("vmanage", "SD-WAN Orchestrator", icon="server", role="vManage NMS"))
            vsmart = diag.add(Shape("vsmart", "SD-WAN Route Controller", icon="core_router", protocol="OMP Policy"))
            vsmart.below(vmanage, margin=30)

        with diag.group("Headquarters Hub") as g_2:
            hub = diag.add(Shape("hub", "Headquarters Hub Router", icon="core_router", throughput="10 Gbps IPsec"))

        with diag.group("Remote Branch Sites") as g_3:
            branch1 = diag.add(Shape("branch1", "Branch 01 Appliance", icon="router", uplink="Broadband + LTE"))
            branch2 = diag.add(Shape("branch2", "Branch 02 Appliance", icon="router", uplink="Dual Fiber Broadband"))
            branch2.below(branch1, margin=30)

        # Position starting group
        g_1.at(60.0, 80.0)

        # Arrange groups in horizontal sequence
        g_2.right_of(g_1, margin=80)
        g_3.right_of(g_2, margin=80)

        # Establish inter-element connections with protocol annotations
        vsmart >> diag.edge("OMP Routing", style="solid") >> hub
        vsmart >> diag.edge("OMP Policy", style="solid") >> branch1
        vsmart >> diag.edge("OMP Policy", style="solid") >> branch2
        hub >> diag.edge("IPsec Tunnel", style="solid") >> branch1
        hub >> diag.edge("IPsec Tunnel", style="solid") >> branch2

    # Render outputs after diagram context resolves layout constraints
    diag.render_svg(svg_file)
    diag.render_png(png_file)
    diag.generate_readme("05_sd_wan_hub_and_spoke.svg", readme_file)

    return svg_file


if __name__ == "__main__":
    dest = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("output/network_engineering")
    build_diagram(dest)
