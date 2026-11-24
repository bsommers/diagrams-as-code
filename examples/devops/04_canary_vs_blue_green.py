"""Example architecture: canary versus blue-green rollout (DEVOPS domain)."""
from __future__ import annotations

import sys
from pathlib import Path

from diagrams_as_code import Diagram, Edge, Group, Shape
from diagrams_as_code.output import render_all


def diagram() -> Diagram:
    with Diagram("Progressive Delivery: Blue-Green Cutover vs Canary Rollout", theme="nord") as diag:
        with diag.group("Blue-green: two full environments, one switch") as bg:
            bg_users = diag.add(Shape("bg_users", "Users", icon="user", traffic="all requests"))
            bg_router = diag.add(Shape("bg_router", "Router / Load Balancer", icon="load_balancer", control="atomic switch"))
            with diag.group("Blue (v1, live)") as blue:
                blue_app = diag.add(Shape("blue_app", "v1 Application Pods", width=190, icon="container", replicas="6"))
            with diag.group("Green (v2, standby)") as green:
                green_app = diag.add(Shape("green_app", "v2 Application Pods", width=190, icon="container", replicas="6"))
            bg_db = diag.add(Shape("bg_db", "Shared Database", icon="database", schema="backward compatible"))
            bg_users.at(30, 60)
            bg_router.at(30, 200)
            blue.at(300, 60)
            green.at(300, 250)
            bg_db.at(600, 195)
            diag.text("Rollback is the same switch,\nflipped back to blue.", size=11, italic=True).at(
                30, 300)

        with diag.group("Canary: a small slice of traffic, promoted by metrics") as cn:
            cn_users = diag.add(Shape("cn_users", "Users", icon="user", traffic="all requests"))
            cn_router = diag.add(Shape("cn_router", "Ingress with Weighted Routing", icon="load_balancer", control="weight per step"))
            with diag.group("Stable ReplicaSet (v1)") as stable:
                stable_app = diag.add(Shape("stable_app", "v1 Pods", width=190, icon="container", replicas="9"))
            with diag.group("Canary ReplicaSet (v2)") as canary:
                canary_app = diag.add(Shape("canary_app", "v2 Pods", width=190, icon="container", replicas="1"))
            analysis = diag.add(Shape("analysis", "Metric Analysis", icon="analytics", slis="error rate, p99 latency"))
            controller = diag.add(Shape("controller", "Rollout Controller", icon="kubernetes", steps="5, 25, 50, 100 percent"))
            cn_users.at(30, 60)
            cn_router.at(30, 200)
            stable.at(300, 60)
            canary.at(300, 250)
            analysis.at(600, 280)
            controller.at(30, 420)

        bg.at(40, 60)
        cn.at(40, 560)

        bg_users >> diag.edge("requests", style="solid") >> bg_router
        bg_router >> diag.edge("100%", style="solid") >> blue_app
        bg_router >> diag.edge("0%, smoke tests only", style="dashed") >> green_app
        blue_app >> diag.edge("SQL", style="solid") >> bg_db
        green_app >> diag.edge("SQL", style="solid") >> bg_db

        cn_users >> diag.edge("requests", style="solid") >> cn_router
        cn_router >> diag.edge("90%", style="solid") >> stable_app
        cn_router >> diag.edge("10%", style="solid", color="#D08770") >> canary_app
        canary_app >> diag.edge("SLI queries", style="dashed") >> analysis
        analysis >> diag.edge("pass / fail", style="solid", source_port="south", target_port="east") >> controller
        controller >> diag.edge("set weight or abort", style="dashed", color="#D08770") >> cn_router

    return diag


def build_diagram(output_dir: Path | str = "examples/devops") -> Path:
    return render_all(diagram(), output_dir, "04_canary_vs_blue_green")["svg"]


if __name__ == "__main__":
    dest = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("examples/devops")
    build_diagram(dest)
