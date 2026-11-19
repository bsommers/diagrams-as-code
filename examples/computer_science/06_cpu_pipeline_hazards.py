"""A five-stage RISC pipeline: the datapath with its hazard units, and a run with forwarding.

The upper panel is the classic IF-ID-EX-MEM-WB datapath with its four pipeline
registers. The hazard detection unit stalls a load-use pair for one cycle; the
forwarding unit feeds results from the EX/MEM and MEM/WB registers straight
back into the ALU. The lower panel runs four dependent instructions through it:
the load forces one bubble, and every other dependence is covered by a
forwarding path (arrows), so four instructions finish in nine cycles.
"""
from __future__ import annotations

import sys
from pathlib import Path

from diagrams_as_code import Diagram, Style
from diagrams_as_code.output import render_all

STAGE_FILL = {"IF": "#F2F2F2", "ID": "#E4E4E8", "EX": "#C9D3E6", "MEM": "#E4E4E8", "WB": "#F2F2F2"}
PROGRAM = [
    ("lw   x1, 0(x2)", {1: "IF", 2: "ID", 3: "EX", 4: "MEM", 5: "WB"}),
    ("add  x3, x1, x4", {2: "IF", 3: "ID", 4: "ID*", 5: "EX", 6: "MEM", 7: "WB"}),
    ("sub  x5, x3, x6", {3: "IF", 4: "IF*", 5: "ID", 6: "EX", 7: "MEM", 8: "WB"}),
    ("and  x7, x5, x3", {5: "IF", 6: "ID", 7: "EX", 8: "MEM", 9: "WB"}),
]
# (producer row, producer cycle, consumer row, x offset in the gap, y offset where it enters)
FORWARDS = [(0, 4, 1, 9, 0), (1, 5, 2, 9, 0), (2, 6, 3, 5, 6), (1, 6, 3, 13, -6)]
FWD = "#1F5FAD"
LINE = {"width": 1.2}
DATA = {"width": 1.4, "color": FWD}
CTRL = {"width": 0.9, "style": "dashed"}

# Datapath geometry.
SX, SW, SH, SY = (60.0, 250.0, 440.0, 630.0, 820.0), 130.0, 64.0, 140.0
REG_W, REG_Y, REG_H = 16.0, 116.0, 112.0
# Pipeline grid geometry.
GX, GY, CW, CH, GAP, PITCH = 250.0, 440.0, 58.0, 30.0, 18.0, 42.0


