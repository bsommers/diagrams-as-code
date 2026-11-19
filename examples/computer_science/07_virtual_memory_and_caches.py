"""Address translation and the cache hierarchy behind one load.

A 32-bit virtual address with 4 KiB pages splits into a 10-bit directory
index, a 10-bit table index and a 12-bit page offset. The TLB maps the virtual
page number to a physical one; on a miss the hardware walks the two-level
page table from CR3 and refills the TLB. The page offset passes through
untranslated. The physical address then goes down the cache hierarchy; an L1
set index and block offset that fit inside the page offset let the L1 be
indexed while the TLB is still translating (virtually indexed, physically
tagged).
"""
from __future__ import annotations

import sys
from pathlib import Path

from diagrams_as_code import Diagram, Style
from diagrams_as_code.output import render_all

INK = "#E6EEF8"
HOT = "#FFC857"
FIELD = Style(fill="#1E4A7A", font_size=12)
TABLE = Style(fill="#16385E", font_size=11, radius=0)
PICK = Style(fill=HOT, text_color="#10243D", font_size=11, radius=0)
UNIT = Style(fill="#1E4A7A", font_size=12)
LINE = {"routing": "direct", "width": 1.3}
WALK = {"width": 1.3, "color": HOT}
VA_Y, VA_H = 90.0, 44.0
VA = ((240.0, 400.0), (400.0, 560.0), (560.0, 720.0))
ROW_H, ROWS, TAB_Y = 24.0, 7, 240.0
TLB_X, TLB_Y, TLB_W, TLB_H = 800.0, 220.0, 240.0, 170.0
PA_Y = 460.0
CACHES = (("**L1-D** 32 KiB, 8-way", 200, "4 cycles"), ("**L2** 1 MiB, 16-way", 260, "~14 cycles"),
          ("**L3** 32 MiB, shared", 320, "~45 cycles"), ("**DRAM**", 380, "~200 cycles"))


