"""Agentic RAG with query rewriting and a document-grading loop.

Unlike one-shot RAG, the model decides whether to retrieve at all, a grader
checks that the retrieved passages are relevant, and an irrelevant result
triggers a query rewrite and another retrieval (bounded by a retry limit)
before the answer is generated.
"""
from __future__ import annotations

import sys
from pathlib import Path

from diagrams_as_code import Diagram
from diagrams_as_code.output import render_all


def diagram() -> Diagram:
    with Diagram("Agentic RAG: Rewrite and Grade Loop", theme="dracula") as diag:
        def put(shape, col: float, row: float):
            return shape.at(120 + col * 240, 130 + row * 190, anchor="center")

        user = put(diag.shape("User Question", icon="user"), 0, 0)
        decide = put(diag.shape("Agent: retrieve\nor answer directly?", kind="diamond", width=210, height=120), 1, 0)
        retriever = put(diag.shape("Retriever", icon="vector_db"), 2, 0)
        grader = put(diag.shape("Relevance Grader\nLLM judge", kind="diamond", width=210, height=120), 3, 0)
        gen = put(diag.shape("Answer Generator\ngrounded in passages", icon="model", width=160), 4, 0)
        out = put(diag.shape("Answer + citations", icon="document", width=160), 4, 1)
        rewrite = put(diag.shape("Query Rewriter\nLLM", icon="model"), 2.5, 1)

        user >> diag.edge() >> decide
        decide >> diag.edge("needs facts") >> retriever
        retriever >> diag.edge("top-k passages") >> grader
        grader >> diag.edge("relevant") >> gen
        grader >> diag.edge("not relevant", style="dashed", source_port="south", target_port="east") >> rewrite
        rewrite >> diag.edge("new query", style="dashed", source_port="west", target_port="south") >> retriever
        decide >> diag.edge("no retrieval", style="dashed", source_port="north", target_port="north") >> gen
        gen >> diag.edge(source_port="south", target_port="north") >> out

    return diag


def build_diagram(output_dir: Path | str = "examples/agentic_dev") -> Path:
    return render_all(diagram(), output_dir, "08_agentic_rag_grade_loop")["svg"]


if __name__ == "__main__":
    dest = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("examples/agentic_dev")
    build_diagram(dest)
