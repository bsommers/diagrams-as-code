"""Example architecture: Smart Factory MES & ERP Integration (IIOT domain)."""
from __future__ import annotations

import sys
from pathlib import Path

from diagrams_as_code import Diagram, Edge, Group, Shape
from diagrams_as_code.output import render_all


def diagram() -> Diagram:
    with Diagram("Smart Factory MES & ERP Integration", theme="emerald") as diag:
        with diag.group("Shop Floor") as g_1:
            hmi_station = diag.add(Shape("hmi_station", "Line Operator HMI", icon="hmi", screen="15-inch Touch"))
            barcode_scan = diag.add(Shape("barcode_scan", "Pallet RFID / Barcode", icon="sensor", type="Fixed Mount"))
            barcode_scan.below(hmi_station, margin=30)

        with diag.group("Edge Industrial PC") as g_2:
            ipc_worker = diag.add(Shape("ipc_worker", "IPC Edge Controller", icon="gateway", runtime="Linux IPC"))

        with diag.group("Enterprise ERP") as g_3:
            mes_core = diag.add(Shape("mes_core", "Core MES Server", icon="server", function="OEE & Dispatch"))
            erp_db = diag.add(Shape("erp_db", "SAP ERP Database", icon="database", modules="MM / PP / QM"))
            erp_db.below(mes_core, margin=30)

        # Position starting group
        g_1.at(60.0, 80.0)

        # Arrange groups in horizontal sequence
        g_2.right_of(g_1, margin=80)
        g_3.right_of(g_2, margin=80)

        # Establish inter-element connections with protocol annotations
        hmi_station >> diag.edge("Work Order Start", style="solid") >> ipc_worker
        barcode_scan >> diag.edge("Serial Scan", style="solid") >> ipc_worker
        ipc_worker >> diag.edge("REST API :443", style="solid") >> mes_core
        mes_core >> diag.edge("Batch Sync", style="solid") >> erp_db

    return diag


def build_diagram(output_dir: Path | str = "output/iiot") -> Path:
    return render_all(diagram(), output_dir, "07_smart_factory_mes_integration")["svg"]


if __name__ == "__main__":
    dest = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("output/iiot")
    build_diagram(dest)
