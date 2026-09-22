"""Example architecture: Auto-Laid-Out Serverless Pipeline (CLOUD domain)."""
from __future__ import annotations

import sys
from pathlib import Path

from diagrams_as_code import Diagram
from diagrams_as_code.output import render_all


def diagram() -> Diagram:
    with Diagram("Auto-Laid-Out Serverless Pipeline", theme="nord", layout="auto") as diag:
        with diag.group("Ingress") as ingress:
            client = diag.shape("Client", icon="mobile")
            gw = diag.shape("API Gateway", icon="api_gateway")
        with diag.group("Compute") as compute:
            fn_a = diag.shape("Order Function", icon="server")
            fn_b = diag.shape("Billing Function", icon="server")
        with diag.group("Data") as data:
            queue = diag.shape("Event Queue", icon="queue")
            db = diag.shape("Orders DB", icon="database")

        client >> diag.edge("HTTPS") >> gw
        gw >> diag.edge("invoke") >> fn_a
        gw >> diag.edge("invoke") >> fn_b
        fn_a >> diag.edge("publish") >> queue
        fn_b >> diag.edge("write") >> db
        queue >> diag.edge("consume") >> fn_b

    return diag


def build_diagram(output_dir: Path | str = "output/cloud") -> Path:
    return render_all(diagram(), output_dir, "11_auto_serverless_pipeline")["svg"]


if __name__ == "__main__":
    dest = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("output/cloud")
    build_diagram(dest)
