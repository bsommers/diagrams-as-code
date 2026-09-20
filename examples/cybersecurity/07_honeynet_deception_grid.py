"""Example architecture: Deception Technology Honeynet Grid (CYBERSECURITY domain)."""
from __future__ import annotations

import sys
from pathlib import Path

from diagrams_as_code import Diagram, Edge, Group, Shape


def build_diagram(output_dir: Path | str = "output/cybersecurity") -> Path:
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    svg_file = out / "07_honeynet_deception_grid.svg"
    png_file = out / "07_honeynet_deception_grid.png"
    readme_file = out / "07_honeynet_deception_grid_README.md"

    with Diagram("Deception Technology Honeynet Grid", theme="cyber_slate") as diag:
        with diag.group("Attacker Vector") as g_1:
            adversary = diag.add(Shape("adversary", "Adversary Terminal", icon="terminal", origin="Compromised Node"))

        with diag.group("Decoy VLAN Subnet") as g_2:
            decoy_ssh = diag.add(Shape("decoy_ssh", "Decoy SSH Bastion", icon="honeypot", service="OpenSSH 8.2 Decoy"))
            decoy_web = diag.add(Shape("decoy_web", "Decoy Admin Portal", icon="honeypot", service="Fake Jenkins UI"))
            decoy_web.below(decoy_ssh, margin=30)
            decoy_db = diag.add(Shape("decoy_db", "Honeytoken SQL DB", icon="honeypot", data="Canary Records"))
            decoy_db.below(decoy_web, margin=30)

        with diag.group("Deception Controller") as g_3:
            honey_siem = diag.add(Shape("honey_siem", "Deception Telemetry", icon="siem", analysis="Session Recording"))

        with diag.group("Automated Defense") as g_4:
            blackhole = diag.add(Shape("blackhole", "BGP Flowspec Sinkhole", icon="lock", action="Null-Route IP"))

        # Position starting group
        g_1.at(60.0, 80.0)

        # Arrange groups in horizontal sequence
        g_2.right_of(g_1, margin=80)
        g_3.right_of(g_2, margin=80)
        g_4.right_of(g_3, margin=80)

        # Establish inter-element connections with protocol annotations
        adversary >> diag.edge("Brute Force Attempt", style="solid") >> decoy_ssh
        adversary >> diag.edge("HTTP Exploit Attempt", style="solid") >> decoy_web
        adversary >> diag.edge("SQL Injection", style="solid") >> decoy_db
        decoy_ssh >> diag.edge("Session PCAP", style="solid") >> honey_siem
        decoy_web >> diag.edge("Payload Dump", style="solid") >> honey_siem
        decoy_db >> diag.edge("Honeytoken Tripwire", style="solid") >> honey_siem
        honey_siem >> diag.edge("Trigger Block", style="solid") >> blackhole

    # Render outputs after diagram context resolves layout constraints
    diag.render_svg(svg_file)
    diag.render_png(png_file)
    diag.generate_readme("07_honeynet_deception_grid.svg", readme_file)

    return svg_file


if __name__ == "__main__":
    dest = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("output/cybersecurity")
    build_diagram(dest)
