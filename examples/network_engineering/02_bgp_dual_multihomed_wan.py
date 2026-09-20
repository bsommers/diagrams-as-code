"""Example architecture: Dual-Homed eBGP Enterprise WAN Peering (NETWORK_ENGINEERING domain)."""
from __future__ import annotations

import sys
from pathlib import Path

from diagrams_as_code import Diagram, Edge, Group, Shape


def build_diagram(output_dir: Path | str = "output/network_engineering") -> Path:
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    svg_file = out / "02_bgp_dual_multihomed_wan.svg"
    png_file = out / "02_bgp_dual_multihomed_wan.png"
    readme_file = out / "02_bgp_dual_multihomed_wan_README.md"

    with Diagram("Dual-Homed eBGP Enterprise WAN Peering", theme="cyber_slate") as diag:
        with diag.group("Upstream Transit Providers") as g_1:
            isp1 = diag.add(Shape("isp1", "Tier-1 ISP A (AS 174)", icon="bgp", routes="Full BGP Table"))
            isp2 = diag.add(Shape("isp2", "Tier-1 ISP B (AS 2914)", icon="bgp", routes="Full BGP Table"))
            isp2.below(isp1, margin=30)

        with diag.group("Enterprise Edge AS 65001") as g_2:
            edge1 = diag.add(Shape("edge1", "BGP Edge Router 1", icon="core_router", hardware="Juniper MX204"))
            edge2 = diag.add(Shape("edge2", "BGP Edge Router 2", icon="core_router", hardware="Juniper MX204"))
            edge2.below(edge1, margin=30)

        with diag.group("Enterprise Internal Core") as g_3:
            core_fabric = diag.add(Shape("core_fabric", "Campus Core Fabric", icon="switch", backbone="ECMP Routing"))

        # Position starting group
        g_1.at(60.0, 80.0)

        # Arrange groups in horizontal sequence
        g_2.right_of(g_1, margin=50)
        g_3.right_of(g_2, margin=50)

        # Establish inter-element connections with protocol annotations
        isp1 >> diag.edge("eBGP Peering", style="solid") >> edge1
        isp2 >> diag.edge("eBGP Peering", style="solid") >> edge2
        edge1 >> diag.edge("iBGP Full Mesh", style="solid") >> edge2
        edge1 >> diag.edge("OSPF Internal", style="solid") >> core_fabric
        edge2 >> diag.edge("OSPF Internal", style="solid") >> core_fabric

    # Render outputs after diagram context resolves layout constraints
    diag.render_svg(svg_file)
    diag.render_png(png_file)
    diag.generate_readme("02_bgp_dual_multihomed_wan.svg", readme_file)

    return svg_file


if __name__ == "__main__":
    dest = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("output/network_engineering")
    build_diagram(dest)
