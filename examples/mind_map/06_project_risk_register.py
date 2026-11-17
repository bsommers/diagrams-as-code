"""Mind map: Project Risk Register (MIND_MAP domain, Moderate).

The risk register of a data-platform migration drawn radially. Six risk
categories surround the project; each risk is a leaf whose outline carries
its category colour and whose fill shows its rated severity, explained by the
legend in the corner. Positions come from ``math.cos`` / ``math.sin``.
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

from diagrams_as_code import Diagram, Style
from diagrams_as_code.output import render_all

CX, CY = 660.0, 400.0
SEVERITY = {"High": "#7F1D1D", "Medium": "#78350F", "Low": "#14532D"}
CATEGORIES = [
    # (category, colour, bearing in degrees, [(risk, severity), ...])
    ("Schedule", "#38BDF8", -60, [("Data freeze slips", "High"), ("Holiday code freeze", "Medium")]),
    ("Technical", "#A78BFA", 0, [("Schema drift in\nlegacy tables", "High"), ("Throughput below\n50k rows/s", "Medium"), ("Index rebuild time", "Low")]),
    ("Vendor", "#F472B6", 60, [("Licence renewal\nunsigned", "Medium"), ("Support SLA 48h", "Low")]),
    ("Compliance", "#FBBF24", 120, [("GDPR data residency", "High"), ("Audit trail gaps", "Medium")]),
    ("People", "#34D399", 180, [("DBA on leave in Q2", "Medium"), ("Single owner of\nETL jobs", "High"), ("Onboarding contractors", "Low")]),
    ("Budget", "#FB923C", 240, [("Cloud egress costs", "Medium"), ("Dual-running licences", "Low")]),
]


def _side(dx: float, dy: float) -> str:
    """The side of a box facing direction (dx, dy)."""
    if abs(dx) * 0.55 >= abs(dy):
        return "right" if dx > 0 else "left"
    return "bottom" if dy > 0 else "top"


def _opposite(side: str) -> str:
    return {"left": "right", "right": "left", "top": "bottom", "bottom": "top"}[side]


def _polar(rx: float, ry: float, deg: float) -> tuple[float, float]:
    rad = math.radians(deg)
    return CX + rx * math.cos(rad), CY + ry * math.sin(rad)


def diagram() -> Diagram:
    with Diagram("Data Platform Migration Risk Register", theme="cyber_slate") as diag:
        root = diag.shape(
            "**Project Atlas**\nRisk Register", 200, 74,
            style=Style(radius=37, fill="#F8FAFC", stroke="#38BDF8", stroke_width=3, text_color="#0F172A", font_size=17),
        ).at(CX, CY, anchor="center")

        for label, colour, bearing, risks in CATEGORIES:
            bx, by = _polar(255, 180, bearing)
            branch = diag.shape(
                f"**{label}**", 136, 44,
                style=Style(radius=22, fill=colour, stroke=colour, text_color="#0F172A", font_size=15),
            ).at(bx, by, anchor="center")
            out = _side(bx - CX, by - CY)
            frac = 0.5 if out in ("left", "right") else (0.72 if bx > CX else 0.28)
            diag.connect(root.anchor(out, frac), branch.anchor(_opposite(out), 0.5),
                         routing="curve", color=colour, width=4, head="none")
            n = len(risks)
            for i, (risk, severity) in enumerate(risks):
                lx, ly = _polar(480, 330, bearing + (i - (n - 1) / 2) * (25 if n == 3 else 30))
                lines = risk.count("\n") + 1
                leaf = diag.shape(
                    risk, 170, 22 + 18 * lines,
                    style=Style(radius=16, fill=SEVERITY[severity], stroke=colour, stroke_width=1.8,
                                text_color="#F8FAFC", font_size=13),
                ).at(lx, ly, anchor="center")
                leg = _side(lx - bx, ly - by)
                diag.connect(branch.anchor(leg, 0.5), leaf.anchor(_opposite(leg), 0.5),
                             routing="curve", color=colour, width=2, head="none")

        # Legend in the empty top-left corner.
        diag.text("**Severity**", size=14, align="left").at(40, 40)
        for i, (name, fill) in enumerate(SEVERITY.items()):
            diag.shape(name, 90, 26, style=Style(radius=13, fill=fill, stroke="#94A3B8", stroke_width=1,
                                                  text_color="#F8FAFC", font_size=12)).at(40, 70 + i * 34)
    return diag


def build_diagram(output_dir: Path | str = "output/mind_map") -> Path:
    return render_all(diagram(), output_dir, "06_project_risk_register")["svg"]


if __name__ == "__main__":
    dest = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("output/mind_map")
    build_diagram(dest)
