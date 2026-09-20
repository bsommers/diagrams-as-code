"""Example architecture: Self-Hosted vLLM Ray Cluster with PagedAttention (AI domain)."""
from __future__ import annotations

import sys
from pathlib import Path

from diagrams_as_code import Diagram, Edge, Group, Shape


def build_diagram(output_dir: Path | str = "output/ai") -> Path:
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    svg_file = out / "10_self_hosted_vllm_cluster.svg"
    png_file = out / "10_self_hosted_vllm_cluster.png"
    readme_file = out / "10_self_hosted_vllm_cluster_README.md"

    with Diagram("Self-Hosted vLLM Ray Cluster with PagedAttention", theme="emerald") as diag:
        with diag.group("Load Balancing") as g_1:
            ingress_lb = diag.add(Shape("ingress_lb", "Traefik Ingress Router", icon="api_gateway", rate_limiting="Token Bucket"))

        with diag.group("Cluster Control") as g_2:
            vllm_router = diag.add(Shape("vllm_router", "vLLM Request Coordinator", icon="workflow", scheduling="Continuous Batching"))
            ray_head = diag.add(Shape("ray_head", "Ray Cluster Head Node", icon="server", nodes="4 Worker Pods"))
            ray_head.below(vllm_router, margin=30)

        with diag.group("Tensor Parallel Workers") as g_3:
            worker1 = diag.add(Shape("worker1", "GPU Pod 01 (8x H100)", icon="chip", tp="TP=8 / FP8 Cache"))
            worker2 = diag.add(Shape("worker2", "GPU Pod 02 (8x H100)", icon="chip", tp="TP=8 / FP8 Cache"))
            worker2.below(worker1, margin=30)

        with diag.group("Memory Management") as g_4:
            kv_cache = diag.add(Shape("kv_cache", "PagedAttention RAM Buffer", icon="storage", allocation="Dynamic Block Pool"))

        with diag.group("Observability") as g_5:
            metrics = diag.add(Shape("metrics", "Prometheus Performance Metrics", icon="dashboard", kpi="Tokens/sec, TTFT, ITL"))

        # Position starting group
        g_1.at(60.0, 80.0)

        # Arrange groups in horizontal sequence
        g_2.right_of(g_1, margin=50)
        g_3.right_of(g_2, margin=50)
        g_4.right_of(g_3, margin=50)
        g_5.right_of(g_4, margin=50)

        # Establish inter-element connections with protocol annotations
        ingress_lb >> diag.edge("OpenAI Compatible /chat", style="solid") >> vllm_router
        vllm_router >> diag.edge("Dispatch Batch", style="solid") >> ray_head
        ray_head >> diag.edge("Tensor Parallel Rank 0-7", style="solid") >> worker1
        ray_head >> diag.edge("Tensor Parallel Rank 8-15", style="solid") >> worker2
        worker1 >> diag.edge("Paged Attention Blocks", style="dashed") >> kv_cache
        worker2 >> diag.edge("Paged Attention Blocks", style="dashed") >> kv_cache
        vllm_router >> diag.edge("Report Latency & TTFT", style="dashed") >> metrics

    # Render outputs after diagram context resolves layout constraints
    diag.render_svg(svg_file)
    diag.render_png(png_file)
    diag.generate_readme("10_self_hosted_vllm_cluster.svg", readme_file)

    return svg_file


if __name__ == "__main__":
    dest = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("output/ai")
    build_diagram(dest)
