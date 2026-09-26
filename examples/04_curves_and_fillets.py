#!/usr/bin/env python3
"""Example 04: Curved Bezier Routing and Rounded Corner Fillets.

Demonstrates the v0.8.0 connection routing capabilities:
1. Rounded corner fillets on Manhattan orthogonal edges (corner_radius / arc_radius).
2. Analytical cubic Bezier S-curves with outward normal port handles (Routing.CURVE).
3. Physical arc-length midpoint protocol badge placement.
4. Per-edge corner radius overrides (sharp corners via corner_radius=0.0).
"""
from __future__ import annotations

import sys
from pathlib import Path
from diagrams_as_code import Diagram, Edge, Port, Routing
from diagrams_as_code.output import render_all

OUTPUT_STEM = "curves_and_fillets"


def diagram() -> Diagram:
    diag = Diagram(
        "Architecture Overview: Curves & Fillets",
        width=950,
        height=680,
        theme="iiot_dark_gold",
        corner_radius=16.0,
    )

    with diag:
        ingress = diag.shape("API Gateway", kind="cloud", icon="gateway").at(80.0, 220.0)
        auth = diag.shape("Auth Service", kind="cybersecurity", icon="lock").at(340.0, 360.0)
        analytics = diag.shape("Analytics Engine", kind="ai", icon="server").at(640.0, 360.0)
        db = diag.shape("Primary DB", kind="database", icon="database").at(340.0, 520.0)

        # 1. Rounded orthogonal connection with 90-degree corners (inherits diagram corner_radius=16.0)
        ingress >> diag.edge("HTTPS") >> auth

        # 2. Smooth cubic Bezier feedback loop with protocol label
        diag.connect(
            analytics,
            ingress,
            routing=Routing.CURVE,
            source_port=Port.NORTH,
            target_port=Port.NORTH,
            label="Async Event",
            color="#8B5CF6",
        )

        # 3. Direct orthogonal connection to DB with sharp corner override
        diag.connect(
            auth,
            db,
            routing=Routing.ORTHOGONAL,
            source_port=Port.SOUTH,
            target_port=Port.EAST,
            corner_radius=0.0,
            label="SQL Sync",
        )

    return diag


def generate_curves_and_fillets(output_dir: Path | str = "output") -> Diagram:
    diag = diagram()
    for path in render_all(diag, output_dir, OUTPUT_STEM).values():
        print(f"Generated: {path}")
    return diag


if __name__ == "__main__":
    out_dir = sys.argv[1] if len(sys.argv) > 1 else "output"
    generate_curves_and_fillets(out_dir)
