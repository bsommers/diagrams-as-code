"""Example architecture: Serverless Event Processing Pipeline (CLOUD domain)."""
from __future__ import annotations

import sys
from pathlib import Path

from iiot_diagrams import Diagram, Edge, Group, Shape


def build_diagram(output_dir: Path | str = "output/cloud") -> Path:
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    svg_file = out / "02_serverless_event_pipeline.svg"
    readme_file = out / "02_serverless_event_pipeline_README.md"

    with Diagram("Serverless Event Processing Pipeline", theme="cyber_slate") as diag:
        with diag.group("Client Tier") as g_1:
            app = diag.add(Shape("app", "Mobile App Client", icon="mobile", sdk="Amplify SDK"))

        with diag.group("Ingress Layer") as g_2:
            apigw = diag.add(Shape("apigw", "REST API Gateway", icon="api_gateway", throttling="10k req/s"))

        with diag.group("Compute Tier") as g_3:
            worker = diag.add(Shape("worker", "Lambda Ingest Worker", icon="serverless", runtime="Python 3.12"))

        with diag.group("Messaging Tier") as g_4:
            queue = diag.add(Shape("queue", "SQS Buffer Queue", icon="queue", retention="14 Days"))

        with diag.group("Data Layer") as g_5:
            dynamo = diag.add(Shape("dynamo", "DynamoDB Real-Time State", icon="storage", billing="On-Demand"))
            s3 = diag.add(Shape("s3", "S3 Archive Lake", icon="storage", tier="Intelligent-Tiering"))
            s3.below(dynamo, margin=30)

        # Arrange groups in horizontal sequence
        g_2.right_of(g_1, margin=50)
        g_3.right_of(g_2, margin=50)
        g_4.right_of(g_3, margin=50)
        g_5.right_of(g_4, margin=50)

        # Establish inter-element connections with protocol annotations
        app >> diag.edge("HTTPS REST", style="solid") >> apigw
        apigw >> diag.edge("Event Dispatch", style="solid") >> worker
        worker >> diag.edge("Enqueue Event", style="solid") >> queue
        queue >> diag.edge("Write State", style="solid") >> dynamo
        queue >> diag.edge("Parquet Dump", style="solid") >> s3

        diag.render_svg(svg_file)
        diag.generate_readme("02_serverless_event_pipeline.svg", readme_file)

    return svg_file


if __name__ == "__main__":
    dest = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("output/cloud")
    build_diagram(dest)
