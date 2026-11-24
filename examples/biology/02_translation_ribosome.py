"""Translation at the ribosome: mRNA codons, charged tRNAs and the growing peptide.

The ribosome (large and small subunits) holds three tRNA sites. The mRNA 5'-AUG GCU UGG GAA-3'
is read 5' to 3'. Each tRNA carries the amino acid for its codon and its anticodon pairs
antiparallel with the codon (codon GCU pairs with anticodon 3'-CGA-5', written 5'-AGC-3').
The ribosome moves 5' to 3' along the mRNA; the peptide is on the tRNA in the P site and is
transferred onto the amino acid held in the A site.
"""
import sys
from pathlib import Path

from diagrams_as_code import Diagram, Style
from diagrams_as_code.output import render_all

INK = "#1F2F57"
BLUE, RED, GREEN, AMBER = "#2F5FA8", "#B03A3A", "#2E6B3F", "#8A5A00"
CODONS = ["AUG", "GCU", "UGG", "GAA"]
AA = {"AUG": "Met", "GCU": "Ala", "UGG": "Trp", "GAA": "Glu"}
COMP = {"A": "U", "U": "A", "G": "C", "C": "G"}
X0, W = 170.0, 120.0          # first codon left edge, codon width
Y_MRNA = 410.0
CODON_X = [X0 + i * W for i in range(len(CODONS))]


def anticodon_35(codon: str) -> str:
    """Anticodon written 3' to 5' under the codon (it pairs base for base)."""
    return "".join(COMP[b] for b in codon)


