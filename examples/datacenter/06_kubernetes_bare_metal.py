"""Example architecture: Bare-Metal Kubernetes High Availability (DATACENTER domain)."""
from __future__ import annotations

import sys
from pathlib import Path

from diagrams_as_code import Diagram, Edge, Group, Shape


def build_diagram(output_dir: Path | str = "output/datacenter") -> Path:
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    svg_file = out / "06_kubernetes_bare_metal.svg"
    png_file = out / "06_kubernetes_bare_metal.png"
    readme_file = out / "06_kubernetes_bare_metal_README.md"

    with Diagram("Bare-Metal Kubernetes High Availability", theme="emerald") as diag:
        with diag.group("Load Balancers") as g_1:
            vip_lb = diag.add(Shape("vip_lb", "Keepalived / HAProxy VIP", icon="api_gateway", virtual_ip="10.0.0.10:6443"))

        with diag.group("Control Plane") as g_2:
            master1 = diag.add(Shape("master1", "Control Plane 01 (etcd)", icon="server", quorum="Member 1/3"))
            master2 = diag.add(Shape("master2", "Control Plane 02 (etcd)", icon="server", quorum="Member 2/3"))
            master2.below(master1, margin=30)
            master3 = diag.add(Shape("master3", "Control Plane 03 (etcd)", icon="server", quorum="Member 3/3"))
            master3.below(master2, margin=30)

        with diag.group("Worker Nodes") as g_3:
            worker1 = diag.add(Shape("worker1", "Worker Node 01", icon="container", cni="Calico BGP"))
            worker2 = diag.add(Shape("worker2", "Worker Node 02", icon="container", cni="Calico BGP"))
            worker2.below(worker1, margin=30)

        with diag.group("Persistent Storage") as g_4:
            ceph = diag.add(Shape("ceph", "Ceph Rook Distributed CSI", icon="storage_array", type="NVMe Block Pool"))

        # Position starting group
        g_1.at(60.0, 80.0)

        # Arrange groups in horizontal sequence
        g_2.right_of(g_1, margin=50)
        g_3.right_of(g_2, margin=50)
        g_4.right_of(g_3, margin=50)

        # Establish inter-element connections with protocol annotations
        vip_lb >> diag.edge("API Request", style="solid") >> master1
        vip_lb >> diag.edge("API Request", style="solid") >> master2
        master1 >> diag.edge("etcd Raft Consensus", style="dashed") >> master2
        master2 >> diag.edge("etcd Raft Consensus", style="dashed") >> master3
        master1 >> diag.edge("Kubelet Instruction", style="solid") >> worker1
        master1 >> diag.edge("Kubelet Instruction", style="solid") >> worker2
        worker1 >> diag.edge("RBD Mount", style="dashed") >> ceph

    # Render outputs after diagram context resolves layout constraints
    diag.render_svg(svg_file)
    diag.render_png(png_file)
    diag.generate_readme("06_kubernetes_bare_metal.svg", readme_file)

    return svg_file


if __name__ == "__main__":
    dest = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("output/datacenter")
    build_diagram(dest)
