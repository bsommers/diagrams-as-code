"""Example architecture: Automotive Plant Flow, Press to Final Assembly (MANUFACTURING domain).

A car body moves through four shops. The press shop stamps panels; the body
shop welds them into a body-in-white (underbody, framing at the geometry
station, then closures); the paint shop pretreats, e-coats, seals and
top-coats it; general assembly fits trim, marries the body to the powertrain
or battery pack, and finishes the car for end-of-line test. Buffers between
the shops (the white-body and painted-body stores) decouple their downtime,
and the painted-body store restores the build sequence that just-in-sequence
suppliers deliver against.
"""
from __future__ import annotations

import sys
from pathlib import Path

from diagrams_as_code import Diagram
from diagrams_as_code.output import render_all

W, H = 150.0, 64.0
COL = [70.0 + i * 220.0 for i in range(5)]
ROW = [140.0, 350.0, 560.0, 750.0]


def diagram() -> Diagram:
    with Diagram("Automotive Plant Flow: Press, Body, Paint, Assembly", theme="emerald") as diag:

        def node(label: str, icon: str, c: int, r: int, **meta: str):
            return diag.shape(label, W, H, icon=icon, metadata=meta).at(COL[c], ROW[r])

        with diag.group("Press Shop"):
            press = node("Tandem Press Line", "robot", 0, 0, output="stamped panels")

        with diag.group("Body Shop (Body-in-White)"):
            underbody = node("Underbody\nWelding", "robot", 1, 0, joining="resistance spot weld")
            framing = node("Framing\nGeo Station", "robot", 2, 0, fixes="body geometry")
            closures = node("Closures &\nRespot", "robot", 3, 0, parts="doors, hood, liftgate")

        wbs = node("White Body\nStore", "queue", 4, 0, role="buffer")

        with diag.group("Paint Shop"):
            ecoat = node("Pretreat &\nE-Coat", "robot", 4, 1, layer="corrosion protection")
            sealer = node("Sealer &\nPrimer", "robot", 3, 1, method="robotic seam seal")
            topcoat = node("Basecoat &\nClearcoat", "robot", 2, 1, booths="robotic bells")
            paint_inspect = node("Paint Inspection", "vision", 1, 1, check="surface defects")

        pbs = node("Painted Body\nStore", "queue", 0, 1, role="resequence to build order")

        with diag.group("General Assembly"):
            trim = node("Trim Line", "user", 0, 2, work="harness, glass, seats")
            marriage = node("Chassis\nMarriage", "robot", 1, 2, joins="body to drivetrain")
            final = node("Final Line", "user", 2, 2, work="fluids, wheels, doors back on")
            eol = node("End-of-Line\nTest", "plc", 3, 2, checks="alignment, rolls, water")

        yard = node("Vehicle Yard", "dashboard", 4, 2, next="ship to dealer")
        jis = node("JIS Supplier\nSeats & Cockpit", "message", 0, 3, delivery="just in sequence")
        powertrain = node("Powertrain /\nBattery Sub-Assy", "robot", 1, 3, variant="ICE or EV")

        press >> diag.edge("panels") >> underbody
        underbody >> diag.edge() >> framing
        framing >> diag.edge() >> closures
        closures >> diag.edge() >> wbs
        wbs >> diag.edge("BIW") >> ecoat
        ecoat >> diag.edge() >> sealer
        sealer >> diag.edge() >> topcoat
        topcoat >> diag.edge() >> paint_inspect
        paint_inspect >> diag.edge() >> pbs
        pbs.anchor("bottom", 0.85) >> diag.edge("sequenced bodies") >> trim.anchor("top", 0.85)
        trim >> diag.edge() >> marriage
        marriage >> diag.edge() >> final
        final >> diag.edge() >> eol
        eol >> diag.edge("pass") >> yard
        jis >> diag.edge("seats") >> trim
        powertrain >> diag.edge("drivetrain") >> marriage

    return diag


def build_diagram(output_dir: Path | str = "output/manufacturing") -> Path:
    return render_all(diagram(), output_dir, "08_automotive_assembly_line")["svg"]


if __name__ == "__main__":
    dest = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("output/manufacturing")
    build_diagram(dest)
