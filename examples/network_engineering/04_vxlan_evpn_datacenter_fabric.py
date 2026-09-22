"""Example architecture: EVPN-VXLAN Datacenter Spine-Leaf Fabric (NETWORK_ENGINEERING domain)."""
from __future__ import annotations

import sys
from pathlib import Path

from diagrams_as_code import Diagram, Edge, Group, Shape
from diagrams_as_code.output import render_all


def diagram() -> Diagram:
    with Diagram("EVPN-VXLAN Datacenter Spine-Leaf Fabric", theme="nord") as diag:
        with diag.group("Spine Layer (Underlay)") as g_1:
            spine1 = diag.add(Shape("spine1", "Spine Switch 01", icon="switch", speed="400GbE QSFP-DD"))
            spine2 = diag.add(Shape("spine2", "Spine Switch 02", icon="switch", speed="400GbE QSFP-DD"))
            spine2.below(spine1, margin=30)

        with diag.group("Leaf Layer (Overlay VTEPs)") as g_2:
            leaf1 = diag.add(Shape("leaf1", "Leaf 01 (VTEP A)", icon="switch", vni="VXLAN 10010"))
            leaf2 = diag.add(Shape("leaf2", "Leaf 02 (VTEP B)", icon="switch", vni="VXLAN 10020"))
            leaf2.below(leaf1, margin=30)

        with diag.group("Compute Workloads") as g_3:
            host1 = diag.add(Shape("host1", "Compute Host 01", icon="server", lacp="Bond0 Active/Active"))
            host2 = diag.add(Shape("host2", "Compute Host 02", icon="server", lacp="Bond0 Active/Active"))
            host2.below(host1, margin=30)

        # Position starting group
        g_1.at(60.0, 80.0)

        # Arrange groups in horizontal sequence
        g_2.right_of(g_1, margin=80)
        g_3.right_of(g_2, margin=80)

        # Establish inter-element connections with protocol annotations
        spine1 >> diag.edge("100G Underlay", style="solid") >> leaf1
        spine1 >> diag.edge("100G Underlay", style="solid") >> leaf2
        spine2 >> diag.edge("100G Underlay", style="solid") >> leaf1
        spine2 >> diag.edge("100G Underlay", style="solid") >> leaf2
        leaf1 >> diag.edge("25G MLAG", style="solid") >> host1
        leaf2 >> diag.edge("25G MLAG", style="solid") >> host2

    return diag


def build_diagram(output_dir: Path | str = "output/network_engineering") -> Path:
    return render_all(diagram(), output_dir, "04_vxlan_evpn_datacenter_fabric")["svg"]


if __name__ == "__main__":
    dest = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("output/network_engineering")
    build_diagram(dest)
