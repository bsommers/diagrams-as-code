"""Example architecture: Multimodal Vision Inference Pipeline (AI domain)."""
from __future__ import annotations

import sys
from pathlib import Path

from iiot_diagrams import Diagram, Edge, Group, Shape


def build_diagram(output_dir: Path | str = "output/ai") -> Path:
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    svg_file = out / "02_multimodal_vision_inference.svg"
    readme_file = out / "02_multimodal_vision_inference_README.md"

    with Diagram("Multimodal Vision Inference Pipeline", theme="cyber_slate") as diag:
        with diag.group("Perception Tier") as g_1:
            cam = diag.add(Shape("cam", "IP Surveillance Camera", icon="vision", stream="RTSP 4K 60fps"))

        with diag.group("Preprocessing") as g_2:
            sampler = diag.add(Shape("sampler", "Frame Sampler & Decoder", icon="serverless", resolution="1080p 15fps"))

        with diag.group("Inference Tier") as g_3:
            vit = diag.add(Shape("vit", "Vision Transformer (ViT)", icon="brain", backbone="ViT-H/14"))
            yolo = diag.add(Shape("yolo", "YOLO Object Detector", icon="chip", framework="TensorRT"))
            yolo.below(vit, margin=30)

        with diag.group("Notification Tier") as g_4:
            alert = diag.add(Shape("alert", "Alert Event Dispatcher", icon="message", webhook="Enterprise Slack / PagerDuty"))

        # Arrange groups in horizontal sequence
        g_2.right_of(g_1, margin=50)
        g_3.right_of(g_2, margin=50)
        g_4.right_of(g_3, margin=50)

        # Establish inter-element connections with protocol annotations
        cam >> diag.edge("RTSP Feed", style="solid") >> sampler
        sampler >> diag.edge("Normalized Tensors", style="solid") >> vit
        vit >> diag.edge("Feature Embeddings", style="solid") >> yolo
        yolo >> diag.edge("Hazard Detected", style="solid") >> alert

        diag.render_svg(svg_file)
        diag.generate_readme("02_multimodal_vision_inference.svg", readme_file)

    return svg_file


if __name__ == "__main__":
    dest = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("output/ai")
    build_diagram(dest)
