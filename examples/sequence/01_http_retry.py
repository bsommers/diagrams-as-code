"""An HTTP request with retries, as a UML sequence diagram.

The client sends a request through a load balancer to an API server, which
reads from a cache and falls back to the database on a miss. A ``loop`` frame
holds the retry policy: each attempt that times out waits $2^k \\cdot 100$ ms
before the next. An ``alt`` frame shows the two outcomes the client can see.
"""
from __future__ import annotations

import sys
from pathlib import Path

from diagrams_as_code import Diagram
from diagrams_as_code.output import render_all
from diagrams_as_code.sequence import SequenceDiagram


def diagram() -> Diagram:
    seq = SequenceDiagram("HTTP request with retry", theme="iiot_light")
    client = seq.participant("Client")
    lb = seq.participant("Load balancer")
    api = seq.participant("API server")
    cache = seq.participant("Cache")
    db = seq.participant("Database", kind="database")

    with seq.loop("attempt $k$ = 0 .. 2, while timed out"):
        seq.message(client, lb, "GET /orders/42", activate=True)
        seq.message(lb, api, "forward", activate=True)
        seq.message(api, cache, "get order:42")
        seq.reply(cache, api, "miss")
        seq.message(api, db, "SELECT * FROM orders WHERE id = 42", activate=True)
        seq.reply(db, api, "row")
        seq.message(api, api, "serialize")
        seq.message(api, cache, "set order:42, ttl 60 s", style="async")
        seq.reply(api, lb, "200 OK")
        seq.note(client, "on timeout: sleep $2^k \\cdot 100$ ms", side="right")
    with seq.alt("response arrived") as outcome:
        seq.reply(lb, client, "200 OK, JSON body", deactivate=False)
        outcome.branch("all attempts timed out")
        seq.reply(lb, client, "504 Gateway Timeout", deactivate=False)
    seq.deactivate(lb)
    diag = seq.build()
    diag.caption("**Figure 1:** a cache-aside read behind a load balancer, retried with exponential backoff",
                 small_caps=True)
    return diag


def build_diagram(output_dir: Path | str = "examples/sequence") -> Path:
    return render_all(diagram(), output_dir, "01_http_retry")["svg"]


if __name__ == "__main__":
    dest = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("examples/sequence")
    build_diagram(dest)
