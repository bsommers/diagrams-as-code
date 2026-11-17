"""Mind map: Startup Idea Brainstorm (MIND_MAP domain, Moderate).

A fully radial brainstorm. Six branches sit on an ellipse around the central
idea and their sub-topics fan out further along the same bearing; every
position is computed with ``math.cos`` / ``math.sin`` so the map stays tidy
when branches are added or removed.
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

from diagrams_as_code import Diagram, Style
from diagrams_as_code.output import render_all

CX, CY = 640.0, 400.0
BRANCHES = [
    # (label, colour, bearing in degrees (0 = east, clockwise), sub-topics)
    ("Problem", "#F28B82", -60, ["Freelancers chase\nlate invoices", "Cash-flow gaps"]),
    ("Solution", "#FBBC04", 0, ["Auto-reminder\nworkflows", "Instant payout\nadvance", "Bank sync"]),
    ("Customers", "#81C995", 60, ["Designers", "Developers"]),
    ("Revenue", "#78D9EC", 120, ["Freemium SaaS", "1% payout fee"]),
    ("Competition", "#AECBFA", 180, ["Spreadsheets", "Big accounting\nsuites", "Factoring firms"]),
    ("Risks", "#D7AEFB", 240, ["Credit default", "Bank APIs"]),
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
    with Diagram("Startup Idea Brainstorm Radial Mind Map", theme="nord") as diag:
        root = diag.shape(
            "**InvoicePilot**\nGet paid on time", 200, 74,
            style=Style(radius=37, fill="#ECEFF4", stroke="#88C0D0", stroke_width=3, text_color="#2E3440", font_size=17),
        ).at(CX, CY, anchor="center")
        for label, colour, bearing, children in BRANCHES:
            bx, by = _polar(250, 175, bearing)
            branch = diag.shape(
                f"**{label}**", 130, 44,
                style=Style(radius=22, fill=colour, stroke=colour, text_color="#2E3440", font_size=15),
            ).at(bx, by, anchor="center")
            out = _side(bx - CX, by - CY)
            # Diagonal branches leave the top or bottom of the root off-centre.
            frac = 0.5 if out in ("left", "right") else (0.72 if bx > CX else 0.28)
            diag.connect(root.anchor(out, frac), branch.anchor(_opposite(out), 0.5),
                         routing="curve", color=colour, width=4, head="none")
            n = len(children)
            for i, child in enumerate(children):
                spread = 26 if n == 3 else 30
                cx, cy = _polar(460, 330, bearing + (i - (n - 1) / 2) * spread)
                lines = child.count("\n") + 1
                leaf = diag.shape(
                    child, 160, 22 + 18 * lines,
                    style=Style(radius=16, fill="#3B4252", stroke=colour, stroke_width=1.6, text_color="#ECEFF4", font_size=13),
                ).at(cx, cy, anchor="center")
                leg = _side(cx - bx, cy - by)
                diag.connect(branch.anchor(leg, 0.5), leaf.anchor(_opposite(leg), 0.5),
                             routing="curve", color=colour, width=2, head="none")
    return diag


def build_diagram(output_dir: Path | str = "output/mind_map") -> Path:
    return render_all(diagram(), output_dir, "02_startup_idea_brainstorm")["svg"]


if __name__ == "__main__":
    dest = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("output/mind_map")
    build_diagram(dest)