def diagram() -> Diagram:
    with Diagram("Virtual memory translation and cache hierarchy", theme="blueprint") as diag:
        # Virtual address.
        diag.text("**Virtual address** (32 bits)", size=13).at(VA[0][0], VA_Y - 34, anchor="bottom_left")
        labels = ("**directory**\nbits 31-22", "**table**\nbits 21-12", "**page offset**\nbits 11-0")
        va = [diag.shape(text, b - a, VA_H, style=FIELD, fit_label=False).at(a, VA_Y)
              for (a, b), text in zip(VA, labels)]

        # The page walk, under the two index fields it uses.
        with diag.band("On a TLB miss: two-level page walk", min_width=560):
            cr3 = diag.shape("**CR3**\ndirectory base", 116, 46, style=UNIT).at(70, TAB_Y)
            tables = []
            for (a, b), pick, name in zip(VA[:2], (3, 5), ("page directory", "page table")):
                x = (a + b) / 2 - 60
                cells = [diag.shape("PTE" if i == pick else ("..." if i == ROWS - 1 else ""), 120, ROW_H,
                                    style=PICK if i == pick else TABLE, fit_label=False).at(x, TAB_Y + i * ROW_H)
                         for i in range(ROWS)]
                diag.text(name, size=11, italic=True).at(x + 60, TAB_Y + ROWS * ROW_H + 6, anchor="top_center")
                tables.append((cells, pick, x))
                diag.text("index", size=11, color=HOT).at((a + b) / 2 + 6, TAB_Y - 26, anchor="left_center")
        (dir_cells, dir_pick, dir_x), (pt_cells, pt_pick, pt_x) = tables
        cr3.anchor("right", 0.5) >> diag.edge(**WALK) >> dir_cells[0].anchor("left", 0.5)
        va[0].anchor("bottom", 0.5) >> diag.edge(**WALK) >> dir_cells[0].anchor("top", 0.5)
        va[1].anchor("bottom", 0.5) >> diag.edge(**WALK) >> pt_cells[0].anchor("top", 0.5)
        diag.connect(dir_cells[dir_pick].anchor("right", 0.5), pt_cells[0].anchor("left", 0.5),
                     via=[(dir_x + 140, TAB_Y + (dir_pick + 0.5) * ROW_H), (dir_x + 140, TAB_Y + ROW_H / 2)], **WALK)

        # The TLB, with three of its entries.
        tlb = diag.shape("**TLB**\nfully associative, 64 entries", TLB_W, TLB_H, label_position="top",
                         style=UNIT).at(TLB_X, TLB_Y)
        for i, entry in enumerate(("VPN 0x00C3A  →  PPN 0x1F2B0", "VPN 0x00401  →  PPN 0x07730", "...")):
            diag.shape(entry, TLB_W - 30, 26, style=TABLE, fit_label=False).inside(tlb, "top_left", 15, 64 + i * 32)
        diag.connect((VA[1][0], VA_Y), tlb.anchor("top", 0.5),
                     via=[(VA[1][0], VA_Y - 22), (TLB_X + TLB_W / 2, VA_Y - 22)], **LINE)
        diag.text("VPN (20 bits)", size=11).at(VA[2][1] + 12, VA_Y - 26, anchor="bottom_left")
        refill_y = TAB_Y + (pt_pick + 0.5) * ROW_H
        diag.connect(pt_cells[pt_pick].anchor("right", 0.5), (TLB_X, refill_y), routing="direct",
                     width=1.3, color=HOT, style="dashed")
        diag.text("refill", size=11, color=HOT).at((pt_x + 120 + TLB_X) / 2, refill_y - 4, anchor="bottom_center")

        # Physical address, and how the L1 reads it.
        pa = [diag.shape("**PPN**\n20 bits", 160, VA_H, style=FIELD, fit_label=False).at(TLB_X, PA_Y),
              diag.shape("**page offset**\n12 bits", 160, VA_H, style=FIELD, fit_label=False).at(TLB_X + 160, PA_Y)]
        diag.text("**Physical address**", size=13).at(TLB_X + 320, PA_Y - 6, anchor="bottom_right")
        tlb.anchor("bottom", 1 / 3) >> diag.edge(**LINE) >> pa[0].anchor("top", 0.5)
        diag.text("hit", size=11).at(TLB_X + 86, (TLB_Y + TLB_H + PA_Y) / 2, anchor="left_center")
        # The offset is not translated: it runs under the PA and into its right end.
        bypass_y, hook_x = PA_Y + VA_H + 16, TLB_X + 350
        diag.connect(va[2].anchor("bottom", 0.5), pa[1].anchor("right", 0.5),
                     via=[((VA[2][0] + VA[2][1]) / 2, bypass_y), (hook_x, bypass_y), (hook_x, PA_Y + VA_H / 2)],
                     **LINE)
        diag.text("page offset, untranslated", size=11, italic=True).at(
            (VA[2][0] + VA[2][1]) / 2 + 8, bypass_y - 4, anchor="bottom_left")
        split_y = PA_Y + VA_H + 40
        split = [diag.shape(text, w, 26, style=TABLE, fit_label=False).at(x, split_y)
                 for text, x, w in (("tag", TLB_X, 160), ("set (6)", TLB_X + 160, 80), ("byte (6)", TLB_X + 240, 80))]
        diag.text("as the L1 sees it", size=11, italic=True).at(TLB_X + 332, split_y + 13, anchor="left_center")

        # Cache hierarchy, widening as it gets slower.
        centre, y = TLB_X + 160, split_y + 70
        levels = []
        for label, width, latency in CACHES:
            level = diag.shape(label, width, 44, style=UNIT).at(centre, y, anchor="top_center")
            diag.text(latency, size=11, italic=True).at(centre + width / 2 + 12, y + 22, anchor="left_center")
            levels.append(level)
            y += 74
        diag.connect(split[0].anchor("bottom", 0.5), levels[0].anchor("top", 0.25), **LINE)
        for upper, lower in zip(levels, levels[1:]):
            upper.anchor("bottom", 0.35) >> diag.edge(**LINE) >> lower.anchor("top", 0.5 - 0.15 * upper.width / lower.width)
            lower.anchor("top", 0.5 + 0.15 * upper.width / lower.width) >> diag.edge(**LINE) >> upper.anchor("bottom", 0.65)
        diag.text("miss ↓  ↑ fill", size=11, italic=True).at(centre - 130, split_y + 70 + 44 + 15,
                                                            anchor="right_center")

        diag.text(
            "**Average memory access time**\n"
            "$\\mathrm{AMAT} = t_1 + m_1 (t_2 + m_2 (t_3 + m_3\\, t_{\\mathrm{mem}}))$\n"
            "$= 4 + 0.05 (14 + 0.3 (45 + 0.4 \\cdot 200)) \\approx 6.6$ cycles\n\n"
            "**Effective translation cost**\n"
            "$t_{\\mathrm{TLB}} + (1 - h_{\\mathrm{TLB}}) \\cdot 2\\, t_{\\mathrm{access}}$\n\n"
            "*Set index + byte offset = 12 bits = page offset,*\n*so the L1 lookup overlaps the TLB lookup.*",
            size=12,
        ).at(70, 560)
        diag.caption("**Figure 7:** Two-level address translation with a TLB, and the cache levels a physical "
                     "address passes through", small_caps=True)
    return diag


def build_diagram(output_dir: Path | str = "examples/computer_science") -> Path:
    return render_all(diagram(), output_dir, "07_virtual_memory_and_caches")["svg"]


if __name__ == "__main__":
    dest = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("examples/computer_science")
    build_diagram(dest)
