"""Example architecture: High-Performance Compute Storage Pipeline (COMPUTER domain)."""
from __future__ import annotations

import sys
from pathlib import Path

from iiot_diagrams import Diagram, Edge, Group, Shape


def build_diagram(output_dir: Path | str = "output/computer") -> Path:
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    svg_file = out / "10_high_performance_workstation_storage.svg"
    readme_file = out / "10_high_performance_workstation_storage_README.md"

    with Diagram("High-Performance Compute Storage Pipeline", theme="crimson") as diag:
        with diag.group("Compute Subsystem") as g_1:
            cpu_host = diag.add(Shape("cpu_host", "AMD Threadripper PRO 64-Core", icon="chip", pcie="128 Lanes PCIe Gen5"))
            gpu_accel = diag.add(Shape("gpu_accel", "NVIDIA RTX 6000 Ada GPU", icon="chip", vram="48GB ECC GDDR6"))
            gpu_accel.below(cpu_host, margin=30)

        with diag.group("Storage Subsystem") as g_2:
            nvme_raid = diag.add(Shape("nvme_raid", "4x Micron 9400 Enterprise NVMe", icon="storage_array", bandwidth="28 GB/s Read"))

        with diag.group("Network Subsystem") as g_3:
            nic_100g = diag.add(Shape("nic_100g", "ConnectX-6 100GbE NIC", icon="router", protocol="RoCEv2 RDMA"))
            nvme_over_fabrics = diag.add(Shape("nvme_over_fabrics", "Remote NVMe-oF Target", icon="storage", latency="15 microseconds"))
            nvme_over_fabrics.below(nic_100g, margin=30)

        # Arrange groups in horizontal sequence
        g_2.right_of(g_1, margin=50)
        g_3.right_of(g_2, margin=50)

        # Establish inter-element connections with protocol annotations
        cpu_host >> diag.edge("PCIe 5.0 x16", style="solid") >> gpu_accel
        gpu_accel >> diag.edge("GPUDirect Storage (GDS)", style="solid") >> nvme_raid
        cpu_host >> diag.edge("NVMe Driver", style="dashed") >> nvme_raid
        gpu_accel >> diag.edge("RDMA Direct Pass", style="solid") >> nic_100g
        nic_100g >> diag.edge("100GbE Fiber Link", style="solid") >> nvme_over_fabrics

        diag.render_svg(svg_file)
        diag.generate_readme("10_high_performance_workstation_storage.svg", readme_file)

    return svg_file


if __name__ == "__main__":
    dest = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("output/computer")
    build_diagram(dest)
