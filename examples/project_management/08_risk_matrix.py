"""A 5x5 risk matrix: likelihood against impact, with the project's risks plotted.

Each cell is scored ``likelihood x impact`` and coloured by rating band (low up
to 4, medium up to 9, high up to 14, critical from 15). Risks are numbered dots
placed in their cell; the register on the right is sorted by score and every
score and rating is computed from the two inputs, so moving a risk is a
one-number change.
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

from diagrams_as_code import Diagram
from diagrams_as_code.output import render_all
from diagrams_as_code.style import Style
from diagrams_as_code.text.metrics import text_width

LIKELIHOOD = ["Rare", "Unlikely", "Possible", "Likely", "Almost certain"]   # 1..5
IMPACT = ["Minor", "Moderate", "Serious", "Major", "Severe"]                 # 1..5
BANDS = [  # (maximum score, name, cell fill, ink)
    (4, "Low", "#CDE8D2", "#2E6B3F"),
    (9, "Medium", "#F6EDB2", "#7A6200"),
    (14, "High", "#F7C99A", "#9A4A00"),
    (25, "Critical", "#EE9C97", "#8A1C1C"),
]

# (title, likelihood, impact)
RISKS = [
    ("Requirement ambiguity", 5, 4),
    ("Scope creep", 5, 3),
    ("Security audit finding", 3, 5),
    ("Key engineer leaves", 3, 4),
    ("Vendor API deprecation", 4, 3),
    ("Data migration corrupts records", 2, 5),
    ("Cloud cost overrun", 4, 2),
    ("Test environment unstable", 4, 2),
    ("Legal review delay", 2, 3),
    ("Licence cost rise", 2, 2),
    ("Office move disrupts team", 1, 2),
]

CELL_W, CELL_H = 80, 62
GX, GY = 180, 70            # top-left of the grid
TX = GX + 5 * CELL_W + 50   # register column


def rect(x0, y0, x1, y1):
    return [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]


def band(score: int):
    return next(b for b in BANDS if score <= b[0])


def diagram() -> Diagram:
    with Diagram("Risk matrix", theme="pastel_light") as diag:
        # Cells: likelihood 5 on the top row, impact 1 on the left column.
        for li in range(1, 6):
            for im in range(1, 6):
                _, _, fill, ink = band(li * im)
                x0, y0 = GX + (im - 1) * CELL_W, GY + (5 - li) * CELL_H
                diag.polygon(rect(x0, y0, x0 + CELL_W, y0 + CELL_H),
                             style=Style(fill=fill, stroke="#FFFFFF", stroke_width=2.0), z=-2)
                diag.text(str(li * im), size=10, color=ink).at(x0 + CELL_W - 6, y0 + 10, anchor="right_center")
        for i, name in enumerate(LIKELIHOOD, start=1):
            diag.text(f"{name} ({i})", size=12).at(GX - 10, GY + (5 - i) * CELL_H + CELL_H / 2, anchor="right_center")
        for i, name in enumerate(IMPACT, start=1):
            diag.text(f"{name} ({i})", size=12).at(GX + (i - 1) * CELL_W + CELL_W / 2, GY + 5 * CELL_H + 16, anchor="center")
        diag.text("**Likelihood**", size=13).at(GX - 10, GY - 20, anchor="right_center")
        diag.text("**Impact**", size=13).at(GX + 5 * CELL_W / 2, GY + 5 * CELL_H + 40, anchor="center")

        # Risk dots, spread across their cell without overlapping.
        cell_risks: dict[tuple[int, int], list[int]] = {}
        for n, (_, li, im) in enumerate(RISKS, start=1):
            cell_risks.setdefault((li, im), []).append(n)
        for (li, im), ids in cell_risks.items():
            cx0, cy0 = GX + (im - 1) * CELL_W, GY + (5 - li) * CELL_H
            step = 26
            for k, n in enumerate(ids):
                cx = cx0 + CELL_W / 2 + (k - (len(ids) - 1) / 2) * step
                cy = cy0 + CELL_H / 2 + 6
                ring = [(cx + 11 * math.cos(a * math.pi / 12), cy + 11 * math.sin(a * math.pi / 12)) for a in range(24)]
                diag.polygon(ring, style=Style(fill="#FFFFFF", stroke="#1F2F57", stroke_width=1.6), z=2)
                diag.text(f"**{n}**", size=11, z=3).at(cx, cy, anchor="center")

        # Register sorted by score.
        diag.text("**Risk register**", size=14).at(TX, GY - 20, anchor="left_center")
        ranked = sorted(enumerate(RISKS, start=1), key=lambda t: (-t[1][1] * t[1][2], t[0]))
        title_w = max(text_width(r[0], 12) for r in RISKS)
        col_score = TX + 30 + title_w + 16
        counts = {b[1]: 0 for b in BANDS}
        for row, (n, (title, li, im)) in enumerate(ranked):
            y = GY + 14 + row * 26
            score = li * im
            _, name, fill, ink = band(score)
            counts[name] += 1
            ring = [(TX + 9 + 9 * math.cos(a * math.pi / 12), y + 9 * math.sin(a * math.pi / 12)) for a in range(24)]
            diag.polygon(ring, style=Style(fill="#FFFFFF", stroke="#1F2F57", stroke_width=1.3), z=2)
            diag.text(str(n), size=10, z=3).at(TX + 9, y, anchor="center")
            diag.text(title, size=12).at(TX + 30, y, anchor="left_center")
            diag.polygon(rect(col_score, y - 10, col_score + 92, y + 10),
                         style=Style(fill=fill, stroke="none"), z=1)
            diag.text(f"{li}x{im} = {score}  {name}", size=11, color=ink, z=3).at(col_score + 46, y, anchor="center")

        summary = ", ".join(f"{counts[b[1]]} {b[1].lower()}" for b in reversed(BANDS))
        diag.text("Score bands: low 1-4, medium 5-9, high 10-14, critical 15-25.", size=11, color="#4B5563").at(
            TX, GY + 14 + len(ranked) * 26 + 6, anchor="left_center")
        diag.caption(
            f"**Figure 8:** Risk matrix with {len(RISKS)} risks: {summary}. "
            f"Highest score {max(li * im for _, li, im in RISKS)} of 25",
            small_caps=True, max_width=900,
        )
    return diag


def build_diagram(output_dir: Path | str = "examples/project_management") -> Path:
    return render_all(diagram(), output_dir, "08_risk_matrix")["svg"]


if __name__ == "__main__":
    dest = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("examples/project_management")
    build_diagram(dest)
