"""Example: Squads, tribes, chapters and guilds (ORGANISATION domain).

The Spotify-model vocabulary on one page. Squads are the columns (cross-functional
teams), tribes group related squads, chapters are the colour-coded rows (people of
one craft across squads) and a guild is a voluntary community of interest cutting
across every tribe.
"""
from __future__ import annotations

import sys
from pathlib import Path

from diagrams_as_code import Diagram, Style
from diagrams_as_code.output import render_all

#: tribe -> squads
TRIBES = {
    "Payments tribe": ("Checkout", "Billing", "Fraud"),
    "Growth tribe": ("Onboarding", "Referrals"),
}
#: chapter (row) -> style
CHAPTERS = {
    "Backend chapter": Style(fill="#D9E3F5", stroke="#2F4B86"),
    "Frontend chapter": Style(fill="#E4F1E8", stroke="#3C8D53"),
    "QA chapter": Style(fill="#FBF0C8", stroke="#B8860B"),
}
WORD = {"Backend chapter": "backend", "Frontend chapter": "frontend", "QA chapter": "QA"}
HEADCOUNT = {"Checkout": (3, 2, 1), "Billing": (2, 1, 1), "Fraud": (3, 0, 1), "Onboarding": (1, 3, 1), "Referrals": (1, 2, 1)}
CW, CH, ROW_GAP = 112.0, 44.0, 14.0
SQUAD_PAD, TRIBE_PAD, SQUAD_GAP, TRIBE_GAP = 14.0, 18.0, 20.0, 40.0
LABEL_X, LABEL_W = 60.0, 150.0
X0, Y0 = LABEL_X + LABEL_W + 40.0, 90.0
ROW_Y = Y0 + 34.0 + TRIBE_PAD + 35.0 + SQUAD_PAD  # below tribe and squad headers


def diagram() -> Diagram:
    with Diagram("Squads, tribes, chapters and guilds", theme="paper") as diag:
        x = X0
        qa_cells = []
        for tribe, squads in TRIBES.items():
            with diag.group(tribe, padding=TRIBE_PAD, header_height=34, style=Style(fill="#F7F8FA", stroke="#6B7280")):
                for squad in squads:
                    sx = x + TRIBE_PAD + SQUAD_PAD
                    with diag.group(f"{squad} squad", padding=SQUAD_PAD, header_height=35):
                        for r, (chapter, style) in enumerate(CHAPTERS.items()):
                            n = HEADCOUNT[squad][r]
                            cell = diag.shape(f"{n} {WORD[chapter]}" if n else "none yet", CW, CH,
                                              style=style if n else Style(fill="#FFFFFF", stroke="#D5D9DE", dash="4,3"),
                                              ).at(sx, ROW_Y + r * (CH + ROW_GAP))
                            if chapter.startswith("QA"):
                                qa_cells.append(cell)
                    x += CW + 2 * SQUAD_PAD + SQUAD_GAP
                x += 2 * TRIBE_PAD - SQUAD_GAP + TRIBE_GAP

        for r, (chapter, style) in enumerate(CHAPTERS.items()):
            diag.shape(chapter, LABEL_W, CH, style=style).at(LABEL_X, ROW_Y + r * (CH + ROW_GAP))

        guild_y = ROW_Y + 3 * (CH + ROW_GAP) + 70.0
        guild_x, guild_right = qa_cells[0].bounds.left, qa_cells[-1].bounds.right
        guild = diag.shape("Test Automation guild: open to anyone, any squad, any tribe",
                           guild_right - guild_x, 46,
                           style=Style(fill="#EFE6F7", stroke="#6B3F95", dash="6,4")).at(guild_x, guild_y)
        for cell in qa_cells:
            frac = (cell.bounds.left + CW / 2 - guild_x) / (guild_right - guild_x)
            guild.anchor("top", frac) >> diag.edge(style="dashed", color="#6B3F95", arrow_head=False) >> cell.anchor("bottom", 0.5)
        diag.text("Squads own delivery, chapters own craft standards, guilds share knowledge by interest.",
                  size=12).at(LABEL_X, guild_y + 80)
    return diag


def build_diagram(output_dir: Path | str = "examples/org") -> Path:
    return render_all(diagram(), output_dir, "05_squads_tribes_chapters_guilds")["svg"]


if __name__ == "__main__":
    build_diagram(Path(sys.argv[1]) if len(sys.argv) > 1 else Path("examples/org"))
