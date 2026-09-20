"""Example architecture: Enterprise Cloud Data Lakehouse Ingest (CLOUD domain)."""
from __future__ import annotations

import sys
from pathlib import Path

from iiot_diagrams import Diagram, Edge, Group, Shape


def build_diagram(output_dir: Path | str = "output/cloud") -> Path:
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    svg_file = out / "07_data_lakehouse_ingest.svg"
    png_file = out / "07_data_lakehouse_ingest.png"
    readme_file = out / "07_data_lakehouse_ingest_README.md"

    with Diagram("Enterprise Cloud Data Lakehouse Ingest", theme="monochrome") as diag:
        with diag.group("Data Sources") as g_1:
            producers = diag.add(Shape("producers", "Event Producers", icon="mobile", protocol="HTTPS Webhooks"))

        with diag.group("Ingest Layer") as g_2:
            kinesis = diag.add(Shape("kinesis", "Amazon Kinesis Stream", icon="queue", shards="16 Shards"))
            firehose = diag.add(Shape("firehose", "Kinesis Data Firehose", icon="serverless", buffer="5MB/300s"))
            firehose.below(kinesis, margin=30)

        with diag.group("Lakehouse Tier") as g_3:
            s3_raw = diag.add(Shape("s3_raw", "S3 Raw Bucket", icon="storage", format="JSON Gzip"))
            s3_curated = diag.add(Shape("s3_curated", "S3 Curated Lake", icon="storage", format="Snappy Parquet"))
            s3_curated.below(s3_raw, margin=30)

        with diag.group("Governance Tier") as g_4:
            glue = diag.add(Shape("glue", "AWS Glue Metastore", icon="workflow", catalog="Iceberg"))

        with diag.group("Analytics Tier") as g_5:
            athena = diag.add(Shape("athena", "Athena Serverless SQL", icon="terminal", engine="Trino SQL"))

        # Arrange groups in horizontal sequence
        g_2.right_of(g_1, margin=50)
        g_3.right_of(g_2, margin=50)
        g_4.right_of(g_3, margin=50)
        g_5.right_of(g_4, margin=50)

        # Establish inter-element connections with protocol annotations
        producers >> diag.edge("Stream Push", style="solid") >> kinesis
        kinesis >> diag.edge("Buffer Batch", style="solid") >> firehose
        firehose >> diag.edge("Object Put", style="solid") >> s3_raw
        s3_raw >> diag.edge("Crawl Schema", style="dashed") >> glue
        glue >> diag.edge("ETL Transform", style="solid") >> s3_curated
        athena >> diag.edge("Direct SQL", style="solid") >> s3_curated

        diag.render_svg(svg_file)
        diag.render_png(png_file)
        diag.generate_readme("07_data_lakehouse_ingest.svg", readme_file)

    return svg_file


if __name__ == "__main__":
    dest = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("output/cloud")
    build_diagram(dest)
