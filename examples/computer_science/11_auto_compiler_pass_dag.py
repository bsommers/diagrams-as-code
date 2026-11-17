"""Example architecture: Auto-Laid-Out Compiler Pass DAG (COMPUTER_SCIENCE domain).

The middle end of an optimising compiler as a pass dependency DAG: analyses
(dominator tree, alias analysis) feed the transforms that need them, and a
pass runs only after every pass it depends on.
No positions are given: the layered layout engine ranks every pass from the
edges alone.
"""
from __future__ import annotations

import sys
from pathlib import Path

from diagrams_as_code import Diagram
from diagrams_as_code.output import render_all


def diagram() -> Diagram:
    with Diagram("Auto-Laid-Out Compiler Pass DAG", theme="dracula", layout="auto", direction="LR") as diag:
        irgen = diag.shape("IR Generator", icon="document")
        mem2reg = diag.shape("SSA Construction\n(mem2reg)")
        domtree = diag.shape("Dominator Tree", icon="analytics")
        alias = diag.shape("Alias Analysis", icon="analytics")
        inliner = diag.shape("Inliner")
        sccp = diag.shape("Sparse Cond.\nConstant Prop.")
        gvn = diag.shape("Global Value\nNumbering")
        licm = diag.shape("Loop-Invariant\nCode Motion")
        dce = diag.shape("Dead Code\nElimination")
        isel = diag.shape("Instruction\nSelection", icon="chip")

        irgen >> diag.edge("IR") >> mem2reg
        mem2reg >> diag.edge() >> inliner
        mem2reg >> diag.edge() >> domtree
        mem2reg >> diag.edge() >> alias
        inliner >> diag.edge() >> sccp
        domtree >> diag.edge() >> gvn
        domtree >> diag.edge() >> licm
        alias >> diag.edge() >> licm
        sccp >> diag.edge() >> dce
        gvn >> diag.edge() >> dce
        licm >> diag.edge() >> dce
        dce >> diag.edge("optimised SSA") >> isel

    return diag


def build_diagram(output_dir: Path | str = "output/computer_science") -> Path:
    return render_all(diagram(), output_dir, "11_auto_compiler_pass_dag")["svg"]


if __name__ == "__main__":
    dest = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("output/computer_science")
    build_diagram(dest)
