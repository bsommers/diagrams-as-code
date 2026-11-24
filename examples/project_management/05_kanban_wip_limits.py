"""A kanban board whose columns enforce work-in-progress (WIP) limits.

Every column header shows ``count / limit``. A column under its limit is green,
one exactly at the limit is amber and one over it is red with a flag, so the
bottleneck is visible without reading a card. Counts, states and the board's
total WIP are computed from the card list. Card age is shown in days; the
stripe colour is the work-item class.
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

from diagrams_as_code import Diagram
from diagrams_as_code.output import render_all
from diagrams_as_code.style import Style

CLASSES = {"feature": "#4F81BD", "bug": "#C0392B", "chore": "#7F8C8D"}

# (column, WIP limit or None)
COLUMNS = [("Backlog", None), ("Ready", 4), ("In progress", 3), ("Review", 2), ("Done", None)]

# (id, title, class, assignee, age in days, column)
CARDS = [
    ("PM-41", "Export to CSV", "feature", "AL", 0, "Backlog"),
    ("PM-42", "Dark mode tokens", "feature", "", 0, "Backlog"),
    ("PM-43", "Rotate API keys", "chore", "", 0, "Backlog"),
    ("PM-44", "Search relevance", "feature", "", 0, "Backlog"),
    ("PM-36", "Fix timezone drift", "bug", "RK", 1, "Ready"),
    ("PM-37", "Invite flow copy", "feature", "", 1, "Ready"),
    ("PM-38", "Upgrade Postgres 16", "chore", "", 2, "Ready"),
    ("PM-31", "Bulk edit tasks", "feature", "JT", 3, "In progress"),
    ("PM-32", "Fix 500 on import", "bug", "MS", 2, "In progress"),
    ("PM-33", "Webhook retries", "feature", "AL", 4, "In progress"),
    ("PM-27", "Billing page", "feature", "RK", 6, "Review"),
    ("PM-28", "Cache invalidation", "bug", "JT", 5, "Review"),
    ("PM-29", "Audit log paging", "feature", "MS", 4, "Review"),
    ("PM-22", "Onboarding emails", "feature", "AL", 8, "Done"),
    ("PM-23", "Fix login redirect", "bug", "RK", 3, "Done"),
    ("PM-24", "Terraform modules", "chore", "JT", 5, "Done"),
]

COL_W, GAP = 196, 14
CARD_W, CARD_H, CARD_GAP = 172, 58, 10
X0, Y0, HEAD_H = 40, 40, 58
GREEN, AMBER, RED = "#2E8B57", "#C98A00", "#C0392B"


def rect(x0, y0, x1, y1):
    return [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]


def state(count: int, limit: int | None) -> tuple[str, str]:
    if limit is None:
        return "#6B7280", "no limit"
    if count > limit:
        return RED, "over limit"
    if count == limit:
        return AMBER, "at limit"
    return GREEN, "within limit"


def diagram() -> Diagram:
    with Diagram("Kanban board with WIP limits", theme="pastel_light") as diag:
        rows = max(sum(1 for c in CARDS if c[5] == name) for name, _ in COLUMNS)
        body_h = rows * (CARD_H + CARD_GAP) + CARD_GAP
        breaches = []
        wip = 0
        for i, (name, limit) in enumerate(COLUMNS):
            x = X0 + i * (COL_W + GAP)
            cards = [c for c in CARDS if c[5] == name]
            colour, word = state(len(cards), limit)
            if limit is not None:
                wip += len(cards)
            if limit is not None and len(cards) > limit:
                breaches.append(name)
            diag.polygon(rect(x, Y0, x + COL_W, Y0 + HEAD_H + body_h),
                         style=Style(fill="#F4F5F7", stroke=colour if word == "over limit" else "#C9CED6",
                                     stroke_width=2.2 if word == "over limit" else 1.0), z=-3)
            diag.polygon(rect(x, Y0, x + COL_W, Y0 + HEAD_H), style=Style(fill=colour, stroke="none"), z=-2)
            diag.text(f"**{name}**", size=15, color="#FFFFFF").at(x + 12, Y0 + 19, anchor="left_center")
            count = f"{len(cards)} / {limit}" if limit is not None else f"{len(cards)}"
            diag.text(f"{count}  {word}", size=12, color="#FFFFFF").at(x + 12, Y0 + 41, anchor="left_center")
            for j, (cid, title, kind, who, age, _) in enumerate(cards):
                cx = x + (COL_W - CARD_W) / 2
                cy = Y0 + HEAD_H + CARD_GAP + j * (CARD_H + CARD_GAP)
                diag.polygon(rect(cx, cy, cx + CARD_W, cy + CARD_H),
                             style=Style(fill="#FFFFFF", stroke="#B8BEC8", stroke_width=1.0), z=0)
                diag.polygon(rect(cx, cy, cx + 5, cy + CARD_H), style=Style(fill=CLASSES[kind], stroke="none"), z=1)
                diag.text(f"**{title}**", size=12).at(cx + 14, cy + 18, anchor="left_center")
                diag.text(cid, size=11, color="#6B7280").at(cx + 14, cy + 41, anchor="left_center")
                if who:
                    ring = [(cx + CARD_W - 20 + 11 * math.cos(a * 0.3927),
                             cy + 41 + 11 * math.sin(a * 0.3927)) for a in range(16)]
                    diag.polygon(ring, style=Style(fill="#E4E8EF", stroke="#9AA3B2", stroke_width=1.0), z=1)
                    diag.text(who, size=10, z=3).at(cx + CARD_W - 20, cy + 41, anchor="center")
                if age and name not in ("Done", "Backlog"):
                    diag.text(f"{age} d", size=10, color=RED if age >= 5 else "#6B7280").at(
                        cx + CARD_W - 12, cy + 16, anchor="right_center")

        ly = Y0 + HEAD_H + body_h + 22
        lx = X0
        for kind, colour in CLASSES.items():
            diag.polygon(rect(lx, ly - 6, lx + 16, ly + 6), style=Style(fill=colour, stroke="none"), z=1)
            diag.text(kind, size=12).at(lx + 24, ly, anchor="left_center")
            lx += 90
        diag.text(f"Board WIP (Ready to Review): {wip} items against a combined limit of "
                  f"{sum(l for _, l in COLUMNS if l)}.  Over limit: {', '.join(breaches) or 'none'}.",
                  size=12, color=RED if breaches else "#4B5563").at(lx + 20, ly, anchor="left_center")
        diag.caption(
            f"**Figure 5:** Kanban board, {len(CARDS)} cards. {', '.join(breaches)} is over its WIP limit: "
            "stop starting, start finishing",
            small_caps=True, max_width=900,
        )
    return diag


def build_diagram(output_dir: Path | str = "examples/project_management") -> Path:
    return render_all(diagram(), output_dir, "05_kanban_wip_limits")["svg"]


if __name__ == "__main__":
    dest = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("examples/project_management")
    build_diagram(dest)
