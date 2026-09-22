"""Example architecture: Inline IDS/IPS Deep Packet Inspection (CYBERSECURITY domain)."""
from __future__ import annotations

import sys
from pathlib import Path

from diagrams_as_code import Diagram, Edge, Group, Shape
from diagrams_as_code.output import render_all


def diagram() -> Diagram:
    with Diagram("Inline IDS/IPS Deep Packet Inspection", theme="cyber_slate") as diag:
        with diag.group("Perimeter Ingress") as g_1:
            border_rtr = diag.add(Shape("border_rtr", "Border Transit Router", icon="core_router", bandwidth="100 Gbps"))

        with diag.group("Inspection Network") as g_2:
            npb = diag.add(Shape("npb", "Packet Broker TAP", icon="switch", mode="Hardware Bypass"))
            decryptor = diag.add(Shape("decryptor", "SSL/TLS Decryptor", icon="key", hardware="ASIC Accelerator"))
            decryptor.below(npb, margin=30)
            suricata_ips = diag.add(Shape("suricata_ips", "Suricata IPS Cluster", icon="malware_scan", engine="Inline Drop Mode"))
            suricata_ips.below(decryptor, margin=30)

        with diag.group("Internal Core Fabric") as g_3:
            core_sw = diag.add(Shape("core_sw", "Campus Core Switch", icon="switch", segment="Clean Corporate LAN"))

        # Position starting group
        g_1.at(60.0, 80.0)

        # Arrange groups in horizontal sequence
        g_2.right_of(g_1, margin=80)
        g_3.right_of(g_2, margin=80)

        # Establish inter-element connections with protocol annotations
        border_rtr >> diag.edge("Raw Ingress", style="solid") >> npb
        npb >> diag.edge("Encrypted Copy", style="solid") >> decryptor
        decryptor >> diag.edge("Decrypted Stream", style="solid") >> suricata_ips
        suricata_ips >> diag.edge("Scrubbed Flow", style="solid") >> npb
        npb >> diag.edge("Permitted Packets", style="solid") >> core_sw

    return diag


def build_diagram(output_dir: Path | str = "output/cybersecurity") -> Path:
    return render_all(diagram(), output_dir, "08_ids_ips_inline_inspection")["svg"]


if __name__ == "__main__":
    dest = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("output/cybersecurity")
    build_diagram(dest)
