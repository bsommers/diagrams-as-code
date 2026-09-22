"""Example architecture: Continuous Deployment & Release Gating (BUSINESS_PROCESS domain)."""
from __future__ import annotations

import sys
from pathlib import Path

from diagrams_as_code import Diagram, Edge, Group, Shape
from diagrams_as_code.output import render_all


def diagram() -> Diagram:
    with Diagram("Continuous Deployment & Release Gating", theme="pastel_light") as diag:
        with diag.group("Engineering") as g_1:
            developer = diag.add(Shape("developer", "Software Engineer", icon="user", git="feature-branch"))
            pr_merge = diag.add(Shape("pr_merge", "Pull Request Peer Review", icon="document", approvals="2 Senior Engineers"))
            pr_merge.below(developer, margin=30)

        with diag.group("Build & Test") as g_2:
            ci_runner = diag.add(Shape("ci_runner", "GitHub Actions CI Pipeline", icon="terminal", matrix="Tests & Linting"))

        with diag.group("Quality Gates") as g_3:
            sast_gate = diag.add(Shape("sast_gate", "SonarQube & Snyk Security Gate", icon="shield", threshold="Zero High Vulnerabilities"))

        with diag.group("Production Rollout") as g_4:
            canary = diag.add(Shape("canary", "Canary Deployment (10%)", icon="server", duration="1 Hour Bake"))
            prod_fleet = diag.add(Shape("prod_fleet", "Full Production Cluster", icon="cluster", traffic="100% Live Users"))
            prod_fleet.below(canary, margin=30)

        # Position starting group
        g_1.at(60.0, 80.0)

        # Arrange groups in horizontal sequence
        g_2.right_of(g_1, margin=80)
        g_3.right_of(g_2, margin=80)
        g_4.right_of(g_3, margin=80)

        # Establish inter-element connections with protocol annotations
        developer >> diag.edge("Open Pull Request", style="solid") >> pr_merge
        pr_merge >> diag.edge("Trigger CI Test Suite", style="solid") >> ci_runner
        ci_runner >> diag.edge("Scan Dependencies & Code", style="solid") >> sast_gate
        sast_gate >> diag.edge("Deploy to Canary", style="solid") >> canary
        canary >> diag.edge("Promote Release", style="solid") >> prod_fleet

    return diag


def build_diagram(output_dir: Path | str = "output/business_process") -> Path:
    return render_all(diagram(), output_dir, "06_software_release_gate")["svg"]


if __name__ == "__main__":
    dest = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("output/business_process")
    build_diagram(dest)
