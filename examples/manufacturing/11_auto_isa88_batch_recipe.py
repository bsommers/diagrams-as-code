"""Example architecture: Auto-Laid-Out ISA-88 Batch Recipe Hierarchy (MANUFACTURING domain).

ISA-88 separates what to make from the equipment that makes it. A general
recipe is narrowed to a site recipe and then to a master recipe for one
process cell; each batch runs a control recipe copied from the master. The
recipe's procedure breaks down into unit procedures, operations and phases,
and each phase is executed by an equipment phase in an equipment module of
the unit. The layered engine places every node from the edges alone.
"""
from __future__ import annotations

import sys
from pathlib import Path

from diagrams_as_code import Diagram
from diagrams_as_code.output import render_all


def diagram() -> Diagram:
    with Diagram("Auto-Laid-Out ISA-88 Batch Recipe Hierarchy", theme="dracula", layout="auto") as diag:
        with diag.group("Recipe Types"):
            general = diag.shape("General Recipe", icon="document")
            site = diag.shape("Site Recipe", icon="document")
            master = diag.shape("Master Recipe", icon="document")
            control = diag.shape("Control Recipe\n(one batch)", icon="document")

        with diag.group("Procedural Control"):
            procedure = diag.shape("Procedure\nMake Batch", icon="workflow")
            unit_proc = diag.shape("Unit Procedure\nReactor R-101", icon="workflow")
            charge = diag.shape("Operation\nCharge", icon="workflow")
            react = diag.shape("Operation\nReact", icon="workflow")
            add = diag.shape("Phase\nAdd Solvent", icon="queue")
            transfer = diag.shape("Operation\nTransfer", icon="workflow")
            heat = diag.shape("Phase\nHeat to Setpoint", icon="queue")
            pump = diag.shape("Phase\nPump to Hold Tank", icon="queue")

        with diag.group("Physical Model"):
            dosing = diag.shape("Equipment Module\nDosing", icon="plc")
            jacket = diag.shape("Equipment Module\nJacket Heating", icon="plc")
            pump_em = diag.shape("Equipment Module\nTransfer Pump", icon="plc")

        general >> diag.edge("localise") >> site
        site >> diag.edge("to cell") >> master
        master >> diag.edge("per batch") >> control
        control >> diag.edge("runs") >> procedure
        procedure >> diag.edge() >> unit_proc
        unit_proc >> diag.edge() >> charge
        unit_proc >> diag.edge() >> react
        unit_proc >> diag.edge() >> transfer
        charge >> diag.edge() >> add
        transfer >> diag.edge() >> pump
        react >> diag.edge() >> heat
        add >> diag.edge("executes on") >> dosing
        heat >> diag.edge("executes on") >> jacket
        pump >> diag.edge("executes on") >> pump_em

    return diag


def build_diagram(output_dir: Path | str = "examples/manufacturing") -> Path:
    return render_all(diagram(), output_dir, "11_auto_isa88_batch_recipe")["svg"]


if __name__ == "__main__":
    dest = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("examples/manufacturing")
    build_diagram(dest)