def diagram() -> Diagram:
    big_top, big_bot = 100.0, 300.0         # large subunit
    small_top, small_bot = 322.0, 366.0     # small subunit
    trna_top, trna_bot = 238.0, 332.0
    with Diagram("Translation at the ribosome", theme="paper") as diag:
        # mRNA as a ribbon of codon cells, 5' on the left.
        for i, c in enumerate(CODONS):
            diag.shape(c, W - 6, 30, style=Style(fill="#F4E9C8", stroke=INK, stroke_width=1.4, radius=3),
                       fit_label=False).at(CODON_X[i] + 3, Y_MRNA, anchor="top_left")
        diag.text("5'", size=14).at(X0 - 12, Y_MRNA + 15, anchor="right_center")
        diag.text("**mRNA**", size=13).at(X0 - 36, Y_MRNA + 15, anchor="right_center")
        diag.text("3'", size=14).at(X0 + 4 * W + 12, Y_MRNA + 15, anchor="left_center")

        # Ribosome: large subunit above, small subunit below; E, P and A sites span three codons.
        x_l, x_r = X0 - 8, X0 + 3 * W + 8
        diag.path(f"M {x_l} {big_bot} L {x_l} {big_top + 50} Q {x_l} {big_top} {x_l + 50} {big_top} "
                  f"L {x_r - 50} {big_top} Q {x_r} {big_top} {x_r} {big_top + 50} L {x_r} {big_bot} Z",
                  style=Style(fill="#DCE6F2", stroke=INK, stroke_width=1.8), z=-2)
        diag.path(f"M {x_l} {small_top} L {x_r} {small_top} L {x_r - 16} {small_bot} L {x_l + 16} {small_bot} Z",
                  style=Style(fill="#C4D4EA", stroke=INK, stroke_width=1.8), z=-2)
        diag.text("**Large subunit**", size=13).at(x_l + 14, big_top + 16, anchor="left_center")
        diag.text("**Small subunit**", size=12).at(x_l - 8, small_top + 22, anchor="right_center")

        # tRNAs: E (empty), P (holds the chain), A (incoming charged tRNA).
        sites = [("E", 0, "AUG"), ("P", 1, "GCU"), ("A", 2, "UGG")]
        for site, slot, codon in sites:
            cx = CODON_X[slot] + W / 2
            diag.path(f"M {cx - 22} {trna_top} Q {cx - 30} {(trna_top + trna_bot) / 2} {cx - 14} {trna_bot} "
                      f"L {cx + 14} {trna_bot} Q {cx + 30} {(trna_top + trna_bot) / 2} {cx + 22} {trna_top} Z",
                      style=Style(fill="#E9F2E1", stroke=GREEN, stroke_width=1.8, dash="5,3" if site == "E" else ""), z=0)
            for j, b in enumerate(anticodon_35(codon)):
                bx = cx - 30 + j * 30
                diag.text(f"**{b}**", size=14, color=RED).at(bx, small_top + 22, anchor="center")
                diag.polyline([(bx, small_bot + 3), (bx, Y_MRNA - 4)], style=Style(stroke="#8A93A8", stroke_width=1.4))
            diag.text(f"**{site}**", size=18, color=BLUE).at(cx - 52, big_bot - 18, anchor="center")
        # Amino acids: E released, P chain Met-Ala, A Trp.
        cp, ca, ce = CODON_X[1] + W / 2, CODON_X[2] + W / 2, CODON_X[0] + W / 2
        diag.text("empty tRNA\nleaves", size=11, color="#555555").at(ce, trna_top - 8, anchor="bottom_center")

        def residue(name, cx, cy):
            diag.shape(name, 54, 26, style=Style(fill="#F0C4C4", stroke=RED, stroke_width=1.6, radius=13),
                       fit_label=False).at(cx, cy, anchor="center")

        residue("Ala", cp, trna_top - 18)
        residue("Met", cp, trna_top - 54)
        diag.polyline([(cp, trna_top - 41), (cp, trna_top - 31)], style=Style(stroke=INK, stroke_width=2.6))
        residue("Trp", ca, trna_top - 18)
        diag.connect((cp + 32, trna_top - 54), (ca - 26, trna_top - 28), routing="direct", width=2.0, color=RED,
                     head="stealth", style="dashed")
        diag.text("peptidyl transfer", size=11, color=RED).at((cp + ca) / 2 + 14, trna_top - 66, anchor="bottom_center")

        # Ribosome movement and the next tRNA (ghost) waiting to enter.
        diag.connect((X0 + 4 * W - 30, Y_MRNA + 62), (X0 + 4 * W + 40, Y_MRNA + 62), routing="direct", width=2.2, color=INK, head="stealth")
        diag.text("ribosome moves 5' to 3'", size=12).at(X0 + 4 * W - 38, Y_MRNA + 62, anchor="right_center")
        nx = CODON_X[3] + W / 2
        diag.path(f"M {nx - 22} {trna_top + 30} Q {nx - 30} {trna_top + 62} {nx - 14} {trna_bot + 30} "
                  f"L {nx + 14} {trna_bot + 30} Q {nx + 30} {trna_top + 62} {nx + 22} {trna_top + 30} Z",
                  style=Style(fill="none", stroke="#8A93A8", stroke_width=1.4, dash="4,3"))
        diag.text("next tRNA: Glu\nanticodon 3'-CUU-5'", size=11, color="#555555").at(nx + 24, trna_top + 22, anchor="bottom_center")

        diag.text(
            "**Sites**  A aminoacyl (incoming charged tRNA)  |  P peptidyl (holds the chain)  |  E exit\n"
            "Anticodons are drawn 3' to 5' so they pair base for base under the codons.\n"
            "Codons: AUG Met, GCU Ala, UGG Trp, GAA Glu.",
            size=12, color="#333333").at(X0 - 120, Y_MRNA + 100, anchor="top_left")
        diag.caption(
            "**Figure 2:** Translation. Charged tRNAs pair their anticodons with mRNA codons in the A site, the ribosome catalyses peptide-bond formation\n"
            "and then advances one codon; the empty tRNA leaves from the E site",
            small_caps=True,
        )
    return diag


def build_diagram(output_dir: Path | str = "examples/biology") -> Path:
    return render_all(diagram(), output_dir, "02_translation_ribosome")["svg"]


if __name__ == "__main__":
    build_diagram(Path(sys.argv[1]) if len(sys.argv) > 1 else Path("examples/biology"))
