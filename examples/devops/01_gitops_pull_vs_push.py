"""Example architecture: GitOps pull versus push deployment (DEVOPS domain)."""
from __future__ import annotations

import sys
from pathlib import Path

from diagrams_as_code import Diagram, Edge, Group, Shape
from diagrams_as_code.output import render_all


def diagram() -> Diagram:
    with Diagram("GitOps: Push-Based CD vs Pull-Based Reconciliation (Argo CD / Flux)", theme="pastel_light") as diag:
        with diag.group("Push model: the pipeline holds cluster credentials") as push:
            p_dev = diag.add(Shape("p_dev", "Developer", icon="laptop", action="git push"))
            p_repo = diag.add(Shape("p_repo", "App Repository", icon="document", content="source + manifests"))
            p_ci = diag.add(Shape("p_ci", "CI/CD Runner", icon="terminal", steps="build, test, deploy"))
            p_reg = diag.add(Shape("p_reg", "Container Registry", icon="storage", artifact="image:sha"))
            p_cluster = diag.add(Shape("p_cluster", "Production Cluster", icon="kubernetes", api="kube-apiserver"))
            p_dev.at(40, 70)
            p_repo.right_of(p_dev, margin=60)
            p_ci.right_of(p_repo, margin=60)
            p_reg.right_of(p_ci, margin=60)
            p_cluster.below(p_ci, margin=50)
            diag.text("The CI network can reach the cluster API;\ncluster credentials live in the pipeline.",
                      size=11, italic=True).right_of(p_cluster, margin=20)

        with diag.group("Pull model: an in-cluster agent reconciles Git") as pull:
            q_dev = diag.add(Shape("q_dev", "Developer", icon="laptop", action="git push / PR"))
            q_app = diag.add(Shape("q_app", "App Repository", icon="document", content="source code"))
            q_ci = diag.add(Shape("q_ci", "CI Runner", icon="terminal", steps="build, test, scan"))
            q_reg = diag.add(Shape("q_reg", "Container Registry", icon="storage", artifact="image:sha"))
            q_cfg = diag.add(Shape("q_cfg", "Config Repository", icon="document", content="desired state"))
            with diag.group("Production Cluster") as cl:
                q_agent = diag.add(Shape("q_agent", "Argo CD / Flux Controller", icon="shield_check", loop="reconcile 3 min"))
                q_work = diag.add(Shape("q_work", "Workloads", icon="container", state="live state"))
                q_work.at(60, 0)
                q_agent.right_of(q_work, margin=70)
            q_dev.at(40, 70)
            q_app.right_of(q_dev, margin=60)
            q_ci.right_of(q_app, margin=60)
            q_reg.right_of(q_ci, margin=60)
            q_cfg.below(q_ci, margin=50)
            cl.below(q_cfg, margin=45)

        push.at(40, 60)
        pull.at(40, 400)

        p_dev >> diag.edge("commit", style="solid") >> p_repo
        p_repo >> diag.edge("webhook", style="solid") >> p_ci
        p_ci >> diag.edge("push image", style="solid") >> p_reg
        p_ci >> diag.edge("kubectl apply / helm upgrade", style="dashed", color="#B03A2E") >> p_cluster

        q_dev >> diag.edge("commit", style="solid") >> q_app
        q_app >> diag.edge("webhook", style="solid") >> q_ci
        q_ci >> diag.edge("push image", style="solid") >> q_reg
        q_ci >> diag.edge("bump image tag", style="solid") >> q_cfg
        q_agent >> diag.edge("pull + diff", style="dashed", color="#1E8449", source_port="north", target_port="east") >> q_cfg
        q_agent >> diag.edge("apply", style="solid") >> q_work

    return diag


def build_diagram(output_dir: Path | str = "examples/devops") -> Path:
    return render_all(diagram(), output_dir, "01_gitops_pull_vs_push")["svg"]


if __name__ == "__main__":
    dest = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("examples/devops")
    build_diagram(dest)
