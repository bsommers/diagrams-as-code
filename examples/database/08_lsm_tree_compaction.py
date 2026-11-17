"""A log-structured merge tree with levelled compaction (DATABASE domain).

Writes go to the write-ahead log and to a sorted in-memory memtable. A full
memtable is frozen and flushed as an L0 SSTable, so L0 files may overlap in
key range. Below L0 each level is one sorted run of non-overlapping files,
ten times larger than the level above; compaction picks a file, merges it
with the files it overlaps one level down, and drops shadowed versions.
Files are drawn along a common key axis, so overlap is visible.
"""
from __future__ import annotations

import sys
from pathlib import Path

from diagrams_as_code import Diagram, Style
from diagrams_as_code.output import render_all

KX, KW = 220.0, 560.0           # key axis: left edge and width
FILE = Style(fill="#FFFFFF", font_size=11)
PICKED = Style(fill="#9FA6B8", font_size=11)
HIT = Style(fill="#C9CDD6", font_size=11)
MEM = Style(fill="#E9E9EC", font_size=13)
FH = 26.0
BAND_W = 760.0
SMALL = 11.0
ARROW = {"routing": "direct", "width": 1.2, "head": "triangle", "arrow_size": 0.8}
# Level -> (y, size label, number of files)
LEVELS = {1: (400.0, "10 MB", 4), 2: (492.0, "100 MB", 8), 3: (570.0, "1 GB", 16)}
PICK = (1, 1)   # the L1 file being compacted: level, index


def diagram() -> Diagram:
    with Diagram("LSM-Tree Levelled Compaction", theme="paper") as diag:
        with diag.band("In memory", notes=["Sorted skip lists;", "reads check these first."],
                       min_width=BAND_W):
            memtable = diag.shape("**Memtable**\nmutable, 64 MB", 190, 50, style=MEM).at(KX, 100)
            frozen = diag.shape("**Immutable memtable**\nawaiting flush", 190, 50, style=MEM).at(KX + 300, 100)
            diag.text("*freeze*", size=SMALL).at(KX + 245, 120, anchor="bottom_center")
        with diag.band("On disk", notes=["L0 files overlap;", "each lower level is one",
                                         "sorted run of disjoint", "files, $T = 10\\times$ larger."],
                       min_width=BAND_W):
            wal = diag.shape("**Write-ahead log**  append-only", 260, 34,
                             style=Style(fill="#FFFFFF", font_size=12)).at(KX, 250)
            # L0: three flushed files with overlapping key ranges, on two sub-rows.
            l0 = [
                diag.shape("k: a–h", 210, FH, style=FILE).at(KX, 310),
                diag.shape("k: e–p", 230, FH, style=FILE).at(KX + 150, 340),
                diag.shape("k: m–z", 250, FH, style=FILE).at(KX + 310, 310),
            ]
            files = {}
            for level, (y, size, count) in LEVELS.items():
                pitch = KW / count
                for i in range(count):
                    style = FILE
                    if (level, i) == PICK:
                        style = PICKED
                    elif level == PICK[0] + 1 and i in (2, 3):
                        style = HIT
                    label = f"SST {i + 1}" if count <= 8 else ""
                    files[level, i] = diag.shape(label, pitch - 4, FH, style=style, fit_label=False).at(
                        KX + i * pitch, y)
            diag.text("**L0**  flushed", size=SMALL).at(KX - 14, 338, anchor="right_center")
            for level, (y, size, _) in LEVELS.items():
                diag.text(f"**L{level}**  {size}", size=SMALL).at(KX - 14, y + FH / 2, anchor="right_center")
            diag.text("*flush*", size=SMALL).at(KX + 460, 276, anchor="left_center")
            diag.text("*compact all of L0*", size=SMALL).at(KX + 232, 383, anchor="left_center")
            diag.leader("picked file and the L2 files it\noverlaps: merge-sort them and\ndrop shadowed versions",
                        files[2, 3].anchor("top", 0.75), at=(KX + 300, 434), anchor="top_left", head="circle")

        # The write path.
        diag.text("**put**$(k, v)$", size=13).at(20, 125, anchor="left_center")
        fork = diag.point(105, 125, dot=True)
        diag.connect((88, 125), fork, routing="direct", width=1.2, arrow_head=False)
        fork >> diag.edge(**ARROW) >> memtable.anchor("left", 0.5)
        diag.connect(fork, wal.anchor("left", 0.5), via=[(105, 267)], **ARROW)
        memtable.anchor("right", 0.5) >> diag.edge(**ARROW) >> frozen.anchor("left", 0.5)
        frozen.anchor("bottom", 0.8) >> diag.edge(**ARROW) >> l0[2].anchor("top", 142 / 250)

        # Compaction L0 -> L1 and the picked L1 file -> its overlap in L2.
        l0[1].anchor("bottom", 0.3) >> diag.edge(**ARROW) >> files[1, 1].anchor("top", 79 / 136)
        files[1, 1].anchor("bottom", 0.5) >> diag.edge(**ARROW) >> files[2, 2].anchor("top", 1.0)
        diag.text(
            "*get*$(k)$ checks the memtables, every L0 file, then at most one file per level; "
            "a Bloom filter per SSTable skips most of them. Leveling gives write amplification "
            "$W \\approx T \\cdot L$ for $L$ levels.",
            size=12, font="serif", italic=True, max_width=BAND_W,
        ).at(60, 624)
        diag.caption("**Figure 8:** Write path and levelled compaction in an LSM tree", small_caps=True)
    return diag


def build_diagram(output_dir: Path | str = "output/database") -> Path:
    return render_all(diagram(), output_dir, "08_lsm_tree_compaction")["svg"]


if __name__ == "__main__":
    dest = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("output/database")
    build_diagram(dest)
