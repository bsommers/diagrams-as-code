"""Example architecture: Mobile Offline-First Database Sync (COMPUTER domain)."""
from __future__ import annotations

import sys
from pathlib import Path

from diagrams_as_code import Diagram, Edge, Group, Shape
from diagrams_as_code.output import render_all


def diagram() -> Diagram:
    with Diagram("Mobile Offline-First Database Sync", theme="nord") as diag:
        with diag.group("Mobile Client") as g_1:
            mobile_app = diag.add(Shape("mobile_app", "Field Technician App", icon="mobile", os="iOS / Android React Native"))
            sqlite = diag.add(Shape("sqlite", "Encrypted SQLite DB (SQLCipher)", icon="database", encryption="256-bit AES"))
            sqlite.below(mobile_app, margin=30)
            sync_mgr = diag.add(Shape("sync_mgr", "Background Sync Engine", icon="workflow", strategy="CRDT / Delta Sync"))
            sync_mgr.below(sqlite, margin=30)

        with diag.group("Cloud Endpoint") as g_2:
            ws_gateway = diag.add(Shape("ws_gateway", "WebSocket Sync Gateway", icon="api_gateway", protocol="WSS Secure Sockets"))
            cloud_db = diag.add(Shape("cloud_db", "Master PostgreSQL DB", icon="storage", ha="Multi-Region Read-Write"))
            cloud_db.below(ws_gateway, margin=30)

        # Position starting group
        g_1.at(60.0, 80.0)

        # Arrange groups in horizontal sequence
        g_2.right_of(g_1, margin=80)

        # Establish inter-element connections with protocol annotations
        mobile_app >> diag.edge("Local CRUD Queries", style="solid") >> sqlite
        sqlite >> diag.edge("Queued Mutations", style="dashed") >> sync_mgr
        sync_mgr >> diag.edge("TLS WebSocket Sync", style="solid") >> ws_gateway
        ws_gateway >> diag.edge("Commit Resolved Transactions", style="solid") >> cloud_db

    return diag


def build_diagram(output_dir: Path | str = "output/computer") -> Path:
    return render_all(diagram(), output_dir, "06_mobile_client_sync")["svg"]


if __name__ == "__main__":
    dest = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("output/computer")
    build_diagram(dest)
