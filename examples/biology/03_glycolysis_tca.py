"""Glycolysis feeding the TCA (Krebs) cycle, with ATP, NADH and FADH2 tallied per glucose.

Glycolysis spends 2 ATP and makes 4 (net 2) and 2 NADH. Pyruvate dehydrogenase turns each pyruvate into
acetyl-CoA (1 NADH, 1 CO2). Each turn of the cycle makes 3 NADH, 1 FADH2, 1 GTP (counted as ATP) and
2 CO2, and runs twice per glucose. Totals per glucose: 4 ATP (substrate level), 10 NADH, 2 FADH2, 6 CO2.
At about 2.5 ATP per NADH and 1.5 per FADH2 that is roughly 32 ATP once oxidative phosphorylation is added.
"""
import math
import sys
from pathlib import Path

from diagrams_as_code import Diagram, Style
from diagrams_as_code.output import render_all

INK = "#1F2F57"
RED, BLUE, GREEN, GREY = "#B03A3A", "#2F5FA8", "#2E6B3F", "#666666"
SUGAR = Style(fill="#F4E9C8", stroke=INK, stroke_width=1.4, radius=6)
ACID = Style(fill="#DCE6F2", stroke=INK, stroke_width=1.4, radius=6)
HEAD = Style(fill="#1F2F57", stroke=INK, stroke_width=1.0, text_color="#FFFFFF")
CELL = Style(fill="#FFFFFF", stroke="#8A93A8", stroke_width=1.0)
TOTAL = Style(fill="#E9F2E1", stroke="#8A93A8", stroke_width=1.0)

# (box label, enzyme, tally text, tally colour) for the arrow leaving each box.
GLYCOLYSIS = [
    ("Glucose", "hexokinase", "-1 ATP", RED),
    ("Glucose 6-phosphate", "phosphoglucose isomerase", "", RED),
    ("Fructose 6-phosphate", "phosphofructokinase-1", "-1 ATP", RED),
    ("Fructose 1,6-bisphosphate", "aldolase + triose-P isomerase", "", RED),
    ("2 x Glyceraldehyde 3-P", "GAPDH", "+2 NADH", BLUE),
    ("2 x 1,3-Bisphosphoglycerate", "phosphoglycerate kinase", "+2 ATP", RED),
    ("2 x 3-Phosphoglycerate", "phosphoglycerate mutase", "", RED),
    ("2 x 2-Phosphoglycerate", "enolase (loses H2O)", "", RED),
    ("2 x Phosphoenolpyruvate", "pyruvate kinase", "+2 ATP", RED),
    ("2 x Pyruvate", "pyruvate dehydrogenase", "+2 NADH, 2 CO2", BLUE),
]
CYCLE = ["Citrate", "Isocitrate", "alpha-Ketoglutarate", "Succinyl-CoA", "Succinate", "Fumarate", "Malate", "Oxaloacetate"]
# Tally on the step leaving each intermediate: (text, colour).
CYCLE_TALLY = {
    "Isocitrate": ("NADH + CO2", BLUE),
    "alpha-Ketoglutarate": ("NADH + CO2", BLUE),
    "Succinyl-CoA": ("GTP (ATP)", RED),
    "Succinate": ("FADH2", GREEN),
    "Malate": ("NADH", BLUE),
}
GX, GY0, GDY = 170.0, 92.0, 46.0
CX, CY, RX, RY = 900.0, 300.0, 230.0, 150.0
BW, BH = 150.0, 28.0


