"""Mind map: System Design Interview Breakdown (MIND_MAP domain, Enterprise).

How to talk through "design a URL shortener" in a 45-minute interview. The
eight branches follow the order a strong answer takes (requirements and
estimates on the left, the design and its trade-offs on the right); leaves
are the points to cover, and dashed notes at the third level hold the
numbers worth quoting.
"""
from __future__ import annotations

import sys
from pathlib import Path

from diagrams_as_code import Diagram, Style
from diagrams_as_code.output import render_all

CX, CY = 890.0, 370.0
PITCH = 42.0
GAP = 26.0

# (branch, colour, [(point, optional third-level note), ...])
PLAN = {
    "left": [
        ("1 Requirements", "#50FA7B", [
            ("Shorten and redirect", None), ("Custom aliases", None), ("Link expiry", None),
            ("100M new URLs / day", "≈1.2k writes/s"), ("Redirect p99 < 50 ms", None),
        ]),
        ("2 Estimates", "#F1FA8C", [
            ("Read:write = 100:1", "≈115k reads/s"), ("500 B per record", None), ("Five-year retention", "≈90 TB stored"),
        ]),
        ("3 API", "#FFB86C", [
            ("POST /urls", None), ("GET /{code} → 302", None), ("DELETE /urls/{code}", None),
        ]),
        ("4 Data Model", "#FF79C6", [
            ("urls(code, long_url, ttl)", None), ("users(id, plan)", None), ("Key-value store", "Scales horizontally"),
        ]),
    ],
    "right": [
        ("5 ID Generation", "#BD93F9", [
            ("Base62 codes", "7 chars ≈ 3.5T codes"), ("Counter ranges per node", "No collisions"), ("Hash + collision check", None),
        ]),
        ("6 Caching", "#8BE9FD", [
            ("Redis LRU for hot codes", "20% of codes, 80% of reads"), ("CDN edge redirects", None), ("Write-through on create", None),
        ]),
        ("7 Scaling", "#FF6E6E", [
            ("Consistent-hash shards", None), ("Read replicas", None), ("Per-key rate limiting", None),
        ]),
        ("8 Trade-offs", "#E2E2DC", [
            ("301 vs 302 redirects", "302 keeps analytics"), ("Async click analytics", None), ("Availability over\nconsistency", None),
        ]),
    ],
}


def diagram() -> Diagram:
    with Diagram("System Design Interview: URL Shortener Breakdown", theme="dracula") as diag:
        root = diag.shape(
            "**Design a**\n**URL Shortener**\n45-minute interview", 210, 92,
            style=Style(radius=40, fill="#F8F8F2", stroke="#BD93F9", stroke_width=3.5, text_color="#282A36", font_size=17),
        ).at(CX, CY, anchor="center")

        for side, branches in PLAN.items():
            sign = -1 if side == "left" else 1
            inner = "right" if side == "left" else "left"
            total = sum(len(b[2]) * PITCH for b in branches) + GAP * (len(branches) - 1)
            top = CY - total / 2
            for label, colour, points in branches:
                block = len(points) * PITCH
                number, name = label.split(" ", 1)
                branch = diag.shape(
                    f"**{number} · {name}**", 160, 46,
                    style=Style(radius=23, fill=colour, stroke=colour, text_color="#282A36", font_size=15),
                ).at(CX + sign * 255, top + block / 2, anchor="center")
                diag.connect(root.anchor(side, 0.5), branch.anchor(inner, 0.5),
                             routing="curve", color=colour, width=3.5, head="none")
                for i, (point, note) in enumerate(points):
                    y = top + PITCH * (i + 0.5)
                    leaf = diag.shape(
                        point, 200, 32 if "\n" not in point else 38,
                        style=Style(radius=16, fill="#383A59", stroke=colour, stroke_width=1.5,
                                    text_color="#F8F8F2", font_size=13 if "\n" not in point else 12),
                    ).at(CX + sign * 545, y, anchor="center")
                    diag.connect(branch.anchor(side, 0.5), leaf.anchor(inner, 0.5),
                                 routing="curve", color=colour, width=1.8, head="none")
                    if note:
                        detail = diag.shape(
                            f"*{note}*", 190, 28,
                            style=Style(radius=14, fill="#282A36", stroke=colour, stroke_width=1, dash="4,3",
                                        shadow=False, text_color=colour, font_size=12),
                        ).at(CX + sign * 765, y, anchor="center")
                        diag.connect(leaf.anchor(side, 0.5), detail.anchor(inner, 0.5),
                                     routing="curve", color=colour, width=1, head="none", style="dashed")
                top += block + GAP
    return diag


def build_diagram(output_dir: Path | str = "output/mind_map") -> Path:
    return render_all(diagram(), output_dir, "09_system_design_interview")["svg"]


if __name__ == "__main__":
    dest = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("output/mind_map")
    build_diagram(dest)
