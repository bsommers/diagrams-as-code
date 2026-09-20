"""Example architecture: Simple Retrieval Augmented Generation (RAG) (AI domain)."""
from __future__ import annotations

import sys
from pathlib import Path

from diagrams_as_code import Diagram, Edge, Group, Shape


def build_diagram(output_dir: Path | str = "output/ai") -> Path:
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    svg_file = out / "01_simple_rag_pipeline.svg"
    png_file = out / "01_simple_rag_pipeline.png"
    readme_file = out / "01_simple_rag_pipeline_README.md"

    with Diagram("Simple Retrieval Augmented Generation (RAG)", theme="nord") as diag:
        with diag.group("Interface Tier") as g_1:
            user = diag.add(Shape("user", "User Query Client", icon="user", channel="Chat UI"))

        with diag.group("Vectorization Tier") as g_2:
            embed = diag.add(Shape("embed", "Embedding Model", icon="brain", model="text-embedding-3-small"))

        with diag.group("Search Tier") as g_3:
            vectordb = diag.add(Shape("vectordb", "Milvus Vector DB", icon="vector_db", index="HNSW / Cosine"))
            retriever = diag.add(Shape("retriever", "Context Retriever", icon="workflow", top_k="5 Chunks"))
            retriever.below(vectordb, margin=30)

        with diag.group("Generation Tier") as g_4:
            llm = diag.add(Shape("llm", "Foundation Model LLM", icon="model", model="Claude 3.5 Sonnet"))

        # Position starting group
        g_1.at(60.0, 80.0)

        # Arrange groups in horizontal sequence
        g_2.right_of(g_1, margin=50)
        g_3.right_of(g_2, margin=50)
        g_4.right_of(g_3, margin=50)

        # Establish inter-element connections with protocol annotations
        user >> diag.edge("Input Query", style="solid") >> embed
        embed >> diag.edge("Embedding Vector", style="solid") >> vectordb
        vectordb >> diag.edge("K-NN Neighbors", style="solid") >> retriever
        retriever >> diag.edge("Augmented Prompt", style="solid") >> llm
        llm >> diag.edge("Synthesized Answer", style="dashed") >> user

    # Render outputs after diagram context resolves layout constraints
    diag.render_svg(svg_file)
    diag.render_png(png_file)
    diag.generate_readme("01_simple_rag_pipeline.svg", readme_file)

    return svg_file


if __name__ == "__main__":
    dest = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("output/ai")
    build_diagram(dest)
