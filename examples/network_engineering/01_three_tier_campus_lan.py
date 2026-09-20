"""Example architecture: Three-Tier Hierarchical Campus LAN (NETWORK_ENGINEERING domain)."""
from __future__ import annotations

import sys
from pathlib import Path

from diagrams_as_code import Diagram, Edge, Group, Shape


def build_diagram(output_dir: Path | str = "output/network_engineering") -> Path:
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    svg_file = out / "01_three_tier_campus_lan.svg"
    png_file = out / "01_three_tier_campus_lan.png"
    readme_file = out / "01_three_tier_campus_lan_README.md"

    with Diagram("Three-Tier Hierarchical Campus LAN", theme="blueprint") as diag:
        with diag.group("Campus Core Layer") as g_1:
            core1 = diag.add(Shape("core1", "Core Switch Alpha", icon="switch", model="Catalyst 9600"))
            core2 = diag.add(Shape("core2", "Core Switch Beta", icon="switch", model="Catalyst 9600"))
            core2.below(core1, margin=30)

        with diag.group("Distribution Aggregation") as g_2:
            dist1 = diag.add(Shape("dist1", "Distribution Switch 1", icon="switch", routing="OSPF / HSRP"))
            dist2 = diag.add(Shape("dist2", "Distribution Switch 2", icon="switch", routing="OSPF / HSRP"))
            dist2.below(dist1, margin=30)

        with diag.group("Access Edge Layer") as g_3:
            acc1 = diag.add(Shape("acc1", "Floor 1 Access Switch", icon="switch", poe="802.3bt PoE++"))
            acc2 = diag.add(Shape("acc2", "Floor 2 Access Switch", icon="switch", poe="802.3bt PoE++"))
            acc2.below(acc1, margin=30)

        # Position starting group
        g_1.at(60.0, 80.0)

        # Arrange groups in horizontal sequence
        g_2.right_of(g_1, margin=50)
        g_3.right_of(g_2, margin=50)

        # Establish inter-element connections with protocol annotations
        core1 >> diag.edge("100G Interconnect", style="solid") >> core2
        core1 >> diag.edge("40G Uplink", style="solid") >> dist1
        core2 >> diag.edge("40G Uplink", style="solid") >> dist2
        dist1 >> diag.edge("Cross-Link", style="solid") >> core2
        dist2 >> diag.edge("Cross-Link", style="solid") >> core1
        dist1 >> diag.edge("10G Trunk", style="solid") >> acc1
        dist2 >> diag.edge("10G Trunk", style="solid") >> acc2

    # Render outputs after diagram context resolves layout constraints
    diag.render_svg(svg_file)
    diag.render_png(png_file)
    diag.generate_readme("01_three_tier_campus_lan.svg", readme_file)

    return svg_file


if __name__ == "__main__":
    dest = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("output/network_engineering")
    build_diagram(dest)
