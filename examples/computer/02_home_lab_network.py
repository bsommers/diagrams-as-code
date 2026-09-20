"""Example architecture: Home Lab Self-Hosted Infrastructure (COMPUTER domain)."""
from __future__ import annotations

import sys
from pathlib import Path

from diagrams_as_code import Diagram, Edge, Group, Shape


def build_diagram(output_dir: Path | str = "output/computer") -> Path:
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    svg_file = out / "02_home_lab_network.svg"
    png_file = out / "02_home_lab_network.png"
    readme_file = out / "02_home_lab_network_README.md"

    with Diagram("Home Lab Self-Hosted Infrastructure", theme="blueprint") as diag:
        with diag.group("WAN Demarcation") as g_1:
            ont = diag.add(Shape("ont", "Fiber ONT Internet", icon="router", speed="1 Gbps Symmetrical"))

        with diag.group("Network Core") as g_2:
            opnsense = diag.add(Shape("opnsense", "OPNsense Firewall Router", icon="firewall", hardware="Intel N100 4x2.5GbE"))
            poe_switch = diag.add(Shape("poe_switch", "2.5GbE Managed PoE Switch", icon="router", ports="8-Port PoE+ 2.5G"))
            poe_switch.below(opnsense, margin=30)

        with diag.group("Wireless Mesh") as g_3:
            ap_wifi = diag.add(Shape("ap_wifi", "Wi-Fi 7 Access Point", icon="router", ssids="Trusted, IoT, Guest"))

        with diag.group("Compute & Storage") as g_4:
            truenas = diag.add(Shape("truenas", "TrueNAS SCALE Storage", icon="storage", zpool="4x 16TB ZFS RAIDZ2"))
            proxmox = diag.add(Shape("proxmox", "Proxmox VE Hypervisor", icon="server", vms="Home Assistant, AdGuard, Plex"))
            proxmox.below(truenas, margin=30)

        # Position starting group
        g_1.at(60.0, 80.0)

        # Arrange groups in horizontal sequence
        g_2.right_of(g_1, margin=50)
        g_3.right_of(g_2, margin=50)
        g_4.right_of(g_3, margin=50)

        # Establish inter-element connections with protocol annotations
        ont >> diag.edge("PPPoE 1Gbps", style="solid") >> opnsense
        opnsense >> diag.edge("Trunk VLAN (802.1q)", style="solid") >> poe_switch
        poe_switch >> diag.edge("PoE+ Ethernet", style="solid") >> ap_wifi
        poe_switch >> diag.edge("2.5GbE LAN", style="solid") >> truenas
        poe_switch >> diag.edge("2.5GbE LAN", style="solid") >> proxmox

    # Render outputs after diagram context resolves layout constraints
    diag.render_svg(svg_file)
    diag.render_png(png_file)
    diag.generate_readme("02_home_lab_network.svg", readme_file)

    return svg_file


if __name__ == "__main__":
    dest = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("output/computer")
    build_diagram(dest)
