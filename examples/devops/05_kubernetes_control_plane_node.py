"""Example architecture: Kubernetes control plane and worker node anatomy (DEVOPS domain)."""
from __future__ import annotations

import sys
from pathlib import Path

from diagrams_as_code import Diagram, Edge, Group, Shape
from diagrams_as_code.output import render_all


def diagram() -> Diagram:
    with Diagram("Kubernetes Control Plane and Worker Node Anatomy", theme="blueprint") as diag:
        user = diag.add(Shape("user", "Engineer / CI", icon="laptop", client="kubectl, Helm, Argo CD"))

        with diag.group("Control plane") as cp:
            sched = diag.add(Shape("sched", "kube-scheduler", width=190, icon="cluster", job="bind pods to nodes"))
            ctrl = diag.add(Shape("ctrl", "kube-controller-manager", width=190, icon="cluster", job="reconcile desired state"))
            cloud = diag.add(Shape("cloud", "cloud-controller-manager", width=190, icon="cloud", job="LBs, volumes, nodes"))
            api = diag.add(Shape("api", "kube-apiserver", width=170, height=300, icon="api_gateway",
                                 job="REST front door, authN/Z, admission"))
            etcd = diag.add(Shape("etcd", "etcd", width=170, icon="database", job="consistent key-value store"))
            sched.at(30, 75)
            ctrl.at(30, 180)
            cloud.at(30, 285)
            api.at(320, 60)
            etcd.at(320, 420)

        with diag.group("Worker node") as node:
            kubelet = diag.add(Shape("kubelet", "kubelet", icon="server", job="run pods, report status"))
            proxy = diag.add(Shape("proxy", "kube-proxy", icon="router", job="Service rules (iptables / IPVS)"))
            runtime = diag.add(Shape("runtime", "containerd (CRI)", width=170, icon="container", job="pull images, start containers"))
            with diag.group("Pods") as pods:
                pod_a = diag.add(Shape("pod_a", "Pod A\napp + sidecar", width=130, icon="container"))
                pod_b = diag.add(Shape("pod_b", "Pod B\napp", width=130, icon="container"))
                pod_a.at(0, 0)
                pod_b.right_of(pod_a, margin=30)
            kubelet.at(30, 105)
            proxy.at(30, 255)
            runtime.at(320, 95)
            pods.at(300, 300)

        cp.at(40, 160)
        node.at(900, 160)
        user.at(400, 30)

        user >> diag.edge("HTTPS API calls", style="solid", target_port="north") >> api
        api >> diag.edge("gRPC read / write", style="solid", source_port="south", target_port="north") >> etcd
        diag.connect(sched, api.anchor("left", 0.15), label="watch, bind", routing="direct")
        diag.connect(ctrl, api.anchor("left", 0.5), label="watch, update", routing="direct")
        diag.connect(cloud, api.anchor("left", 0.85), label="sync cloud", routing="direct")
        diag.connect(kubelet, api.anchor("right", 0.25), label="watch pods, post status")
        diag.connect(proxy, api.anchor("right", 0.75), label="watch Services", style="dashed")
        kubelet >> diag.edge("CRI gRPC", style="solid") >> runtime
        runtime >> diag.edge("OCI runtime (runc)", style="solid") >> pod_a
        runtime >> diag.edge("", style="solid") >> pod_b
        proxy >> diag.edge("route Service traffic", style="dashed") >> pods

    return diag


def build_diagram(output_dir: Path | str = "examples/devops") -> Path:
    return render_all(diagram(), output_dir, "05_kubernetes_control_plane_node")["svg"]


if __name__ == "__main__":
    dest = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("examples/devops")
    build_diagram(dest)