def diagram() -> Diagram:
    with Diagram("Glycolysis and the TCA cycle", theme="paper") as diag:
        diag.text("**Glycolysis** (cytosol)", size=14).at(GX, GY0 - 38, anchor="bottom_center")
        boxes = []
        for i, (name, enz, tally, colour) in enumerate(GLYCOLYSIS):
            y = GY0 + i * GDY
            style = SUGAR if i < 4 else ACID
            boxes.append(diag.shape(name, 190, BH, style=style, fit_label=False).at(GX, y, anchor="center"))
        for i, (name, enz, tally, colour) in enumerate(GLYCOLYSIS):
            y = GY0 + i * GDY + GDY / 2
            if i + 1 < len(boxes):
                diag.connect(boxes[i], boxes[i + 1], routing="direct", width=1.8, color=INK, head="stealth")
            else:
                continue
            diag.text(enz, size=11, color="#333333").at(GX + 108, y, anchor="left_center")
            if tally:
                diag.text(f"**{tally}**", size=12, color=colour).at(GX + 290, y, anchor="left_center")
        # The last arrow: pyruvate -> acetyl-CoA.
        y_last = GY0 + (len(GLYCOLYSIS) - 1) * GDY
        acetyl = diag.shape("2 x Acetyl-CoA", 190, BH, style=Style(fill="#F0C4C4", stroke=INK, stroke_width=1.4, radius=6),
                            fit_label=False).at(GX, y_last + 56, anchor="center")
        diag.connect(boxes[-1], acetyl, routing="direct", width=1.8, color=INK, head="stealth")
        diag.text("pyruvate dehydrogenase", size=11, color="#333333").at(GX + 108, y_last + 28, anchor="left_center")
        diag.text("**+2 NADH, 2 CO2**", size=12, color=BLUE).at(GX + 290, y_last + 28, anchor="left_center")

        # TCA cycle: eight intermediates on an ellipse, clockwise from the upper left.
        diag.text("**TCA cycle** (mitochondrial matrix), runs twice per glucose", size=14).at(CX, CY - RY - 52, anchor="bottom_center")
        nodes = {}
        pos = {}
        for k, name in enumerate(CYCLE):
            ang = math.radians(315 + 45 * k)
            x, y = CX + RX * math.sin(ang), CY - RY * math.cos(ang)
            pos[name] = (x, y, ang)
            nodes[name] = diag.shape(name, 124, BH, style=ACID, fit_label=False).at(x, y, anchor="center")
        for k, name in enumerate(CYCLE):
            nxt = CYCLE[(k + 1) % len(CYCLE)]
            diag.connect(nodes[name], nodes[nxt], routing="direct", width=1.8, color=INK, head="stealth")
            if name in CYCLE_TALLY:
                text, colour = CYCLE_TALLY[name]
                x1, y1, _ = pos[name]
                x2, y2, _ = pos[nxt]
                mx, my = (x1 + x2) / 2, (y1 + y2) / 2
                # Push the tally outward from the middle of the ring.
                ux, uy = CX - mx, CY - my
                n = math.hypot(ux, uy)
                diag.text(f"**{text}**", size=12, color=colour).at(mx - ux / n * 46, my - uy / n * 46, anchor="center")
        diag.text("per turn:\n3 NADH, 1 FADH2\n1 GTP, 2 CO2", size=12, color="#333333").at(CX, CY, anchor="center")

        # Acetyl-CoA joins oxaloacetate at citrate synthase.
        cit = pos["Citrate"]
        diag.connect(acetyl.anchor("right", 0.5), nodes["Citrate"].anchor("left", 0.25), routing="orthogonal",
                     width=1.8, color=INK, head="stealth")
        diag.text("citrate synthase\n(+ oxaloacetate)", size=11, color="#333333").at(cit[0] - 66, cit[1] - 26, anchor="bottom_center")

        # Tally table per glucose.
        tx0, ty0 = 690.0, 532.0
        widths = (210, 70, 70, 70, 70)
        rows = [
            ("Per glucose", "ATP", "NADH", "FADH2", "CO2"),
            ("Glycolysis (net)", "2", "2", "0", "0"),
            ("Pyruvate to acetyl-CoA", "0", "2", "0", "2"),
            ("TCA cycle (2 turns)", "2", "6", "2", "4"),
            ("Total", "4", "10", "2", "6"),
        ]
        for r, row in enumerate(rows):
            x = tx0
            for c, (text, w) in enumerate(zip(row, widths)):
                style = HEAD if r == 0 else TOTAL if r == len(rows) - 1 else CELL
                label = f"**{text}**" if r in (0, len(rows) - 1) else text
                diag.shape(label, w, 24, style=style, fit_label=False).at(x, ty0 + r * 24, anchor="top_left")
                x += w
        diag.text("Oxidative phosphorylation reoxidises 10 NADH and 2 FADH2: about 25 + 3 ATP, so roughly 32 ATP per glucose.",
                  size=11, color="#333333").at(tx0, ty0 + 5 * 24 + 8, anchor="top_left")
        diag.caption(
            "**Figure 3:** Glucose to CO2. Glycolysis invests 2 ATP and returns 4, and the TCA cycle turns twice per glucose;\n"
            "the table counts substrate-level ATP and the reduced carriers NADH and FADH2",
            small_caps=True,
        )
    return diag


def build_diagram(output_dir: Path | str = "examples/biology") -> Path:
    return render_all(diagram(), output_dir, "03_glycolysis_tca")["svg"]


if __name__ == "__main__":
    build_diagram(Path(sys.argv[1]) if len(sys.argv) > 1 else Path("examples/biology"))
