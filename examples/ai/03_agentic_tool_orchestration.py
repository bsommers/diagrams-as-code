"""Example architecture: Autonomous Agent Tool Orchestration (AI domain)."""
from __future__ import annotations

import sys
from pathlib import Path

from diagrams_as_code import Diagram, Edge, Group, Shape


def build_diagram(output_dir: Path | str = "output/ai") -> Path:
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    svg_file = out / "03_agentic_tool_orchestration.svg"
    png_file = out / "03_agentic_tool_orchestration.png"
    readme_file = out / "03_agentic_tool_orchestration_README.md"

    with Diagram("Autonomous Agent Tool Orchestration", theme="dracula") as diag:
        with diag.group("User Tier") as g_1:
            user = diag.add(Shape("user", "Enterprise Operator", icon="user", auth="SSO RBAC"))

        with diag.group("Orchestration Tier") as g_2:
            agent = diag.add(Shape("agent", "Agent Controller", icon="agent", reasoning="ReAct Loop"))

        with diag.group("Tool Execution Tier") as g_3:
            tool_repl = diag.add(Shape("tool_repl", "Python REPL Sandbox", icon="terminal", env="Isolated WASM / gVisor"))
            tool_search = diag.add(Shape("tool_search", "Vector Document Search", icon="vector_db", engine="Qdrant"))
            tool_search.below(tool_repl, margin=30)
            tool_sql = diag.add(Shape("tool_sql", "SQL Analytics Engine", icon="database", engine="DuckDB"))
            tool_sql.below(tool_search, margin=30)

        with diag.group("Memory Tier") as g_4:
            memory = diag.add(Shape("memory", "Conversation Buffer", icon="storage", type="Short-Term / Long-Term"))

        # Position starting group
        g_1.at(60.0, 80.0)

        # Arrange groups in horizontal sequence
        g_2.right_of(g_1, margin=80)
        g_3.right_of(g_2, margin=80)
        g_4.right_of(g_3, margin=80)

        # Establish inter-element connections with protocol annotations
        user >> diag.edge("Task Request", style="solid") >> agent
        agent >> diag.edge("Recall History", style="dashed") >> memory
        agent >> diag.edge("Execute Code", style="solid") >> tool_repl
        agent >> diag.edge("Semantic Lookup", style="solid") >> tool_search
        agent >> diag.edge("Run Query", style="solid") >> tool_sql
        agent >> diag.edge("Verified Plan & Result", style="dashed") >> user

    # Render outputs after diagram context resolves layout constraints
    diag.render_svg(svg_file)
    diag.render_png(png_file)
    diag.generate_readme("03_agentic_tool_orchestration.svg", readme_file)

    return svg_file


if __name__ == "__main__":
    dest = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("output/ai")
    build_diagram(dest)
