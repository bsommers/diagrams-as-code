"""Example architecture: ingress, namespaces and Services in a Kubernetes cluster (DEVOPS domain)."""
from __future__ import annotations

import sys
from pathlib import Path

from diagrams_as_code import Diagram, Edge, Group, Shape
from diagrams_as_code.output import render_all


def diagram() -> Diagram:
    with Diagram("Kubernetes Ingress, Namespace and Service Topology", theme="pastel_light") as diag:
        internet = diag.add(Shape("internet", "Internet Clients", icon="user", host="shop.example.com"))
        dns = diag.add(Shape("dns", "DNS Record", icon="dns", type="A to load balancer"))

        lb = diag.add(Shape("lb", "Cloud Load Balancer", icon="load_balancer", kind="Service type LoadBalancer"))

        with diag.group("Kubernetes cluster") as cluster:
            with diag.group("Namespace: ingress-nginx") as ns_ing:
                ctrl = diag.add(Shape("ctrl", "Ingress Controller Pods", width=180, icon="api_gateway",
                                      reads="Ingress rules, TLS secrets"))

            with diag.group("Namespace: shop") as ns_shop:
                svc_web = diag.add(Shape("svc_web", "Service web (ClusterIP)", width=180, icon="gateway", port="80"))
                web = diag.add(Shape("web", "Deployment web", icon="container", replicas="3"))
                svc_api = diag.add(Shape("svc_api", "Service api (ClusterIP)", width=180, icon="gateway", port="8080"))
                api = diag.add(Shape("api", "Deployment api", icon="container", replicas="4"))
                svc_web.at(30, 60)
                web.at(300, 60)
                svc_api.at(30, 200)
                api.at(300, 200)

            with diag.group("Namespace: payments") as ns_pay:
                svc_pay = diag.add(Shape("svc_pay", "Service payments", width=180, icon="gateway", port="9000"))
                pay = diag.add(Shape("pay", "Deployment payments", icon="container", replicas="2"))
                policy = diag.add(Shape("policy", "NetworkPolicy:\nallow from shop only", width=180, icon="shield",
                                        rule="default deny, allow from shop"))
                svc_pay.at(30, 60)
                pay.at(300, 60)
                policy.at(30, 180)

            with diag.group("Namespace: data") as ns_data:
                svc_db = diag.add(Shape("svc_db", "Headless Service db", width=180, icon="gateway", port="5432"))
                db = diag.add(Shape("db", "StatefulSet db", icon="database", volumes="PVC per pod"))
                svc_db.at(30, 60)
                db.at(300, 60)

        dns.at(40, 60)
        internet.at(40, 170)
        lb.at(40, 280)
        ns_ing.at(300, 220)
        ns_shop.at(640, 80)
        ns_pay.at(1100, 80)
        ns_data.at(1100, 370)

        diag.connect(internet, dns, label="resolve", style="dashed")
        internet >> diag.edge("HTTPS 443", style="solid") >> lb
        lb >> diag.edge("forward", style="solid") >> ctrl
        diag.connect(ctrl, svc_web, label="host shop.example.com, path /", routing="orthogonal")
        diag.connect(ctrl, svc_api, label="path /api", routing="orthogonal")
        svc_web >> diag.edge("selector app=web", style="solid") >> web
        svc_api >> diag.edge("selector app=api", style="solid") >> api
        api >> diag.edge("payments.svc.cluster.local", style="solid") >> svc_pay
        svc_pay >> diag.edge("selector app=payments", style="solid") >> pay
        api >> diag.edge("db.data.svc.cluster.local", style="solid", source_port="south") >> svc_db
        svc_db >> diag.edge("pod DNS", style="solid") >> db

    return diag


def build_diagram(output_dir: Path | str = "examples/devops") -> Path:
    return render_all(diagram(), output_dir, "06_ingress_namespace_service_topology")["svg"]


if __name__ == "__main__":
    dest = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("examples/devops")
    build_diagram(dest)
