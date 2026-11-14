"""Virtual address space of a 32-bit Linux process, with one stack frame enlarged.

The segments are drawn as one adjoining column, high addresses at the top.
Braces separate kernel space from user space, short arrows show which way the
stack and the heap grow, and the current stack frame is drawn again at a
larger scale beside the column.
"""
from __future__ import annotations

import sys
from pathlib import Path

from diagrams_as_code import Diagram, Style
from diagrams_as_code.output import render_all

X, W = 250.0, 190.0  # left edge and width of the column
SMALL = 11.0
MAPPED = Style(fill="#E4E4E8", font_size=13)
KERNEL = Style(fill="#C4C7D0", font_size=13)
FRAME = Style(fill="#9FA6B8", font_size=SMALL)
HOLE = Style(fill="#FFFFFF", dash="4,3", text_color="#666666", font_size=SMALL)
THIN = {"routing": "direct", "width": 0.75}

# (label, height, style), from the highest address down.
SEGMENTS = [
    ("**Kernel space**", 64, KERNEL),
    ("**Stack**", 46, MAPPED),
    ("frame of the running function", 22, FRAME),
    ("", 74, HOLE),
    ("**Memory-mapped region**\nshared libraries, mmap()", 54, MAPPED),
    ("", 74, HOLE),
    ("**Heap**", 46, MAPPED),
    ("**BSS** uninitialised data", 34, MAPPED),
    ("**Data** initialised data", 34, MAPPED),
    ("**Text** program code", 40, MAPPED),
    ("reserved", 26, HOLE),
]
# Addresses at the lower edge of a segment, by index into SEGMENTS.
ADDRESSES = {0: "0xC0000000", 2: "*%esp*", 4: "0x40000000", 5: "*brk*", 9: "0x08048000", 10: "0x00000000"}


def diagram() -> Diagram:
    with Diagram("Process memory layout", theme="paper") as diag:
        y, column, top = 60.0, [], {}
        diag.text("0xFFFFFFFF", size=SMALL).at(X - 10, y, anchor="right_center")
        for index, (label, height, style) in enumerate(SEGMENTS):
            top[index] = y
            column.append(diag.shape(label, W, height, style=style, fit_label=False).at(X, y))
            y += height
            if index in ADDRESSES:
                diag.text(ADDRESSES[index], size=SMALL).at(X - 10, y, anchor="right_center")
        kernel, stack, frame, gap_hi, mapped, gap_lo, heap = column[:7]

        # Growth arrows run into the unmapped holes, each with its remark beyond the tip.
        grow = {"routing": "direct", "width": 1.5}
        diag.connect(frame.anchor("bottom", 0.5), (X + W / 2, top[3] + 30), **grow)
        diag.text("grows down\n*unmapped*", size=SMALL, align="center", color="#555555").inside(
            gap_hi, "bottom_center", 0, -6)
        diag.connect(heap.anchor("top", 0.5), (X + W / 2, top[6] - 30), **grow)
        diag.text("*unmapped*\ngrows up", size=SMALL, align="center", color="#555555").inside(
            gap_lo, "top_center", 0, 6)

        diag.bracket("kernel space\n1 GiB", side="left").spanning(kernel, gap=92)
        diag.bracket("user space\n3 GiB", side="left").spanning(stack, column[-1], gap=92)

        # The stack frame again, enlarged.
        fx, fw, fh = X + W + 130, 180.0, 34.0
        diag.text("**One stack frame**", size=13).at(fx + fw / 2, 96, anchor="bottom_center")
        cells = [
            diag.shape(label, fw, fh, style=style, fit_label=False).at(fx, 104 + row * fh)
            for row, (label, style) in enumerate([
                ("arguments of the call", HOLE), ("return address", FRAME),
                ("saved frame pointer", FRAME), ("local variables", FRAME),
                ("free", HOLE),
            ])
        ]
        dashed = {**THIN, "style": "dashed", "arrow_head": False}
        diag.connect(frame.anchor("right", 0.0), cells[1].anchor("left", 0.0), **dashed)
        diag.connect(frame.anchor("right", 1.0), cells[3].anchor("left", 1.0), **dashed)

        note = {"size": SMALL, "head": "triangle", "anchor": "left_center"}
        right = fx + fw + 34
        diag.leader("*%ebp*", cells[2].anchor("right", 0.5), at=(right, 104 + 2.5 * fh), **note)
        diag.leader("*%esp*", (fx + fw, 104 + 4 * fh), at=(right, 104 + 4 * fh), **note)
        diag.text("$\\uparrow$ higher addresses", size=SMALL, color="#555555").at(
            right, 104 + 0.5 * fh, anchor="left_center")
        diag.text(
            "The shaded cells are pushed by one call. *%ebp* stays fixed for the "
            "whole call; *%esp* moves as locals are pushed and popped.",
            size=SMALL, max_width=fw, font="serif", italic=True,
        ).at(fx, 104 + 5 * fh + 14)
        diag.caption("**Figure 6:** Virtual address space of a process and the layout of one stack frame",
                     small_caps=True)
    return diag


def build_diagram(output_dir: Path | str = "output/technical") -> Path:
    return render_all(diagram(), output_dir, "06_memory_layout")["svg"]


if __name__ == "__main__":
    dest = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("output/technical")
    build_diagram(dest)
