"""Example architecture: MPLS Layer 3 VPN Service Provider Backbone (NETWORK_ENGINEERING domain)."""
from __future__ import annotations

import sys
from pathlib import Path

from diagrams_as_code import Diagram, Edge, Group, Shape
from diagrams_as_code.output import render_all


def diagram() -> Diagram:
    with Diagram("MPLS Layer 3 VPN Service Provider Backbone", theme="nord") as diag:
        with diag.group("Customer Site Alpha") as g_1:
            ce1 = diag.add(Shape("ce1", "Customer Router Alpha", icon="router", vrf="VRF-Finance"))

        with diag.group("Service Provider MPLS Core") as g_2:
            pe1 = diag.add(Shape("pe1", "Provider Edge 1", icon="mpls", labels="LDP / RSVP-TE"))
            p_core = diag.add(Shape("p_core", "Core Transit LSR", icon="core_router", speed="400Gbps Backbone"))
            p_core.below(pe1, margin=30)
            pe2 = diag.add(Shape("pe2", "Provider Edge 2", icon="mpls", labels="MP-BGP VPNv4"))
            pe2.below(p_core, margin=30)

        with diag.group("Customer Site Beta") as g_3:
            ce2 = diag.add(Shape("ce2", "Customer Router Beta", icon="router", vrf="VRF-Finance"))

        # Position starting group
        g_1.at(60.0, 80.0)

        # Arrange groups in horizontal sequence
        g_2.right_of(g_1, margin=80)
        g_3.right_of(g_2, margin=80)

        # Establish inter-element connections with protocol annotations
        ce1 >> diag.edge("BGP Peering", style="solid") >> pe1
        pe1 >> diag.edge("MPLS Label Push", style="solid") >> p_core
        p_core >> diag.edge("MPLS Label Swap", style="solid") >> pe2
        pe2 >> diag.edge("MPLS Label Pop", style="solid") >> ce2

    return diag


def build_diagram(output_dir: Path | str = "output/network_engineering") -> Path:
    return render_all(diagram(), output_dir, "03_mpls_vpn_backbone")["svg"]


if __name__ == "__main__":
    dest = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("output/network_engineering")
    build_diagram(dest)
