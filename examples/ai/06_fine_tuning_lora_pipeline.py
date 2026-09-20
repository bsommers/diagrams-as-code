"""Example architecture: Foundation Model LoRA Fine-Tuning Pipeline (AI domain)."""
from __future__ import annotations

import sys
from pathlib import Path

from iiot_diagrams import Diagram, Edge, Group, Shape


def build_diagram(output_dir: Path | str = "output/ai") -> Path:
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    svg_file = out / "06_fine_tuning_lora_pipeline.svg"
    readme_file = out / "06_fine_tuning_lora_pipeline_README.md"

    with Diagram("Foundation Model LoRA Fine-Tuning Pipeline", theme="crimson") as diag:
        with diag.group("Input Artifacts") as g_1:
            base_model = diag.add(Shape("base_model", "Base Llama-3 70B Weights", icon="model", precision="FP16 Baseline"))
            dataset = diag.add(Shape("dataset", "Curated Instruction Corpus", icon="document", samples="50,000 Verified Q&A"))
            dataset.below(base_model, margin=30)

        with diag.group("Training Compute") as g_2:
            lora_trainer = diag.add(Shape("lora_trainer", "LoRA PEFT Trainer", icon="chip", rank="r=64, alpha=128"))

        with diag.group("Trained Artifacts") as g_3:
            adapter = diag.add(Shape("adapter", "LoRA Adapter Checkpoint", icon="brain", size="320MB SafeTensors"))

        with diag.group("Packaging Tier") as g_4:
            quantizer = diag.add(Shape("quantizer", "AWQ / GGUF Quantizer", icon="workflow", target="4-bit AWQ / Q4_K_M"))
            registry = diag.add(Shape("registry", "Hugging Face Model Registry", icon="storage", status="Production Release"))
            registry.below(quantizer, margin=30)

        # Arrange groups in horizontal sequence
        g_2.right_of(g_1, margin=50)
        g_3.right_of(g_2, margin=50)
        g_4.right_of(g_3, margin=50)

        # Establish inter-element connections with protocol annotations
        base_model >> diag.edge("Load Frozen Weights", style="solid") >> lora_trainer
        dataset >> diag.edge("Instruction Tuning Batch", style="solid") >> lora_trainer
        lora_trainer >> diag.edge("Export Delta Weights", style="solid") >> adapter
        adapter >> diag.edge("Fuse & Quantize", style="solid") >> quantizer
        quantizer >> diag.edge("Register Model Package", style="solid") >> registry

        diag.render_svg(svg_file)
        diag.generate_readme("06_fine_tuning_lora_pipeline.svg", readme_file)

    return svg_file


if __name__ == "__main__":
    dest = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("output/ai")
    build_diagram(dest)
