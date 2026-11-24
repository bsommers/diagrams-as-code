"""Example architecture: CI pipeline with quality gates (DEVOPS domain)."""
from __future__ import annotations

import sys
from pathlib import Path

from diagrams_as_code import Diagram, Edge, Group, Shape
from diagrams_as_code.output import render_all


def diagram() -> Diagram:
    with Diagram("Continuous Integration Pipeline with Quality Gates", theme="paper") as diag:
        with diag.group("1 Commit stage") as g_1:
            pr = diag.add(Shape("pr", "Pull Request", icon="document", trigger="push to feature branch"))
            lint = diag.add(Shape("lint", "Lint and Format", icon="terminal", tools="ruff, eslint"))
            unit = diag.add(Shape("unit", "Unit Tests", icon="terminal", budget="under 5 min"))
            lint.below(pr, margin=30)
            unit.below(lint, margin=30)

        with diag.group("2 Build stage") as g_2:
            compile_ = diag.add(Shape("compile", "Compile and Package", icon="server", cache="remote build cache"))
            image = diag.add(Shape("image", "Build Container Image", icon="container", tag="git SHA"))
            image.below(compile_, margin=30)

        with diag.group("3 Verify stage") as g_3:
            integ = diag.add(Shape("integ", "Integration Tests", icon="database", env="ephemeral compose stack"))
            sast = diag.add(Shape("sast", "Static Analysis (SAST)", icon="shield", tools="Semgrep, SonarQube"))
            deps = diag.add(Shape("deps", "Dependency and Image Scan", icon="malware_scan", tools="Trivy, Snyk"))
            sast.below(integ, margin=30)
            deps.below(sast, margin=30)

        with diag.group("4 Quality gates") as g_4:
            gate_cov = diag.add(Shape("gate_cov", "Coverage at least 80%\nand tests green?", kind="diamond", width=190, height=110))
            gate_sec = diag.add(Shape("gate_sec", "No critical CVEs\nor code smells?", kind="diamond", width=190, height=110))
            gate_sec.right_of(gate_cov, margin=60)

        with diag.group("5 Publish") as g_5:
            registry = diag.add(Shape("registry", "Artifact Registry", icon="storage", state="immutable tag"))
            deploy = diag.add(Shape("deploy", "Deploy to Staging", icon="cloud", handoff="CD pipeline"))
            deploy.below(registry, margin=30)

        blocked = diag.add(Shape("blocked", "Merge Blocked\nauthor notified in the PR", icon="lock"))

        g_1.at(40, 70)
        g_2.right_of(g_1, margin=70, align="top")
        g_3.right_of(g_2, margin=70, align="top")
        g_4.below(g_3, margin=60)
        g_5.right_of(g_4, margin=70)
        blocked.below(g_4, margin=50)

        pr >> diag.edge("trigger", style="solid") >> lint
        lint >> diag.edge("pass", style="solid") >> unit
        unit >> diag.edge("pass", style="solid") >> compile_
        compile_ >> diag.edge("artifact", style="solid") >> image
        image >> diag.edge("image", style="solid") >> integ
        integ >> diag.edge("report", style="solid") >> sast
        sast >> diag.edge("report", style="solid") >> deps
        deps >> diag.edge("all reports", style="solid") >> gate_cov
        gate_cov >> diag.edge("yes", style="solid") >> gate_sec
        gate_sec >> diag.edge("yes", style="solid") >> registry
        registry >> diag.edge("promote", style="solid") >> deploy
        gate_cov >> diag.edge("no", style="dashed", color="#B03A2E") >> blocked
        gate_sec >> diag.edge("no", style="dashed", color="#B03A2E") >> blocked

    return diag


def build_diagram(output_dir: Path | str = "examples/devops") -> Path:
    return render_all(diagram(), output_dir, "02_ci_pipeline_quality_gates")["svg"]


if __name__ == "__main__":
    dest = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("examples/devops")
    build_diagram(dest)
