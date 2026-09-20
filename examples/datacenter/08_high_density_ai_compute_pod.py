"""Example architecture: High-Density AI Supercomputing Pod (DATACENTER domain)."""
from __future__ import annotations

import sys
from pathlib import Path

from diagrams_as_code import Diagram, Edge, Group, Shape


def build_diagram(output_dir: Path | str = "output/datacenter") -> Path:
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    svg_file = out / "08_high_density_ai_compute_pod.svg"
    png_file = out / "08_high_density_ai_compute_pod.png"
    readme_file = out / "08_high_density_ai_compute_pod_README.md"

    with Diagram("High-Density AI Supercomputing Pod", theme="crimson") as diag:
        with diag.group("SuperPOD Racks") as g_1:
            dgx_rack1 = diag.add(Shape("dgx_rack1", "DGX H100 Rack 01", icon="server_rack", compute="8x H100 SXM5 640GB"))
            dgx_rack2 = diag.add(Shape("dgx_rack2", "DGX H100 Rack 02", icon="server_rack", compute="8x H100 SXM5 640GB"))
            dgx_rack2.below(dgx_rack1, margin=30)

        with diag.group("Fabric Network") as g_2:
            ib_spine = diag.add(Shape("ib_spine", "Quantum-2 InfiniBand Switch", icon="router", speed="NDR 400 Gbps"))
            nvlink_switch = diag.add(Shape("nvlink_switch", "NVLink Network Switch Tray", icon="router", bandwidth="7.2 TB/s Bisection"))
            nvlink_switch.below(ib_spine, margin=30)

        with diag.group("Storage Cluster") as g_3:
            storage_appliance = diag.add(Shape("storage_appliance", "AI Lustre Parallel File Appliance", icon="storage_array", iops="10 Million IOPS"))

        with diag.group("Management") as g_4:
            telemetry_node = diag.add(Shape("telemetry_node", "Cluster Health & Thermal Monitor", icon="dashboard", sensors="Cooling / Leak Detect"))

        # Position starting group
        g_1.at(60.0, 80.0)

        # Arrange groups in horizontal sequence
        g_2.right_of(g_1, margin=80)
        g_3.right_of(g_2, margin=80)
        g_4.right_of(g_3, margin=80)

        # Establish inter-element connections with protocol annotations
        dgx_rack1 >> diag.edge("NVLink 4.0", style="solid") >> nvlink_switch
        dgx_rack2 >> diag.edge("NVLink 4.0", style="solid") >> nvlink_switch
        dgx_rack1 >> diag.edge("8x 400G InfiniBand", style="solid") >> ib_spine
        dgx_rack2 >> diag.edge("8x 400G InfiniBand", style="solid") >> ib_spine
        ib_spine >> diag.edge("RDMA Storage Mount", style="solid") >> storage_appliance
        dgx_rack1 >> diag.edge("IPMI / BMC Telemetry", style="dotted") >> telemetry_node

    # Render outputs after diagram context resolves layout constraints
    diag.render_svg(svg_file)
    diag.render_png(png_file)
    diag.generate_readme("08_high_density_ai_compute_pod.svg", readme_file)

    return svg_file


if __name__ == "__main__":
    dest = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("output/datacenter")
    build_diagram(dest)
