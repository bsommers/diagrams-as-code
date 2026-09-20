"""Example architecture: High-Availability Active/Passive Firewall Cluster (NETWORK_ENGINEERING domain)."""
from __future__ import annotations

import sys
from pathlib import Path

from diagrams_as_code import Diagram, Edge, Group, Shape


def build_diagram(output_dir: Path | str = "output/network_engineering") -> Path:
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    svg_file = out / "06_ha_firewall_cluster_carp_sync.svg"
    png_file = out / "06_ha_firewall_cluster_carp_sync.png"
    readme_file = out / "06_ha_firewall_cluster_carp_sync_README.md"

    with Diagram("High-Availability Active/Passive Firewall Cluster", theme="crimson") as diag:
        with diag.group("Public Ingress Zone") as g_1:
            wan_sw = diag.add(Shape("wan_sw", "WAN Ingress Switch", icon="switch", vip="198.51.100.1 VIP"))

        with diag.group("HA Cluster Enclave") as g_2:
            fw_pri = diag.add(Shape("fw_pri", "Primary Firewall Node", icon="firewall_ha", role="MASTER (advbase=1)"))
            fw_sec = diag.add(Shape("fw_sec", "Standby Firewall Node", icon="firewall_ha", role="BACKUP (advskew=100)"))
            fw_sec.below(fw_pri, margin=30)
            sync_link = diag.add(Shape("sync_link", "pfsync State Sync", icon="fiber_optic", speed="Dedicated 10GbE"))
            sync_link.below(fw_sec, margin=30)

        with diag.group("Internal Core Fabric") as g_3:
            lan_sw = diag.add(Shape("lan_sw", "Protected LAN Switch", icon="switch", gateway="10.0.0.1 VIP"))

        # Position starting group
        g_1.at(60.0, 80.0)

        # Arrange groups in horizontal sequence
        g_2.right_of(g_1, margin=50)
        g_3.right_of(g_2, margin=50)

        # Establish inter-element connections with protocol annotations
        wan_sw >> diag.edge("Active Ingress", style="solid") >> fw_pri
        wan_sw >> diag.edge("Standby Ingress", style="dashed") >> fw_sec
        fw_pri >> diag.edge("Session States", style="solid") >> sync_link
        sync_link >> diag.edge("Sync Replicate", style="solid") >> fw_sec
        fw_pri >> diag.edge("Active Gateway", style="solid") >> lan_sw
        fw_sec >> diag.edge("Standby Gateway", style="dashed") >> lan_sw

    # Render outputs after diagram context resolves layout constraints
    diag.render_svg(svg_file)
    diag.render_png(png_file)
    diag.generate_readme("06_ha_firewall_cluster_carp_sync.svg", readme_file)

    return svg_file


if __name__ == "__main__":
    dest = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("output/network_engineering")
    build_diagram(dest)
