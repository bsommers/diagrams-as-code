"""Example architecture: Terraform init, plan and apply with remote state (DEVOPS domain)."""
from __future__ import annotations

import sys
from pathlib import Path

from diagrams_as_code import Diagram, Edge, Group, Shape
from diagrams_as_code.output import render_all


def diagram() -> Diagram:
    with Diagram("Terraform Plan and Apply: Desired State, Recorded State, Real Infrastructure", theme="solarized_light") as diag:
        with diag.group("Desired state (version-controlled)") as inputs:
            config = diag.add(Shape("config", "Configuration .tf", width=170, icon="document", content="resources, modules"))
            tfvars = diag.add(Shape("tfvars", "Variables and tfvars", width=170, icon="key", content="per-environment inputs"))
            config.at(30, 60)
            tfvars.at(30, 170)

        with diag.group("Terraform workflow (CI job or workstation)") as flow:
            init = diag.add(Shape("init", "terraform init", width=150, icon="terminal", does="providers, modules, backend"))
            plan = diag.add(Shape("plan", "terraform plan", width=150, icon="terminal", does="refresh, diff, plan file"))
            review = diag.add(Shape("review", "Plan\nreviewed?", kind="diamond", width=130, height=100))
            apply_ = diag.add(Shape("apply", "terraform apply", width=150, icon="terminal", does="execute saved plan"))
            init.at(30, 60)
            plan.right_of(init, margin=60)
            review.right_of(plan, margin=60)
            apply_.right_of(review, margin=60)

        with diag.group("State") as recorded:
            state = diag.add(Shape("state", "Remote State Backend with state lock (versioned, encrypted)", width=760,
                                   icon="database", lock="held during apply"))
            state.at(30, 60)

        with diag.group("Real world") as world:
            api = diag.add(Shape("api", "Cloud Provider API", width=190, icon="cloud",
                                 auth="short-lived credentials"))
            infra = diag.add(Shape("infra", "Real Infrastructure", width=190, icon="server",
                                   drift="changed outside Terraform"))
            api.at(30, 60)
            infra.below(api, margin=70)
            diag.text("plan also refreshes against the\nAPI with read-only calls", size=11, italic=True).below(
                infra, margin=15)

        inputs.at(40, 60)
        flow.right_of(inputs, margin=70, align="top")
        world.right_of(flow, margin=70, align="top")
        recorded.below(flow, margin=70)

        config >> diag.edge("read", style="solid") >> init
        tfvars >> diag.edge("read", style="solid", target_port="west") >> init
        init >> diag.edge("", style="solid") >> plan
        plan >> diag.edge("tfplan", style="solid") >> review
        review >> diag.edge("approved", style="solid") >> apply_
        review >> diag.edge("changes requested", style="dashed", color="#B03A2E", source_port="north", target_port="north") >> config

        diag.connect(init.anchor("bottom", 0.5), state.anchor("top", 0.1), label="configure backend", style="dashed")
        diag.connect(plan.anchor("bottom", 0.5), state.anchor("top", 0.375), label="read state", style="dashed")
        diag.connect(apply_.anchor("bottom", 0.5), state.anchor("top", 0.9), label="lock, write new state")
        apply_ >> diag.edge("create / update / destroy", style="solid") >> api
        api >> diag.edge("reconcile", style="solid") >> infra

    return diag


def build_diagram(output_dir: Path | str = "examples/devops") -> Path:
    return render_all(diagram(), output_dir, "10_terraform_plan_apply_state")["svg"]


if __name__ == "__main__":
    dest = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("examples/devops")
    build_diagram(dest)
