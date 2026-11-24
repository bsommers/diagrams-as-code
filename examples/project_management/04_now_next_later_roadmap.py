"""A now / next / later roadmap with confidence-weighted cards.

Instead of dates, the roadmap commits to a horizon. *Now* is in flight and
high-confidence, *next* is shaped but not started, *later* is a direction that
may change. Each card carries its strategic objective (colour) and a confidence
level (the pips); the header counts and the legend totals are computed from the
card list, so adding a card updates the figure.
"""
from __future__ import annotations

import sys
from pathlib import Path

from diagrams_as_code import Diagram
from diagrams_as_code.output import render_all
from diagrams_as_code.style import Style
from diagrams_as_code.text.metrics import text_width

OBJECTIVES = {
    "growth": ("Grow activation", "#4F81BD", "#DCE8F5"),
    "reliability": ("Platform reliability", "#2E8B57", "#DDF0E4"),
    "revenue": ("Expand revenue", "#B8860B", "#F7EBCB"),
    "trust": ("Security and trust", "#8E44AD", "#EBDDF3"),
}
CONFIDENCE = {"high": 3, "medium": 2, "low": 1}

# (horizon, title, objective, confidence)
CARDS = [
    ("Now", "Guided onboarding checklist", "growth", "high"),
    ("Now", "Zero-downtime schema migrations", "reliability", "high"),
    ("Now", "SSO with SAML and OIDC", "trust", "high"),
    ("Now", "Usage-based billing meter", "revenue", "medium"),
    ("Next", "In-app templates gallery", "growth", "medium"),
    ("Next", "Multi-region failover", "reliability", "medium"),
    ("Next", "Audit log export API", "trust", "medium"),
    ("Next", "Team plan with seat management", "revenue", "medium"),
    ("Later", "Workspace analytics", "growth", "low"),
    ("Later", "Self-serve data residency", "trust", "low"),
    ("Later", "Partner marketplace", "revenue", "low"),
]
HORIZONS = [
    ("Now", "In flight, committed", "#2E8B57"),
    ("Next", "Shaped, not started", "#9A7209"),
    ("Later", "Direction, may change", "#6B7280"),
]

COL_W, GAP, CARD_H, CARD_GAP = 280, 24, 62, 12
X0, Y0 = 40, 40
HEAD_H = 54


def rect(x0, y0, x1, y1):
    return [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]


def diagram() -> Diagram:
    with Diagram("Now / next / later roadmap", theme="pastel_light") as diag:
        rows = max(sum(1 for c in CARDS if c[0] == h[0]) for h in HORIZONS)
        body_h = rows * (CARD_H + CARD_GAP) + CARD_GAP
        for i, (name, sub, colour) in enumerate(HORIZONS):
            x = X0 + i * (COL_W + GAP)
            cards = [c for c in CARDS if c[0] == name]
            diag.polygon(rect(x, Y0, x + COL_W, Y0 + HEAD_H + body_h),
                         style=Style(fill="#F7F8FA", stroke="#C9CED6", stroke_width=1.0), z=-3)
            diag.polygon(rect(x, Y0, x + COL_W, Y0 + HEAD_H),
                         style=Style(fill=colour, stroke="none"), z=-2)
            diag.text(f"**{name.upper()}**  ({len(cards)})", size=16, color="#FFFFFF").at(
                x + 14, Y0 + 18, anchor="left_center")
            diag.text(sub, size=12, color="#FFFFFF").at(x + 14, Y0 + 39, anchor="left_center")
            for j, (_, title, obj, conf) in enumerate(cards):
                _, stroke, fill = OBJECTIVES[obj]
                cy = Y0 + HEAD_H + CARD_GAP + j * (CARD_H + CARD_GAP)
                diag.polygon(rect(x + 12, cy, x + COL_W - 12, cy + CARD_H),
                             style=Style(fill=fill, stroke=stroke, stroke_width=1.2), z=0)
                diag.polygon(rect(x + 12, cy, x + 18, cy + CARD_H),
                             style=Style(fill=stroke, stroke="none"), z=1)
                diag.text(f"**{title}**", size=13).at(x + 28, cy + 22, anchor="left_center")
                diag.text(OBJECTIVES[obj][0], size=11, color=stroke).at(
                    x + 28, cy + 46, anchor="left_center")
                for k in range(3):  # confidence pips
                    px = x + COL_W - 30 - (2 - k) * 12
                    on = k < CONFIDENCE[conf]
                    diag.polygon(rect(px - 4, cy + 42, px + 4, cy + 50),
                                 style=Style(fill=stroke if on else "#FFFFFF", stroke=stroke, stroke_width=1.0), z=1)
                diag.text(conf, size=10, color="#4B5563").at(x + COL_W - 66, cy + 46, anchor="right_center")

        ly = Y0 + HEAD_H + body_h + 22
        lx = X0
        for key, (name, stroke, fill) in OBJECTIVES.items():
            n = sum(1 for c in CARDS if c[2] == key)
            label = f"{name} ({n})"
            diag.polygon(rect(lx, ly - 6, lx + 16, ly + 6), style=Style(fill=fill, stroke=stroke, stroke_width=1.2), z=1)
            diag.text(label, size=12).at(lx + 24, ly, anchor="left_center")
            lx += 24 + text_width(label, 12) + 28
        diag.text("Confidence pips: 3 = high, 2 = medium, 1 = low", size=11, color="#4B5563").at(
            X0, ly + 24, anchor="left_center")

        high = [c for c in CARDS if c[3] == "high"]
        in_now = sum(1 for c in high if c[0] == "Now")
        diag.caption(
            f"**Figure 4:** Now / next / later roadmap: {len(CARDS)} initiatives across "
            f"{len(OBJECTIVES)} objectives; {in_now} of {len(high)} high-confidence items are in Now",
            small_caps=True, max_width=900,
        )
    return diag


def build_diagram(output_dir: Path | str = "examples/project_management") -> Path:
    return render_all(diagram(), output_dir, "04_now_next_later_roadmap")["svg"]


if __name__ == "__main__":
    dest = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("examples/project_management")
    build_diagram(dest)
