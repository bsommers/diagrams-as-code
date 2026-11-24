"""Planner-executor agent with a re-planning loop.

A planner LLM turns the goal into an ordered list of steps. An executor runs
the next step with its tools and records the observation. After each step a
check decides whether to continue, finish, or send the observations back to
the planner to revise the remaining steps (the re-planner step of
plan-and-execute agents).
"""
from __future__ import annotations

import sys
from pathlib import Path

from diagrams_as_code import Diagram
from diagrams_as_code.output import render_all


def diagram() -> Diagram:
    with Diagram("Planner-Executor with Re-planning", theme="blueprint") as diag:
        def put(shape, col: int, row: int):
            return shape.at(120 + col * 240, 110 + row * 190, anchor="center")

        goal = put(diag.shape("Goal", icon="user"), 0, 0)
        planner = put(diag.shape("Planner LLM\nwrite step list", icon="brain"), 1, 0)
        plan = put(diag.shape("Plan\nstep 1..n", icon="document"), 2, 0)
        executor = put(diag.shape("Executor\nrun next step", icon="agent"), 3, 0)
        tools = put(diag.shape("Tools\nsearch, code, APIs", icon="terminal"), 4, 0)
        check = put(diag.shape("Step done.\nPlan still valid?", kind="diamond", width=190, height=120), 3, 1)
        answer = put(diag.shape("Final Answer", icon="document"), 3, 2)

        goal >> diag.edge() >> planner
        planner >> diag.edge("emit") >> plan
        plan >> diag.edge("next step") >> executor
        executor >> diag.edge("call") >> tools
        tools >> diag.edge("observation", source_port="south", target_port="east") >> check
        check >> diag.edge("more steps", style="dashed", source_port="north", target_port="south") >> executor
        check >> diag.edge("replan with observations", style="dashed", source_port="west", target_port="south") >> planner
        check >> diag.edge("all steps done", source_port="south", target_port="north") >> answer

    return diag


def build_diagram(output_dir: Path | str = "examples/agentic_dev") -> Path:
    return render_all(diagram(), output_dir, "07_planner_executor_replan")["svg"]


if __name__ == "__main__":
    dest = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("examples/agentic_dev")
    build_diagram(dest)
