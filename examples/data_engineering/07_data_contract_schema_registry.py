"""A data contract enforced through a schema registry (DATA ENGINEERING domain).

The producing team owns a contract (schema, semantics, owner, SLA) in git.
CI checks every change against the registry's compatibility rule before the
schema is registered. At runtime the producer serializer embeds the schema
ID in each Kafka message (magic byte + 4-byte ID); the consumer looks the ID
up once, caches it, and sends records that fail validation to a dead-letter
topic instead of silently corrupting downstream tables.
"""
from __future__ import annotations

import sys
from pathlib import Path

from diagrams_as_code import Diagram, Style
from diagrams_as_code.output import render_all

DEV = Style(fill="#DCEBFA", font_size=12)
REG = Style(fill="#FBEFCB", font_size=12)
RUN = Style(fill="#FFFFFF", font_size=12)
BAD = Style(fill="#F5C2C2", font_size=12)
ARROW = {"routing": "orthogonal", "width": 1.4}
W, H = 160.0, 56.0


def diagram() -> Diagram:
    with Diagram("Data Contract and Schema Registry Flow", theme="paper") as diag:
        with diag.band("Design time (pull request)", notes=["Breaking changes", "fail before merge."],
                       min_width=980):
            contract = diag.shape("**Contract in git**\norders.v3.yaml, owner, SLA", 230, 76, icon="document", style=DEV).at(60, 90)
            ci = diag.shape("**CI contract check**\nBACKWARD compatible?", 190, H, kind="diamond", style=DEV).at(340, 90)
            reg = diag.shape("**Schema Registry**\nsubject orders-value, v3 = ID 42", 250, 76, icon="vault", style=REG).at(620, 90)
            contract >> diag.edge("PR", **ARROW) >> ci
            ci >> diag.edge("register on merge", **ARROW) >> reg

        with diag.band("Run time (Kafka)", notes=["Every record carries", "a schema ID."], min_width=980):
            prod = diag.shape("Producer\norders-service", W, H, style=RUN).at(60, 390)
            ser = diag.shape("Avro serializer\nwrites magic byte + ID 42", W, H, style=RUN).at(260, 390)
            topic = diag.shape("Topic: orders", 140, H, style=RUN).at(490, 390)
            des = diag.shape("Avro deserializer\ncaches ID 42", W, H, style=RUN).at(700, 390)
            cons = diag.shape("Consumer\nwarehouse sink", W, H, style=RUN).at(920, 390)
            dlq = diag.shape("Dead-letter topic\nschema violations", W, H, style=BAD).at(700, 510)
            prod >> diag.edge(**ARROW) >> ser
            ser >> diag.edge("ID + payload", **ARROW) >> topic
            topic >> diag.edge(**ARROW) >> des
            des >> diag.edge(**ARROW) >> cons
            des >> diag.edge("fails validation", style="dashed", **ARROW) >> dlq

        reg.anchor("bottom", 0.35) >> diag.edge("get ID 42 (first use)", style="dashed", routing="orthogonal", width=1.2) >> des.anchor("top", 0.5)
        ser.anchor("top", 0.5) >> diag.edge("register / look up", style="dashed", routing="orthogonal", width=1.2) >> reg.anchor("bottom", 0.1)
    return diag


def build_diagram(output_dir: Path | str = "examples/data_engineering") -> Path:
    return render_all(diagram(), output_dir, "07_data_contract_schema_registry")["svg"]


if __name__ == "__main__":
    dest = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("examples/data_engineering")
    build_diagram(dest)
