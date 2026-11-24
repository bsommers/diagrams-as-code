"""Digital RTL-to-GDSII flow with the open-source tool at each step (SEMICONDUCTOR domain).

Synthesis, physical design and signoff are laid out automatically. The solid
arrows are the forward flow; the dashed arrows are the iteration loops a real
project spends most of its time in: timing closure back to placement, DRC/LVS
fixes back to routing, and area or timing misses back to RTL. Tool names follow
the OpenROAD-flow-scripts reference flow (Yosys, OpenROAD, OpenSTA, KLayout);
commercial flows have the same stages.
"""
from __future__ import annotations

import sys
from pathlib import Path

from diagrams_as_code import Diagram
from diagrams_as_code.output import render_all


def diagram() -> Diagram:
    with Diagram("RTL-to-GDSII Flow (open-source tool names)", theme="paper") as diag:
        X = [50.0 + 235.0 * i for i in range(6)]
        Y0, Y1, Y2, Y3 = 60.0, 200.0, 360.0, 480.0
        W = 165.0
        sdc = diag.shape("Constraints\nSDC (clocks, I/O)", W, icon="document").at(X[1], Y0)
        pdk = diag.shape("PDK / Libraries\nLiberty, LEF, tech", W, icon="database").at(X[2], Y0)
        rtl = diag.shape("RTL\nVerilog / SystemVerilog", W, icon="document").at(X[0], Y1)
        synth = diag.shape("Logic synthesis\nYosys + ABC", W, icon="chip").at(X[1], Y1)
        netlist = diag.shape("Gate-level\nnetlist", W, icon="document").at(X[2], Y1)
        floor = diag.shape("Floorplan\n+ power grid", W, icon="chip").at(X[3], Y1)
        place = diag.shape("Placement\nglobal + detail", W, icon="chip").at(X[4], Y1)
        cts = diag.shape("Clock tree synthesis\nTritonCTS", W, icon="chip").at(X[5], Y1)
        route = diag.shape("Routing\nglobal + detail", W, icon="chip").at(X[5], Y2)
        sta = diag.shape("Timing + power signoff\nOpenSTA, OpenRCX", W, icon="analytics").at(X[3], Y2)
        drc = diag.shape("DRC / LVS\nKLayout, Netgen", W, icon="analytics").at(X[3], Y3)
        gds = diag.shape("GDSII\nto foundry", W, icon="storage").at(X[1], Y2 + 50)

        sdc.anchor("bottom", 0.5) >> diag.edge() >> synth.anchor("top", 0.5)
        pdk.anchor("bottom", 0.3) >> diag.edge() >> synth.anchor("top", 0.9)
        rtl >> diag.edge() >> synth
        synth.anchor("top", 0.08) >> diag.edge("timing miss", style="dashed") >> rtl.anchor("top", 0.5)
        synth >> diag.edge() >> netlist
        netlist >> diag.edge() >> floor
        floor >> diag.edge() >> place
        place >> diag.edge() >> cts
        cts >> diag.edge() >> route
        route.anchor("left", 0.3) >> diag.edge("parasitics") >> sta.anchor("right", 0.3)
        route.anchor("left", 0.8) >> diag.edge("layout") >> drc.anchor("right", 0.75)
        drc.anchor("right", 0.25) >> diag.edge("violations", style="dashed") >> route.anchor("bottom", 0.5)
        sta.anchor("top", 0.5) >> diag.edge("setup/hold ECO", style="dashed") >> place.anchor("bottom", 0.5)
        sta.anchor("left", 0.5) >> diag.edge("closed") >> gds.anchor("right", 0.3)
        drc.anchor("left", 0.5) >> diag.edge("clean") >> gds.anchor("right", 0.8)
        diag.caption("**Figure 1:** RTL to GDSII. Dashed arrows are iteration loops; schematic flow, not a tool-specific script.",
                     small_caps=True)
    return diag


def build_diagram(output_dir: Path | str = "examples/semiconductor") -> Path:
    return render_all(diagram(), output_dir, "01_rtl_to_gdsii_flow")["svg"]


if __name__ == "__main__":
    dest = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("examples/semiconductor")
    build_diagram(dest)
