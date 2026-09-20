"""Example architecture: Fibre Channel Storage Area Network (SAN) (DATACENTER domain)."""
from __future__ import annotations

import sys
from pathlib import Path

from iiot_diagrams import Diagram, Edge, Group, Shape


def build_diagram(output_dir: Path | str = "output/datacenter") -> Path:
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    svg_file = out / "02_san_storage_fabric.svg"
    png_file = out / "02_san_storage_fabric.png"
    readme_file = out / "02_san_storage_fabric_README.md"

    with Diagram("Fibre Channel Storage Area Network (SAN)", theme="blueprint") as diag:
        with diag.group("Compute Hosts") as g_1:
            host_app = diag.add(Shape("host_app", "Enterprise Application Host", icon="server", hba="Dual 32G FC HBAs"))

        with diag.group("Fabric A") as g_2:
            fc_switch_a = diag.add(Shape("fc_switch_a", "Brocade 32G FC Switch A", icon="router", zone="Storage Zone A"))

        with diag.group("Fabric B") as g_3:
            fc_switch_b = diag.add(Shape("fc_switch_b", "Brocade 32G FC Switch B", icon="router", zone="Storage Zone B"))

        with diag.group("Storage Array") as g_4:
            ctrl_a = diag.add(Shape("ctrl_a", "Storage Controller A", icon="storage_array", cache="128GB Mirrored"))
            ctrl_b = diag.add(Shape("ctrl_b", "Storage Controller B", icon="storage_array", cache="128GB Mirrored"))
            ctrl_b.below(ctrl_a, margin=30)
            disk_shelf = diag.add(Shape("disk_shelf", "24x NVMe SSD Drive Shelf", icon="storage", capacity="153 TB Raw"))
            disk_shelf.below(ctrl_b, margin=30)

        # Arrange groups in horizontal sequence
        g_2.right_of(g_1, margin=50)
        g_3.right_of(g_2, margin=50)
        g_4.right_of(g_3, margin=50)

        # Establish inter-element connections with protocol annotations
        host_app >> diag.edge("32G FC Link", style="solid") >> fc_switch_a
        host_app >> diag.edge("32G FC Link", style="dashed") >> fc_switch_b
        fc_switch_a >> diag.edge("Target Port A1", style="solid") >> ctrl_a
        fc_switch_b >> diag.edge("Target Port B1", style="dashed") >> ctrl_b
        ctrl_a >> diag.edge("SAS-4 24G Loop", style="solid") >> disk_shelf
        ctrl_b >> diag.edge("SAS-4 24G Loop", style="dashed") >> disk_shelf

        diag.render_svg(svg_file)
        diag.render_png(png_file)
        diag.generate_readme("02_san_storage_fabric.svg", readme_file)

    return svg_file


if __name__ == "__main__":
    dest = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("output/datacenter")
    build_diagram(dest)
