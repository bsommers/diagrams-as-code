"""Example architecture: Enterprise Feature Store & MLOps Pipeline (AI domain)."""
from __future__ import annotations

import sys
from pathlib import Path

from diagrams_as_code import Diagram, Edge, Group, Shape


def build_diagram(output_dir: Path | str = "output/ai") -> Path:
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    svg_file = out / "05_feature_store_mlops.svg"
    png_file = out / "05_feature_store_mlops.png"
    readme_file = out / "05_feature_store_mlops_README.md"

    with Diagram("Enterprise Feature Store & MLOps Pipeline", theme="blueprint") as diag:
        with diag.group("Data Ingestion") as g_1:
            stream_in = diag.add(Shape("stream_in", "Streaming Kafka Topics", icon="queue", rate="250,000 evt/s"))
            batch_in = diag.add(Shape("batch_in", "Batch Parquet Dumps", icon="storage", frequency="Hourly ETL"))
            batch_in.below(stream_in, margin=30)

        with diag.group("Feature Engineering") as g_2:
            feast = diag.add(Shape("feast", "Feast Feature Registry", icon="workflow", schema="Protobuf Definitions"))

        with diag.group("Serving Tier") as g_3:
            redis_online = diag.add(Shape("redis_online", "Online Low-Latency Redis", icon="storage", latency="<2ms P99"))
            model_svc = diag.add(Shape("model_svc", "Online Prediction Service", icon="model", framework="Triton Server"))
            model_svc.below(redis_online, margin=30)

        with diag.group("Training Tier") as g_4:
            warehouse = diag.add(Shape("warehouse", "Offline BigQuery Lakehouse", icon="database", retention="3 Years"))

        # Position starting group
        g_1.at(60.0, 80.0)

        # Arrange groups in horizontal sequence
        g_2.right_of(g_1, margin=50)
        g_3.right_of(g_2, margin=50)
        g_4.right_of(g_3, margin=50)

        # Establish inter-element connections with protocol annotations
        stream_in >> diag.edge("Materialize Features", style="solid") >> feast
        batch_in >> diag.edge("Load History", style="solid") >> warehouse
        feast >> diag.edge("Sync Hot Vectors", style="solid") >> redis_online
        model_svc >> diag.edge("Retrieve Entity Vector", style="solid") >> redis_online
        warehouse >> diag.edge("Offline Training Features", style="dashed") >> feast

    # Render outputs after diagram context resolves layout constraints
    diag.render_svg(svg_file)
    diag.render_png(png_file)
    diag.generate_readme("05_feature_store_mlops.svg", readme_file)

    return svg_file


if __name__ == "__main__":
    dest = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("output/ai")
    build_diagram(dest)
