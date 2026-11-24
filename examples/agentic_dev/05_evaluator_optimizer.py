"""Evaluator-optimizer loop, after Anthropic's "Building effective agents".

One LLM call generates a response; a second call evaluates it against explicit
criteria and returns feedback. The generator revises until the evaluator
accepts or an iteration cap is hit. It pays off when criteria are clear and
feedback measurably improves the result, such as literary translation.
"""
from __future__ import annotations

import sys
from pathlib import Path

from diagrams_as_code import Diagram
from diagrams_as_code.output import render_all


def diagram() -> Diagram:
    with Diagram("Evaluator-Optimizer Loop", theme="solarized_light", layout="auto", direction="LR") as diag:
        task = diag.shape("Task +\nacceptance criteria", icon="user")
        gen = diag.shape("Generator LLM\nproduce or revise", icon="model")
        ev = diag.shape("Evaluator LLM\nscore vs criteria", icon="shield_check")
        ok = diag.shape("Accepted?", kind="diamond", width=150, height=90)
        out = diag.shape("Final Answer", icon="document")
        cap = diag.shape("Iteration cap\nreturn best so far", icon="queue")

        task >> diag.edge() >> gen
        gen >> diag.edge("candidate") >> ev
        ev >> diag.edge("score + critique") >> ok
        ok >> diag.edge("yes") >> out
        ok >> diag.edge("no: feedback", style="dashed", source_port="south", target_port="south") >> gen
        ok >> diag.edge("max rounds", style="dashed") >> cap

    return diag


def build_diagram(output_dir: Path | str = "examples/agentic_dev") -> Path:
    return render_all(diagram(), output_dir, "05_evaluator_optimizer")["svg"]


if __name__ == "__main__":
    dest = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("examples/agentic_dev")
    build_diagram(dest)
