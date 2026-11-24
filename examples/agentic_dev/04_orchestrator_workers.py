"""Orchestrator-workers, after Anthropic's "Building effective agents".

Unlike plain parallelization, the subtasks are not fixed in advance. A central
LLM decides at run time which pieces the task needs (for example which files a
change touches), delegates each to a worker, and synthesises their results.
"""
from __future__ import annotations

import sys
from pathlib import Path

from diagrams_as_code import Diagram
from diagrams_as_code.output import render_all


def diagram() -> Diagram:
    with Diagram("Orchestrator-Workers", theme="emerald", layout="auto", direction="LR") as diag:
        task = diag.shape("Task\n\"rename API across repo\"", icon="user")
        orch = diag.shape("Orchestrator LLM\ndecides subtasks at run time", icon="agent", width=190, height=80)
        w1 = diag.shape("Worker 1\nedit file A", icon="model")
        w2 = diag.shape("Worker 2\nedit file B", icon="model")
        w3 = diag.shape("Worker N\nedit file ...", icon="model")
        synth = diag.shape("Synthesizer\nmerge results", icon="workflow")
        out = diag.shape("Combined Result", icon="document")

        task >> diag.edge() >> orch
        orch >> diag.edge("subtask") >> w1
        orch >> diag.edge("subtask") >> w2
        orch >> diag.edge("subtask") >> w3
        w1 >> diag.edge("result") >> synth
        w2 >> diag.edge("result") >> synth
        w3 >> diag.edge("result") >> synth
        synth >> diag.edge() >> out

    return diag


def build_diagram(output_dir: Path | str = "examples/agentic_dev") -> Path:
    return render_all(diagram(), output_dir, "04_orchestrator_workers")["svg"]


if __name__ == "__main__":
    dest = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("examples/agentic_dev")
    build_diagram(dest)
