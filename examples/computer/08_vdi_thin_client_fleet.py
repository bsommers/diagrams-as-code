"""Example architecture: Enterprise Virtual Desktop Infrastructure (VDI) (COMPUTER domain)."""
from __future__ import annotations

import sys
from pathlib import Path

from diagrams_as_code import Diagram, Edge, Group, Shape
from diagrams_as_code.output import render_all


def diagram() -> Diagram:
    with Diagram("Enterprise Virtual Desktop Infrastructure (VDI)", theme="monochrome") as diag:
        with diag.group("Office Floor") as g_1:
            thin1 = diag.add(Shape("thin1", "Dell Wyse Thin Client 01", icon="laptop", os="ThinOS"))
            thin2 = diag.add(Shape("thin2", "Dell Wyse Thin Client 02", icon="laptop", os="ThinOS"))
            thin2.below(thin1, margin=30)

        with diag.group("Control Plane") as g_2:
            broker = diag.add(Shape("broker", "VDI Connection Broker", icon="api_gateway", auth="MFA RADIUS"))
            ad_dc = diag.add(Shape("ad_dc", "Active Directory Domain Controller", icon="server", domain="corp.internal"))
            ad_dc.below(broker, margin=30)

        with diag.group("Virtual Desktop Farm") as g_3:
            esxi_cluster = diag.add(Shape("esxi_cluster", "VMware ESXi Compute Cluster", icon="cluster", hosts="6x Dual Xeon Servers"))
            san_storage = diag.add(Shape("san_storage", "All-Flash SAN Storage", icon="storage_array", latency="0.2ms IOPS"))
            san_storage.below(esxi_cluster, margin=30)

        # Position starting group
        g_1.at(60.0, 80.0)

        # Arrange groups in horizontal sequence
        g_2.right_of(g_1, margin=80)
        g_3.right_of(g_2, margin=80)

        # Establish inter-element connections with protocol annotations
        thin1 >> diag.edge("Blast Extreme :443", style="solid") >> broker
        thin2 >> diag.edge("Blast Extreme :443", style="solid") >> broker
        broker >> diag.edge("Kerberos Ticket", style="dashed") >> ad_dc
        broker >> diag.edge("Allocate VM Session", style="solid") >> esxi_cluster
        esxi_cluster >> diag.edge("VMDK Disk I/O", style="solid") >> san_storage

    return diag


def build_diagram(output_dir: Path | str = "output/computer") -> Path:
    return render_all(diagram(), output_dir, "08_vdi_thin_client_fleet")["svg"]


if __name__ == "__main__":
    dest = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("output/computer")
    build_diagram(dest)
