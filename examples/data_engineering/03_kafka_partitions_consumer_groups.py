"""A Kafka topic with partitions and two consumer groups (DATA ENGINEERING domain).

Producers pick a partition from the record key (hash mod partition count),
so all records for one key stay in order. Each partition is an append-only
log of offsets. Inside a consumer group every partition is owned by exactly
one consumer; separate groups read the same partitions independently with
their own committed offsets.
"""
from __future__ import annotations

import sys
from pathlib import Path

from diagrams_as_code import Diagram, Style
from diagrams_as_code.output import render_all

CELL = Style(fill="#FFFFFF", font_size=11)
HEAD = Style(fill="#FBE3A6", font_size=11)
LABEL = Style(fill="#B9C6DC", font_size=12)
A_STYLE = Style(fill="#D5EFD9", font_size=12)
B_STYLE = Style(fill="#DCEBFA", font_size=12)
GREEN, BLUE = "#2E7D4F", "#1E6FB5"
X0, PITCH, CW = 392.0, 40.0, 36.0
ROWS = {0: (120.0, 8), 1: (210.0, 7), 2: (300.0, 8)}   # partition -> (y, record count)
ARROW = {"routing": "direct", "width": 1.4}


def diagram() -> Diagram:
    with Diagram("Kafka Topic, Partitions and Consumer Groups", theme="paper") as diag:
        producer = diag.shape("**Producer**\norders-service", 120, 54, icon="server").at(40, 193)
        part = diag.shape("partitioner\nhash(key) mod 3", 120, 54, style=Style(fill="#E9E9EC", font_size=11)).at(200, 193)
        producer.anchor("right", 0.5) >> diag.edge(**ARROW) >> part.anchor("left", 0.5)

        cells: dict[int, list] = {}
        labels = {}
        with diag.group("Topic: orders (3 partitions, replication factor 3)", padding=18):
            for p, (y, count) in ROWS.items():
                labels[p] = diag.shape(f"**P{p}**", 40, 34, style=LABEL).at(X0 - 50, y)
                cells[p] = []
                for i in range(count):
                    style = HEAD if i == count - 1 else CELL
                    cells[p].append(diag.shape(str(i), CW, 34, style=style, fit_label=False).at(X0 + i * PITCH, y))
        for p in ROWS:
            part.anchor("right", 0.5) >> diag.edge(routing="orthogonal", width=1.4) >> labels[p].anchor("left", 0.5)

        diag.text("**Group analytics**\n2 consumers", size=12).at(880, 28, anchor="left_center")
        diag.text("**Group billing**\n3 consumers", size=12).at(1090, 28, anchor="left_center")
        a1 = diag.shape("A1\nowns P0, P1", 130, 50, style=A_STYLE).at(880, 48)
        a2 = diag.shape("A2\nowns P2", 130, 50, style=A_STYLE).at(880, 360)
        b = [diag.shape(f"B{p}\nowns P{p}", 110, 50, style=B_STYLE).at(1090, y) for p, y in ((0, 112), (1, 202), (2, 292))]
        for p in ROWS:
            diag.connect(cells[p][-1].anchor("right", 0.5), b[p].anchor("left", 0.5), color=BLUE, **ARROW)
        diag.connect(cells[0][-1].anchor("right", 0.5), a1.anchor("left", 0.3), color=GREEN, **ARROW)
        diag.connect(cells[1][-1].anchor("right", 0.5), a1.anchor("left", 0.7), color=GREEN, **ARROW)
        diag.connect(cells[2][-1].anchor("right", 0.5), a2.anchor("left", 0.5), color=GREEN, **ARROW)

        diag.text(
            "Yellow cell = log end offset. Each group stores its own committed offset per partition\n"
            "in __consumer_offsets, so analytics and billing never affect each other.\n"
            "A consumer joining or leaving triggers a rebalance; the member count caps the parallelism at 3.",
            size=12, line_height=1.4,
        ).at(40, 440)
    return diag


def build_diagram(output_dir: Path | str = "examples/data_engineering") -> Path:
    return render_all(diagram(), output_dir, "03_kafka_partitions_consumer_groups")["svg"]


if __name__ == "__main__":
    dest = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("examples/data_engineering")
    build_diagram(dest)
