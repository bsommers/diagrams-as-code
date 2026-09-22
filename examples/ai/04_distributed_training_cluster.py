"""Example architecture: Distributed Multi-GPU Training Cluster (AI domain)."""
from __future__ import annotations

import sys
from pathlib import Path

from diagrams_as_code import Diagram, Edge, Group, Shape
from diagrams_as_code.output import render_all


def diagram() -> Diagram:
    with Diagram("Distributed Multi-GPU Training Cluster", theme="dracula") as diag:
        with diag.group("Coordination") as g_1:
            param_server = diag.add(Shape("param_server", "Parameter Server Coordinator", icon="server", framework="Megatron-LM"))

        with diag.group("GPU Workers") as g_2:
            gpu1 = diag.add(Shape("gpu1", "Worker Node 01 (8x H100)", icon="chip", interconnect="NVLink 900GB/s"))
            gpu2 = diag.add(Shape("gpu2", "Worker Node 02 (8x H100)", icon="chip", interconnect="NVLink 900GB/s"))
            gpu2.below(gpu1, margin=30)
            gpu3 = diag.add(Shape("gpu3", "Worker Node 03 (8x H100)", icon="chip", interconnect="NVLink 900GB/s"))
            gpu3.below(gpu2, margin=30)
            gpu4 = diag.add(Shape("gpu4", "Worker Node 04 (8x H100)", icon="chip", interconnect="NVLink 900GB/s"))
            gpu4.below(gpu3, margin=30)

        with diag.group("Dataset Storage") as g_3:
            lustre = diag.add(Shape("lustre", "Lustre Parallel Storage", icon="storage_array", throughput="2.5 TB/s"))

        # Position starting group
        g_1.at(60.0, 80.0)

        # Arrange groups in horizontal sequence
        g_2.right_of(g_1, margin=80)
        g_3.right_of(g_2, margin=80)

        # Establish inter-element connections with protocol annotations
        param_server >> diag.edge("Broadcast Weights", style="solid") >> gpu1
        param_server >> diag.edge("Broadcast Weights", style="solid") >> gpu2
        param_server >> diag.edge("Broadcast Weights", style="solid") >> gpu3
        param_server >> diag.edge("Broadcast Weights", style="solid") >> gpu4
        gpu1 >> diag.edge("Ring AllReduce", style="dashed") >> gpu2
        gpu2 >> diag.edge("Ring AllReduce", style="dashed") >> gpu3
        gpu3 >> diag.edge("Ring AllReduce", style="dashed") >> gpu4
        lustre >> diag.edge("Sharded Batch Feed", style="solid") >> gpu1

    return diag


def build_diagram(output_dir: Path | str = "output/ai") -> Path:
    return render_all(diagram(), output_dir, "04_distributed_training_cluster")["svg"]


if __name__ == "__main__":
    dest = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("output/ai")
    build_diagram(dest)
