"""Example architecture: Semiconductor Back-End Assembly & Test Line (MANUFACTURING domain).

Sorted wafers leave the fab for assembly and test (OSAT). The wafer is thinned,
mounted on tape and diced; the wafer-sort bin map tells die attach which dies
are good, so failed dies are never packaged. Dies are attached to a lead frame
or substrate strip, wire bonded and transfer molded. The strip is marked,
balled or plated and singulated into units, which are burned in, final tested
on ATE with a handler, and packed into tape and reel. Failing units go to
failure analysis.
"""
from __future__ import annotations

import sys
from pathlib import Path

from diagrams_as_code import Diagram
from diagrams_as_code.output import render_all

W, H = 140.0, 64.0
X0, PITCH, GROUP_GAP = 190.0, 190.0, 60.0
ROW1, ROW2, ROW3 = 230.0, 480.0, 650.0


def col(i: int) -> float:
    """x of column i; the second group of each row starts after a wider gap."""
    return X0 + i * PITCH + (GROUP_GAP if i >= 3 else 0.0)


def diagram() -> Diagram:
    with Diagram("Semiconductor Back-End Assembly & Test Line", theme="solarized_light") as diag:

        def node(label: str, icon: str, i: int, row: float, **meta: str):
            return diag.shape(label, W, H, icon=icon, metadata=meta).at(col(i), row)

        with diag.group("Wafer Preparation"):
            grind = node("Backgrind", "robot", 0, ROW1, target="thin to package height")
            mount = node("Tape Mount", "robot", 1, ROW1, carrier="film frame")
            dice = node("Dicing", "robot", 2, ROW1, method="blade, laser or stealth")

        with diag.group("Assembly"):
            attach = node("Die Attach", "robot", 3, ROW1, material="epoxy or DAF")
            bond = node("Wire Bond", "robot", 4, ROW1, wire="Au or Cu")
            mold = node("Mold & Cure", "robot", 5, ROW1, process="transfer molding")

        with diag.group("Package Finish"):
            mark = node("Laser Mark", "robot", 5, ROW2, content="part, lot, date code")
            ball = node("Ball Attach\nor Plating", "robot", 4, ROW2, finish="solder balls or lead plating")
            singulate = node("Singulation", "robot", 3, ROW2, method="saw or punch")

        with diag.group("Test & Pack"):
            burn_in = node("Burn-In", "plc", 2, ROW2, purpose="screen infant mortality")
            final_test = node("Final Test\nATE + Handler", "chip", 1, ROW2, temps="hot / cold")
            pack = node("Tape & Reel", "queue", 0, ROW2, output="to customer")

        bin_map = diag.shape("Wafer Sort\nBin Map", W, H, icon="database", metadata={"source": "probe"}).at(
            col(3) + 40, ROW1 - 150)
        failure = node("Failure Analysis", "vision", 1, ROW3, tools="X-ray, decap, SEM")

        diag.connect((col(0) - 130, ROW1 + H / 2), grind, routing="direct", label="sorted wafers")
        grind >> diag.edge() >> mount
        mount >> diag.edge() >> dice
        dice >> diag.edge("diced wafer") >> attach
        bin_map.anchor("bottom", 0.5) >> diag.edge("good-die map") >> attach.anchor("top", 0.786)
        attach >> diag.edge() >> bond
        bond >> diag.edge() >> mold
        mold >> diag.edge("molded strip") >> mark
        mark >> diag.edge() >> ball
        ball >> diag.edge() >> singulate
        singulate >> diag.edge("units") >> burn_in
        burn_in >> diag.edge() >> final_test
        final_test >> diag.edge("pass") >> pack
        final_test >> diag.edge("fail bins") >> failure

    return diag


def build_diagram(output_dir: Path | str = "examples/manufacturing") -> Path:
    return render_all(diagram(), output_dir, "06_backend_assembly_test")["svg"]


if __name__ == "__main__":
    dest = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("examples/manufacturing")
    build_diagram(dest)
