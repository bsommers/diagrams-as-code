"""Example architecture: Auto-Laid-Out Cache-Aside Read and Write Path (DATABASE domain)."""
from __future__ import annotations

import sys
from pathlib import Path

from diagrams_as_code import Diagram
from diagrams_as_code.output import render_all


def diagram() -> Diagram:
    with Diagram("Auto-Laid-Out Cache-Aside Read and Write Path", theme="pastel_light", layout="auto",
                 direction="TB") as diag:
        client = diag.shape("Client")
        api = diag.shape("Product API", icon="api_gateway")
        cache_hit = diag.shape("In Redis?", kind="diamond")
        serve = diag.shape("Serve Cached Row", icon="queue")
        replica = diag.shape("Read Replica", kind="cylinder")
        populate = diag.shape("SET key, TTL 5 min", icon="queue")
        writer = diag.shape("Admin Service", icon="server")
        primary = diag.shape("Primary DB", kind="cylinder")
        cdc = diag.shape("CDC Invalidator", icon="serverless")
        evict = diag.shape("DEL key")

        client >> diag.edge("GET /product") >> api
        api >> diag.edge() >> cache_hit
        cache_hit >> diag.edge("hit") >> serve
        cache_hit >> diag.edge("miss") >> replica
        replica >> diag.edge("row") >> populate
        writer >> diag.edge("UPDATE") >> primary
        primary >> diag.edge("WAL stream") >> replica
        primary >> diag.edge("change events") >> cdc
        cdc >> diag.edge() >> evict

    return diag


def build_diagram(output_dir: Path | str = "output/database") -> Path:
    return render_all(diagram(), output_dir, "11_auto_cache_aside_read_path")["svg"]


if __name__ == "__main__":
    dest = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("output/database")
    build_diagram(dest)