def diagram() -> Diagram:
    with Diagram("Five-stage pipeline with hazards and forwarding", theme="paper") as diag:
        # ---- (a) datapath
        diag.text("**(a)** Datapath with pipeline registers, hazard detection and forwarding", size=14).at(60, 22)
        labels = ("**IF**\ninstruction fetch", "**ID**\ndecode, read regs", "**EX**\nALU",
                  "**MEM**\ndata memory", "**WB**\nwrite back")
        stages = [diag.shape(label, SW, SH, style=Style(fill=fill, font_size=12)).at(x, SY)
                  for label, x, fill in zip(labels, SX, STAGE_FILL.values())]
        regs = []
        for i, name in enumerate(("IF/ID", "ID/EX", "EX/MEM", "MEM/WB")):
            x = SX[i] + SW + (SX[i + 1] - SX[i] - SW) / 2 - REG_W / 2
            regs.append(diag.shape("", REG_W, REG_H, style=Style(fill="#9FA6B8")).at(x, REG_Y))
            diag.text(name, size=11).at(x + REG_W / 2 + 5, REG_Y - 3, anchor="bottom_left")
        for i in range(4):
            stages[i].anchor("right", 0.5) >> diag.edge(**LINE) >> regs[i].anchor("left", 0.5)
            regs[i].anchor("right", 0.5) >> diag.edge(**LINE) >> stages[i + 1].anchor("left", 0.5)

        # Forwarding data paths over the top, into the ALU.
        ex, top = stages[2], REG_Y - 26
        diag.connect(regs[2].anchor("top", 0.5), ex.anchor("top", 0.75),
                     via=[(SX[3] - 30, top), (SX[2] + 0.75 * SW, top)], **DATA)
        diag.connect(regs[3].anchor("top", 0.5), ex.anchor("top", 0.35),
                     via=[(SX[4] - 30, top - 30), (SX[2] + 0.35 * SW, top - 30)], **DATA)
        diag.text("EX/MEM forward", size=11, color=FWD).at(SX[2] + 0.75 * SW + 8, top - 4, anchor="bottom_left")
        diag.text("MEM/WB forward", size=11, color=FWD).at(SX[3] + 30, top - 34, anchor="bottom_left")

        # Control units below.
        unit_y = SY + SH + 70
        fwd = diag.shape("**Forwarding unit**\n$rs_1, rs_2$ vs. $rd$", 150, 50,
                         style=Style(font_size=12, double=3)).at(SX[2] - 10, unit_y)
        hazard = diag.shape("**Hazard detection**\nload-use check", 150, 50,
                            style=Style(font_size=12, double=3)).at(SX[1] - 10, unit_y)
        fwd.anchor("top", 0.5) >> diag.edge(**CTRL) >> ex.anchor("bottom", 0.5)
        diag.connect(regs[2].anchor("bottom", 0.5), fwd.anchor("right", 0.3),
                     via=[(SX[3] - 30, unit_y + 15)], **CTRL)
        diag.connect(regs[3].anchor("bottom", 0.5), fwd.anchor("right", 0.75),
                     via=[(SX[4] - 30, unit_y + 37.5)], **CTRL)
        diag.connect(regs[1].anchor("bottom", 0.5), hazard.anchor("right", 0.5),
                     via=[(SX[2] - 30, unit_y + 25)], **CTRL)
        diag.connect(hazard.anchor("left", 0.3), regs[0].anchor("bottom", 0.5),
                     via=[(SX[1] - 30, unit_y + 15)], **CTRL)
        diag.connect(hazard.anchor("left", 0.75), stages[0].anchor("bottom", 0.5),
                     via=[(SX[0] + SW / 2, unit_y + 37.5)], **CTRL)
        diag.text("ForwardA/B\nselect", size=11, align="right").at(SX[2] + SW / 2 - 6, SY + SH + 34, anchor="right_center")
        diag.text("hold IF/ID", size=11).at(SX[1] - 30 + 5, SY + SH + 52, anchor="left_center")
        diag.text("hold PC", size=11).at(SX[0] + SW / 2 + 4, SY + SH + 34, anchor="left_center")
        diag.text("MemRead, $rd$", size=11).at(SX[2] - 30 - 5, SY + SH + 34, anchor="right_center")

        # ---- (b) pipeline diagram
        diag.text("**(b)** A load-use stall and four forwarding paths", size=14).at(60, GY - 70)

        def cx(cycle: int) -> float:
            return GX + (cycle - 1) * (CW + GAP)

        def ry(row: int) -> float:
            return GY + row * PITCH

        for cycle in range(1, 10):
            diag.text(f"{cycle}", size=11, color="#555555").at(cx(cycle) + CW / 2, GY - 8, anchor="bottom_center")
        diag.text("clock cycle", size=11, italic=True, color="#555555").at(GX - 14, GY - 8, anchor="bottom_right")
        cells: dict[tuple[int, int], object] = {}
        for row, (instruction, timeline) in enumerate(PROGRAM):
            diag.text(instruction, size=12).at(60, ry(row) + CH / 2, anchor="left_center")
            for cycle, stage in timeline.items():
                if stage.endswith("*"):  # held for a cycle by the stall
                    style = Style(fill="#FFFFFF", dash="4,3", text_color="#666666", font_size=12)
                    text = stage[:-1]
                else:
                    style = Style(fill=STAGE_FILL[stage], font_size=12)
                    text = stage
                cells[(row, cycle)] = diag.shape(text, CW, CH, style=style, fit_label=False).at(cx(cycle), ry(row))

        for prow, pcycle, crow, dx, dy in FORWARDS:
            start = (cx(pcycle) + CW, ry(prow) + CH / 2)
            gx = cx(pcycle) + CW + dx
            end_y = ry(crow) + CH / 2 + dy
            diag.connect(start, (cx(pcycle + 1), end_y), routing="direct",
                         via=[(gx, start[1]), (gx, end_y)], width=1.3, color=FWD, arrow_size=0.7)

        diag.text(
            "Without forwarding, each dependent instruction waits in ID for its producer's WB and the\n"
            "last one retires in cycle 14. With forwarding only the load-use pair stalls, for one cycle:\n"
            "the run ends in cycle 9 instead of 8. Dashed cells are stages held by the stall.",
            size=12, font="serif", italic=True,
        ).at(60, ry(4) + 6)
        diag.caption("**Figure 6:** Five-stage pipeline; dashed lines are control, blue lines carry forwarded "
                     "operands", small_caps=True)
    return diag


def build_diagram(output_dir: Path | str = "examples/computer_science") -> Path:
    return render_all(diagram(), output_dir, "06_cpu_pipeline_hazards")["svg"]


if __name__ == "__main__":
    dest = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("examples/computer_science")
    build_diagram(dest)
