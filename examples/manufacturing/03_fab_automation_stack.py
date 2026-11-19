"""Example architecture: 300 mm Fab Automation, MES to AMHS to Tool (MANUFACTURING domain).

The host layer decides what runs where: the MES dispatches lots, the material
control system (MCS) turns moves into AMHS transport jobs, and the equipment
automation program (EAP) drives each tool over SECS/GEM. Overhead hoist
transport (OHT) vehicles carry FOUPs between stockers and tool load ports,
handing off under SEMI E84. Inside the tool the EFEM opens the FOUP and moves
wafers to the chambers, while the equipment controller streams trace data to
fault detection over EDA (Interface A).
"""
from __future__ import annotations

import sys
from pathlib import Path

from diagrams_as_code import Diagram
from diagrams_as_code.output import render_all

COL = [80.0, 340.0, 600.0, 860.0]  # x of each column of shapes
ROW = [120.0, 380.0, 580.0]  # y of each row of shapes
W, H = 160.0, 64.0


def diagram() -> Diagram:
    with Diagram("300 mm Fab Automation: MES to AMHS to Tool", theme="nord") as diag:

        def node(label: str, icon: str, col: int, row: int, **meta: str):
            return diag.shape(label, W, H, icon=icon, metadata=meta).at(COL[col], ROW[row])

        with diag.group("Fab Host Systems (CIM)"):
            mcs = node("Material Control\nSystem (MCS)", "workflow", 0, 0, role="transport orchestration")
            mes = node("MES + Real-Time\nDispatcher", "server", 1, 0, role="lot tracking, what-next")
            eap = node("Equipment Automation\nProgram (EAP)", "gateway", 2, 0, role="tool host")
            fdc = node("FDC / Trace\nData Collector", "analytics", 3, 0, role="fault detection")

        with diag.group("AMHS"):
            stocker = node("FOUP Stocker", "storage_array", 0, 1, capacity="hundreds of FOUPs")
            oht = node("OHT Vehicle\n(ceiling rail)", "queue", 1, 1, payload="1 FOUP, 25 wafers")

        with diag.group("Process Tool"):
            load_port = node("Load Port", "plc", 2, 1, standard="SEMI E15.1 / E87")
            controller = node("Equipment\nController", "plc", 3, 1, interfaces="HSMS, EDA")
            efem = node("EFEM\nWafer Robot", "robot", 2, 2, environment="mini-environment")
            chamber = node("Process\nChambers", "chip", 3, 2, example="etch or CVD")

        mes >> diag.edge("move request") >> mcs
        mes >> diag.edge("lot start, recipe") >> eap
        mcs >> diag.edge("store / retrieve") >> stocker
        mcs.anchor("bottom", 0.8) >> diag.edge("transport job") >> oht.anchor("top", 0.2)
        stocker >> diag.edge("FOUP") >> oht
        oht >> diag.edge("E84 hand-off") >> load_port
        load_port >> diag.edge("E87 dock, open FOUP") >> efem
        efem >> diag.edge("E90 wafer moves") >> chamber
        eap.anchor("bottom", 0.8) >> diag.edge("SECS/GEM (HSMS)") >> controller.anchor("top", 0.2)
        controller >> diag.edge("E40 / E94 jobs") >> chamber
        controller.anchor("top", 0.8) >> diag.edge("EDA / Interface A") >> fdc.anchor("bottom", 0.8)

    return diag


def build_diagram(output_dir: Path | str = "examples/manufacturing") -> Path:
    return render_all(diagram(), output_dir, "03_fab_automation_stack")["svg"]


if __name__ == "__main__":
    dest = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("examples/manufacturing")
    build_diagram(dest)
