"""Routing workflow, after Anthropic's "Building effective agents".

A classifier LLM call inspects the input once and sends it to exactly one
specialised downstream path, each with its own prompt, tools and model size.
Cheap, common questions go to a small model; hard ones go to a larger one.
"""
from __future__ import annotations

import sys
from pathlib import Path

from diagrams_as_code import Diagram
from diagrams_as_code.output import render_all


def diagram() -> Diagram:
    with Diagram("Routing Workflow", theme="pastel_light", layout="auto", direction="LR") as diag:
        inp = diag.shape("User Request", icon="user")
        router = diag.shape("Router\nLLM classifier", icon="decision")
        general = diag.shape("General Q&A\nsmall, fast model", icon="model")
        refunds = diag.shape("Refund Handler\nprompt + billing tool", icon="workflow")
        tech = diag.shape("Technical Support\nlarge model + docs search", icon="model")
        out = diag.shape("Response", icon="document")

        inp >> diag.edge("input") >> router
        router >> diag.edge() >> general
        router >> diag.edge() >> refunds
        router >> diag.edge() >> tech
        general >> diag.edge() >> out
        refunds >> diag.edge() >> out
        tech >> diag.edge() >> out

    return diag


def build_diagram(output_dir: Path | str = "examples/agentic_dev") -> Path:
    return render_all(diagram(), output_dir, "02_routing_workflow")["svg"]


if __name__ == "__main__":
    dest = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("examples/agentic_dev")
    build_diagram(dest)
