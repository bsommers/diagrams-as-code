"""Example architecture: GraphRAG & Knowledge Graph Augmented LLM (AI domain)."""
from __future__ import annotations

import sys
from pathlib import Path

from diagrams_as_code import Diagram, Edge, Group, Shape


def build_diagram(output_dir: Path | str = "output/ai") -> Path:
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    svg_file = out / "07_enterprise_knowledge_graph_llm.svg"
    png_file = out / "07_enterprise_knowledge_graph_llm.png"
    readme_file = out / "07_enterprise_knowledge_graph_llm_README.md"

    with Diagram("GraphRAG & Knowledge Graph Augmented LLM", theme="pastel_light") as diag:
        with diag.group("Source Corpus") as g_1:
            raw_corpus = diag.add(Shape("raw_corpus", "Unstructured PDF / Confluence", icon="document", volume="100,000 Documents"))

        with diag.group("Graph Construction") as g_2:
            extractor = diag.add(Shape("extractor", "Entity/Relation Extractor", icon="brain", model="GPT-4o NER"))

        with diag.group("Graph Store") as g_3:
            neo4j = diag.add(Shape("neo4j", "Neo4j Knowledge Graph", icon="database", nodes="2M Entities, 8M Edges"))

        with diag.group("Query Layer") as g_4:
            graph_retriever = diag.add(Shape("graph_retriever", "Multi-Hop Cypher Retriever", icon="workflow", hops="3-Hop Expansion"))
            synth_llm = diag.add(Shape("synth_llm", "Synthesis LLM Engine", icon="model", prompt="Graph Context Injected"))
            synth_llm.below(graph_retriever, margin=30)

        with diag.group("End Consumer") as g_5:
            analyst = diag.add(Shape("analyst", "Intelligence Analyst", icon="user", role="Investigative Research"))

        # Position starting group
        g_1.at(60.0, 80.0)

        # Arrange groups in horizontal sequence
        g_2.right_of(g_1, margin=80)
        g_3.right_of(g_2, margin=80)
        g_4.right_of(g_3, margin=80)
        g_5.right_of(g_4, margin=80)

        # Establish inter-element connections with protocol annotations
        raw_corpus >> diag.edge("Document Chunks", style="solid") >> extractor
        extractor >> diag.edge("Merge Cypher Triples", style="solid") >> neo4j
        analyst >> diag.edge("Natural Language Query", style="solid") >> graph_retriever
        graph_retriever >> diag.edge("Execute Graph Traversal", style="solid") >> neo4j
        graph_retriever >> diag.edge("Sub-graph Context", style="solid") >> synth_llm
        synth_llm >> diag.edge("Grounded Graph Synthesis", style="dashed") >> analyst

    # Render outputs after diagram context resolves layout constraints
    diag.render_svg(svg_file)
    diag.render_png(png_file)
    diag.generate_readme("07_enterprise_knowledge_graph_llm.svg", readme_file)

    return svg_file


if __name__ == "__main__":
    dest = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("output/ai")
    build_diagram(dest)
