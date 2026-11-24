"""Exactly-once read-process-write with Kafka transactions (DATA ENGINEERING domain).

A stream task reads a batch from the input topic, writes results to the
output topic and its new consumer offset to __consumer_offsets inside one
transaction. The transaction coordinator logs the decision in
__transaction_state and then writes commit markers to every partition
involved. Consumers using isolation.level=read_committed skip records that
belong to open or aborted transactions, and the producer epoch fences out a
zombie instance with the same transactional.id.
"""
from __future__ import annotations

import sys
from pathlib import Path

from diagrams_as_code import Diagram, Style
from diagrams_as_code.output import render_all

IN = Style(fill="#DCEBFA", font_size=12)
TASK = Style(fill="#FBEFCB", font_size=12)
OUT = Style(fill="#D5EFD9", font_size=12)
COORD = Style(fill="#EDE3F3", font_size=12)
ARROW = {"routing": "orthogonal", "width": 1.4}


def diagram() -> Diagram:
    with Diagram("Exactly-Once Semantics with Transactions and Offsets", theme="paper") as diag:
        inp = diag.shape("**Input topic**\norders, P0\noffsets 100 to 109", 150, 80, icon="queue", style=IN).at(40, 245)
        task = diag.shape("**Stream task**\ntransactional.id = app-1\nproducer epoch 7", 190, 100, icon="workflow", style=TASK).at(280, 235)
        out = diag.shape("**Output topic**\nenriched-orders, P0\nrecords + commit marker", 190, 80, icon="queue", style=OUT).at(620, 60)
        coord = diag.shape("**Transaction coordinator**\nbroker", 190, 70, icon="gateway", style=COORD).at(620, 250)
        state = diag.shape("**__transaction_state**\nPREPARE_COMMIT, COMPLETE", 200, 70, kind="cylinder", style=COORD).at(910, 250)
        offs = diag.shape("**__consumer_offsets**\ngroup g: input P0 = 110", 190, 80, kind="cylinder", style=OUT).at(620, 430)
        down = diag.shape("**Downstream consumer**\nisolation.level = read_committed", 210, 70, icon="server", style=IN).at(910, 65)

        inp >> diag.edge("1  poll", **ARROW) >> task
        task.anchor("top", 0.75) >> diag.edge("2  produce (in txn)", **ARROW) >> out.anchor("left", 0.5)
        task.anchor("bottom", 0.75) >> diag.edge("3  sendOffsetsToTransaction", **ARROW) >> offs.anchor("left", 0.5)
        task.anchor("right", 0.5) >> diag.edge("4  commitTransaction", **ARROW) >> coord.anchor("left", 0.5)
        coord >> diag.edge("5  log decision", **ARROW) >> state
        coord.anchor("top", 0.5) >> diag.edge("6  commit marker", style="dashed", **ARROW) >> out.anchor("bottom", 0.5)
        coord.anchor("bottom", 0.5) >> diag.edge("6  commit marker", style="dashed", **ARROW) >> offs.anchor("top", 0.5)
        out >> diag.edge("7  only committed records", **ARROW) >> down

        diag.text(
            "If the task crashes before step 4, the coordinator aborts the transaction: the output records stay invisible\n"
            "and the offset is not advanced, so the restarted task re-reads 100 to 109 and produces them once.\n"
            "Exactly-once here covers Kafka to Kafka; a side effect outside Kafka needs an idempotent or transactional sink.",
            size=12, line_height=1.4,
        ).at(40, 560)
    return diag


def build_diagram(output_dir: Path | str = "examples/data_engineering") -> Path:
    return render_all(diagram(), output_dir, "09_exactly_once_transactions")["svg"]


if __name__ == "__main__":
    dest = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("examples/data_engineering")
    build_diagram(dest)
