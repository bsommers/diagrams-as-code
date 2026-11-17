"""Example architecture: Semiconductor Yield Management Data Flow (MANUFACTURING domain).

Inline metrology, defect inspection with SEM review, scribe-line parametric
test and wafer sort all land in one yield data warehouse, keyed by lot, wafer
and die. Yield analytics look for spatial wafer-map signatures, tool
commonality across low-yield lots, and the kill ratio of each defect class.
An excursion alert reaches the yield engineer, who holds lots or tools
through the MES.
"""
from __future__ import annotations

import sys
from pathlib import Path

from diagrams_as_code import Diagram
from diagrams_as_code.output import render_all

COL = [60.0, 290.0, 520.0, 750.0, 980.0]
W, H = 170.0, 64.0
ROW0, ROW1, ROW2, ROW3 = 130.0, 340.0, 530.0, 690.0
WH_X, WH_W = 60.0, 860.0  # warehouse spans the first four columns


def diagram() -> Diagram:
    with Diagram("Semiconductor Yield Management Data Flow", theme="cyber_slate") as diag:

        def node(label: str, icon: str, col: int, row: float, **meta: str):
            return diag.shape(label, W, H, icon=icon, metadata=meta).at(COL[col], row)

        with diag.group("Fab Inline Data"):
            metrology = node("Inline Metrology", "sensor", 0, ROW0, measures="film thickness, CD")
            inspection = node("Optical Defect\nInspection", "vision", 1, ROW0, mode="bright / dark field")
            review = node("SEM Review + ADC", "vision", 2, ROW0, output="defect class codes")

        with diag.group("Electrical Test"):
            pcm = node("Parametric E-Test\n(scribe line)", "chip", 3, ROW0, structures="PCM test keys")
            sort = node("Wafer Sort\n(probe)", "chip", 4, ROW0, output="die bin map")

        warehouse = diag.shape(
            "Yield Data Warehouse\nlot / wafer / die keyed", WH_W, 80, kind="cylinder", icon="database",
            metadata={"store": "columnar"},
        ).at(WH_X, ROW1)

        with diag.group("Yield Analytics"):
            signature = node("Wafer-Map Spatial\nSignatures", "analytics", 0, ROW2, method="zone / cluster")
            commonality = node("Tool Commonality\nAnalysis", "analytics", 1, ROW2, method="lot history join")
            kill_ratio = node("Defect Kill Ratio\nby Class", "analytics", 2, ROW2, method="defect-to-bin overlay")

        alert = node("Excursion Alert", "message", 3, ROW2, trigger="yield below limit")
        engineer = node("Yield Engineer", "user", 4, ROW2, role="disposition")
        mes = node("MES Lot / Tool Hold", "server", 4, ROW3, action="hold, scrap, rework")

        def into_warehouse(source, col: int, label: str) -> None:
            x = COL[col] + W / 2
            source.anchor("bottom", 0.5) >> diag.edge(label) >> warehouse.anchor("top", (x - WH_X) / WH_W)

        inspection >> diag.edge("defect map") >> review
        into_warehouse(metrology, 0, "measurements")
        into_warehouse(review, 2, "classified defects")
        into_warehouse(pcm, 3, "Vt, Idsat, R")
        sort.anchor("bottom", 0.5) >> diag.edge("bin maps") >> warehouse.anchor("right", 0.5)

        for col, target in enumerate((signature, commonality, kill_ratio)):
            x = COL[col] + 0.8 * W  # clear of the group title
            warehouse.anchor("bottom", (x - WH_X) / WH_W) >> diag.edge() >> target.anchor("top", 0.8)

        diag.fan_in([signature.anchor("bottom", 0.5), commonality.anchor("bottom", 0.5),
                     kill_ratio.anchor("bottom", 0.5)], alert.anchor("bottom", 0.5), trunk=40)
        alert >> diag.edge("notify") >> engineer
        engineer >> diag.edge("disposition") >> mes

    return diag


def build_diagram(output_dir: Path | str = "output/manufacturing") -> Path:
    return render_all(diagram(), output_dir, "05_yield_management")["svg"]


if __name__ == "__main__":
    dest = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("output/manufacturing")
    build_diagram(dest)
