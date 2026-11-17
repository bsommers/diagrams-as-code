"""Mind map: Operating Systems Study Notes (MIND_MAP domain, Moderate).

Revision notes for an operating-systems course. Six colour-coded chapters are
balanced left and right of the central subject; each chapter's block of
sub-topics is stacked so blocks never overlap, and the chapter pill sits at
the vertical centre of its block.
"""
from __future__ import annotations

import sys
from pathlib import Path

from diagrams_as_code import Diagram, Style
from diagrams_as_code.output import render_all

CX, CY = 650.0, 280.0
PITCH = 44.0  # vertical distance between neighbouring sub-topics
GAP = 30.0  # extra space between two chapter blocks on one side

CHAPTERS = {
    "left": [
        ("Processes", "#268BD2", ["Process Control Block", "CPU Scheduling (RR, MLFQ)", "Context Switch", "Threads vs Processes"]),
        ("Concurrency", "#DC322F", ["Mutexes & Semaphores", "Deadlock: 4 Conditions", "Monitors"]),
        ("Security", "#6C71C4", ["User vs Kernel Mode", "System Calls"]),
    ],
    "right": [
        ("Memory", "#2AA198", ["Paging & Page Tables", "TLB Hits and Misses", "Virtual Memory", "Page Replacement (LRU)"]),
        ("File Systems", "#B58900", ["Inodes & Directories", "Journaling", "VFS Layer"]),
        ("I/O Devices", "#D33682", ["Interrupts & DMA", "Device Drivers"]),
    ],
}


def diagram() -> Diagram:
    with Diagram("Operating Systems Concepts Study Notes", theme="solarized_light") as diag:
        root = diag.shape(
            "**Operating Systems**\nExam Revision", 210, 78,
            style=Style(radius=39, fill="#073642", stroke="#073642", text_color="#FDF6E3", font_size=18),
        ).at(CX, CY, anchor="center")

        for side, chapters in CHAPTERS.items():
            sign = -1 if side == "left" else 1
            inner = "right" if side == "left" else "left"
            total = sum(len(c[2]) * PITCH for c in chapters) + GAP * (len(chapters) - 1)
            top = CY - total / 2
            for label, colour, topics in chapters:
                block = len(topics) * PITCH
                by = top + block / 2
                chapter = diag.shape(
                    f"**{label}**", 140, 46,
                    style=Style(radius=23, fill=colour, stroke=colour, text_color="#FDF6E3", font_size=15),
                ).at(CX + sign * 250, by, anchor="center")
                diag.connect(root.anchor(side, 0.5), chapter.anchor(inner, 0.5),
                             routing="curve", color=colour, width=3.5, head="none")
                for i, topic in enumerate(topics):
                    leaf = diag.shape(
                        topic, 200, 32,
                        style=Style(radius=16, fill="#FDF6E3", stroke=colour, stroke_width=1.5, text_color="#586E75", font_size=13),
                    ).at(CX + sign * 490, top + PITCH * (i + 0.5), anchor="center")
                    diag.connect(chapter.anchor(side, 0.5), leaf.anchor(inner, 0.5),
                                 routing="curve", color=colour, width=1.8, head="none")
                top += block + GAP
    return diag


def build_diagram(output_dir: Path | str = "output/mind_map") -> Path:
    return render_all(diagram(), output_dir, "03_operating_systems_study_notes")["svg"]


if __name__ == "__main__":
    dest = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("output/mind_map")
    build_diagram(dest)
