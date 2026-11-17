"""Mind map: Concept Map of Distributed Consistency (MIND_MAP domain, Advanced).

A concept map in the paper-figure style: black hairlines on white, a
caption, and linking phrases on every line so each edge reads as a
proposition ("Linearizability *implies* Sequential"). Concepts sit on two
computed ellipses around the central idea; size and border weight fall
with distance from it.
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

from diagrams_as_code import Diagram, Style
from diagrams_as_code.output import render_all

CX, CY = 640.0, 290.0
LINE = {"width": 1.0, "routing": "curve", "head": "stealth"}

RING_1 = {
    # concept: bearing in degrees (0 = east, clockwise)
    "Linearizability": -90,
    "Sequential\nConsistency": -25,
    "Causal\nConsistency": 35,
    "Eventual\nConsistency": 95,
    "CAP Theorem": 160,
    "Consensus": 215,
}
RING_2 = {
    # concept: (parent, bearing)
    "Raft": ("Consensus", 201),
    "Paxos": ("Consensus", 187),
    "Vector Clocks": ("Causal\nConsistency", 38),
    "CRDTs": ("Eventual\nConsistency", 100),
    "PACELC": ("CAP Theorem", 162),
}


def _polar(rx: float, ry: float, deg: float) -> tuple[float, float]:
    rad = math.radians(deg)
    return CX + rx * math.cos(rad), CY + ry * math.sin(rad)


def diagram() -> Diagram:
    with Diagram("Distributed Consistency Concept Map", theme="paper") as diag:
        root = diag.shape(
            "**Consistency**\n**Model**", 170, 64,
            style=Style(radius=32, stroke_width=2, double=4, font_size=17),
        ).at(CX, CY, anchor="center")

        ring1 = {}
        for name, bearing in RING_1.items():
            x, y = _polar(330, 230, bearing)
            tall = "\n" in name
            ring1[name] = diag.shape(
                name, 150, 50 if tall else 38, style=Style(radius=19, stroke_width=1.4, font_size=14),
            ).at(x, y, anchor="center")

        ring2 = {}
        for name, (parent, bearing) in RING_2.items():
            x, y = _polar(560, 330, bearing)
            ring2[name] = diag.shape(
                f"*{name}*", 120, 30, style=Style(radius=15, stroke_width=0.8, font_size=13),
            ).at(x, y, anchor="center")

        lin = ring1["Linearizability"]
        seq = ring1["Sequential\nConsistency"]
        causal = ring1["Causal\nConsistency"]
        eventual = ring1["Eventual\nConsistency"]
        cap = ring1["CAP Theorem"]
        consensus = ring1["Consensus"]

        diag.connect(root.anchor("top", 0.5), lin.anchor("bottom", 0.5), label="strongest form", **LINE)
        diag.connect(root.anchor("bottom", 0.5), eventual.anchor("top", 0.5), label="weakest useful form", **LINE)
        diag.connect(lin.anchor("right", 0.5), seq.anchor("top", 0.5), label="implies", **LINE)
        diag.connect(seq.anchor("bottom", 0.5), causal.anchor("top", 0.5), label="implies", **LINE)
        diag.connect(causal.anchor("bottom", 0.5), eventual.anchor("right", 0.5), label="implies", **LINE)
        diag.connect(cap.anchor("right", 0.5), root.anchor("left", 0.5), label="constrains", **LINE)
        diag.connect(consensus.anchor("top", 0.5), lin.anchor("left", 0.5), label="provides", **LINE)

        diag.connect(consensus.anchor("bottom", 0.3), ring2["Paxos"].anchor("right", 0.5), label="e.g.", **LINE)
        diag.connect(consensus.anchor("left", 0.5), ring2["Raft"].anchor("right", 0.5), label="e.g.", **LINE)
        diag.connect(causal.anchor("right", 0.5), ring2["Vector Clocks"].anchor("left", 0.5), label="tracked by", **LINE)
        diag.connect(eventual.anchor("bottom", 0.5), ring2["CRDTs"].anchor("top", 0.5), label="converges via", **LINE)
        diag.connect(cap.anchor("left", 0.5), ring2["PACELC"].anchor("right", 0.5), label="extended by", **LINE)

        diag.caption(
            "**Figure 10:** Consistency models as a concept map; every line reads *concept – phrase → concept*",
            small_caps=True,
        )
    return diag


def build_diagram(output_dir: Path | str = "output/mind_map") -> Path:
    return render_all(diagram(), output_dir, "10_consistency_concept_map")["svg"]


if __name__ == "__main__":
    dest = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("output/mind_map")
    build_diagram(dest)
