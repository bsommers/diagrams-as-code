"""Example architecture: Leaf-Spine Clos Datacenter Network (DATACENTER domain)."""
from __future__ import annotations

import sys
from pathlib import Path

from diagrams_as_code import Diagram, Edge, Group, Shape


def build_diagram(output_dir: Path | str = "output/datacenter") -> Path:
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    svg_file = out / "03_leaf_spine_clos_network.svg"
    png_file = out / "03_leaf_spine_clos_network.png"
    readme_file = out / "03_leaf_spine_clos_network_README.md"

    with Diagram("Leaf-Spine Clos Datacenter Network", theme="cyber_slate") as diag:
        with diag.group("Spine Layer") as g_1:
            spine1 = diag.add(Shape("spine1", "Core Spine Switch 01", icon="router", throughput="32x 400GbE Ports"))
            spine2 = diag.add(Shape("spine2", "Core Spine Switch 02", icon="router", throughput="32x 400GbE Ports"))
            spine2.below(spine1, margin=30)

        with diag.group("Leaf Layer") as g_2:
            leaf1 = diag.add(Shape("leaf1", "Leaf Switch 01 (Rack A)", icon="router", uplink="2x 100GbE to Spines"))
            leaf2 = diag.add(Shape("leaf2", "Leaf Switch 02 (Rack B)", icon="router", uplink="2x 100GbE to Spines"))
            leaf2.below(leaf1, margin=30)
            leaf3 = diag.add(Shape("leaf3", "Leaf Switch 03 (Rack C)", icon="router", uplink="2x 100GbE to Spines"))
            leaf3.below(leaf2, margin=30)

        with diag.group("Server Pods") as g_3:
            pod1 = diag.add(Shape("pod1", "Compute Pod 01", icon="cluster", density="40 Compute Nodes"))
            pod2 = diag.add(Shape("pod2", "Compute Pod 02", icon="cluster", density="40 Compute Nodes"))
            pod2.below(pod1, margin=30)

        # Position starting group
        g_1.at(60.0, 80.0)

        # Arrange groups in horizontal sequence
        g_2.right_of(g_1, margin=50)
        g_3.right_of(g_2, margin=50)

        # Establish inter-element connections with protocol annotations
        leaf1 >> diag.edge("ECMP Route", style="solid") >> spine1
        leaf1 >> diag.edge("ECMP Route", style="solid") >> spine2
        leaf2 >> diag.edge("ECMP Route", style="solid") >> spine1
        leaf2 >> diag.edge("ECMP Route", style="solid") >> spine2
        leaf3 >> diag.edge("ECMP Route", style="solid") >> spine1
        leaf3 >> diag.edge("ECMP Route", style="solid") >> spine2
        pod1 >> diag.edge("TOR Trunk", style="solid") >> leaf1
        pod2 >> diag.edge("TOR Trunk", style="solid") >> leaf2

    # Render outputs after diagram context resolves layout constraints
    diag.render_svg(svg_file)
    diag.render_png(png_file)
    diag.generate_readme("03_leaf_spine_clos_network.svg", readme_file)

    return svg_file


if __name__ == "__main__":
    dest = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("output/datacenter")
    build_diagram(dest)
