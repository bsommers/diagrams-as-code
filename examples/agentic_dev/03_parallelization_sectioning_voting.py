"""Parallelization, in its two variants from Anthropic's "Building effective agents".

Sectioning splits a task into independent subtasks that run at the same time.
Voting runs the same task several times and aggregates the answers for higher
confidence. Both end in a programmatic aggregator rather than another LLM.
"""
from __future__ import annotations

import sys
from pathlib import Path

from diagrams_as_code import Diagram
from diagrams_as_code.output import render_all


def diagram() -> Diagram:
    with Diagram("Parallelization: Sectioning and Voting", theme="nord", layout="auto", direction="LR") as diag:
        with diag.group("Sectioning: independent subtasks") as sec:
            req1 = diag.shape("Request", icon="user")
            guard = diag.shape("LLM A\nguardrail screen", icon="shield_check")
            answer = diag.shape("LLM B\nanswer the query", icon="model")
            merge1 = diag.shape("Aggregate\nblock or release", icon="workflow")
        with diag.group("Voting: same task, N runs") as vote:
            req2 = diag.shape("Code to review", icon="document")
            v1 = diag.shape("Run 1\nprompt variant A", icon="model")
            v2 = diag.shape("Run 2\nprompt variant B", icon="model")
            v3 = diag.shape("Run 3\nprompt variant C", icon="model")
            merge2 = diag.shape("Aggregate\nmajority / threshold", icon="decision")

        req1 >> diag.edge("task") >> guard
        req1 >> diag.edge("task") >> answer
        guard >> diag.edge("safe?") >> merge1
        answer >> diag.edge("draft") >> merge1

        req2 >> diag.edge() >> v1
        req2 >> diag.edge() >> v2
        req2 >> diag.edge() >> v3
        v1 >> diag.edge("verdict") >> merge2
        v2 >> diag.edge("verdict") >> merge2
        v3 >> diag.edge("verdict") >> merge2

    return diag


def build_diagram(output_dir: Path | str = "examples/agentic_dev") -> Path:
    return render_all(diagram(), output_dir, "03_parallelization_sectioning_voting")["svg"]


if __name__ == "__main__":
    dest = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("examples/agentic_dev")
    build_diagram(dest)
