"""The central dogma of molecular biology, worked through one three-codon gene.

DNA is replicated (semiconservative), transcribed into mRNA and translated into protein.
The sequences are consistent: the template strand is complementary to the coding strand, the
mRNA is complementary to the template (so it reads like the coding strand with U for T) and
each codon is looked up in the standard genetic code: AUG = Met, GCU = Ala, UGG = Trp.
"""
import sys
from pathlib import Path

from diagrams_as_code import Diagram, Style
from diagrams_as_code.output import render_all

INK = "#1F2F57"
BLUE, RED, GREEN, AMBER = "#2F5FA8", "#B03A3A", "#2E6B3F", "#8A5A00"
BASE_COLOR = {"A": RED, "T": BLUE, "U": BLUE, "G": GREEN, "C": AMBER}
PAIR = {"A": "T", "T": "A", "G": "C", "C": "G"}
RNA_PAIR = {"A": "U", "T": "A", "G": "C", "C": "G"}
CODING = "ATGGCTTGG"
CODON_TABLE = {"AUG": "Met", "GCU": "Ala", "UGG": "Trp"}
X0, DX = 260.0, 34.0
Y_DNA, Y_RNA, Y_PROT = 110.0, 300.0, 450.0


def letters(diag, seq, y, x0=X0):
    for i, b in enumerate(seq):
        diag.text(f"**{b}**", size=17, color=BASE_COLOR[b]).at(x0 + i * DX, y, anchor="center")


def diagram() -> Diagram:
    template = "".join(PAIR[b] for b in CODING)           # read 3' -> 5' under the coding strand
    mrna = "".join(RNA_PAIR[b] for b in template)
    codons = [mrna[i:i + 3] for i in range(0, len(mrna), 3)]
    end = X0 + (len(CODING) - 1) * DX
    with Diagram("Central dogma of molecular biology", theme="paper") as diag:
        # DNA double helix as a ladder of paired bases.
        letters(diag, CODING, Y_DNA - 20)
        letters(diag, template, Y_DNA + 20)
        for i in range(len(CODING)):
            x = X0 + i * DX
            diag.polyline([(x, Y_DNA - 8), (x, Y_DNA + 8)], style=Style(stroke="#8A93A8", stroke_width=1.4))
        for y, a, b in ((Y_DNA - 20, "5'", "3'"), (Y_DNA + 20, "3'", "5'")):
            diag.text(a, size=13).at(X0 - 24, y, anchor="right_center")
            diag.text(b, size=13).at(end + 24, y, anchor="left_center")
        diag.text("**DNA**\ncoding strand\ntemplate strand", size=13).at(40, Y_DNA, anchor="left_center")

        # Replication: a loop arrow leaving and re-entering the DNA.
        diag.path(f"M {X0 - 60} {Y_DNA - 36} C {X0 - 120} {Y_DNA - 100}, {X0 - 120} {Y_DNA + 100}, {X0 - 60} {Y_DNA + 36}",
                  style=Style(fill="none", stroke=INK, stroke_width=2.2))
        diag.connect((X0 - 70, Y_DNA + 44), (X0 - 56, Y_DNA + 34), routing="direct", width=2.2, color=INK, head="stealth")

        diag.text("**Replication**\nDNA polymerase", size=12).at(X0 - 100, Y_DNA + 78, anchor="top_center")

        # Transcription DNA -> mRNA.
        diag.connect((X0 + 70, Y_DNA + 50), (X0 + 70, Y_RNA - 40), routing="direct", width=2.6, color=INK, head="stealth")
        diag.text("**Transcription**\nRNA polymerase\nreads the template 3' to 5'", size=12).at(X0 + 82, (Y_DNA + Y_RNA) / 2 + 4, anchor="left_center")
        # Reverse transcription (a special transfer), dashed.
        diag.connect((end + 10, Y_RNA - 40), (end + 10, Y_DNA + 50), routing="direct", width=1.8, color=INK,
                     head="stealth", style="dashed")
        diag.text("*reverse transcription*\n(retroviruses)", size=12).at(end + 22, (Y_DNA + Y_RNA) / 2 + 4, anchor="left_center")

        # mRNA.
        letters(diag, mrna, Y_RNA)
        diag.text("5'", size=13).at(X0 - 24, Y_RNA, anchor="right_center")
        diag.text("3'", size=13).at(end + 24, Y_RNA, anchor="left_center")
        diag.text("**mRNA**\ncodons", size=13).at(40, Y_RNA, anchor="left_center")
        for k in range(len(codons)):
            x1, x2 = X0 + (3 * k) * DX - 15, X0 + (3 * k + 2) * DX + 15
            diag.polyline([(x1, Y_RNA + 22), (x1, Y_RNA + 28), (x2, Y_RNA + 28), (x2, Y_RNA + 22)],
                          style=Style(stroke=INK, stroke_width=1.2))

        # Translation mRNA -> protein.
        diag.connect((X0 + 70, Y_RNA + 40), (X0 + 70, Y_PROT - 40), routing="direct", width=2.6, color=INK, head="stealth")
        diag.text("**Translation**\nribosome + tRNA\n(next figure)", size=12).at(X0 + 82, (Y_RNA + Y_PROT) / 2 + 2, anchor="left_center")

        # Protein: one residue per codon, joined by peptide bonds.
        diag.text("**Protein**\nresidues", size=13).at(40, Y_PROT, anchor="left_center")
        for k, c in enumerate(codons):
            cx = X0 + (3 * k + 1) * DX
            diag.shape(CODON_TABLE[c], 78, 34, style=Style(fill="#DCE6F2", stroke=INK, stroke_width=1.6, radius=17),
                       fit_label=False).at(cx, Y_PROT, anchor="center")
            if k:
                diag.polyline([(cx - 3 * DX + 39, Y_PROT), (cx - 39, Y_PROT)], style=Style(stroke=INK, stroke_width=2.4))
        diag.text("N", size=12).at(X0 - 60, Y_PROT, anchor="right_center")
        diag.text("C", size=12).at(end + 60, Y_PROT, anchor="left_center")

        diag.text("Information flows DNA to RNA to protein; the dashed arrow is a special transfer.\n"
                  "Replication copies DNA with DNA polymerase; each daughter duplex keeps one old strand.",
                  size=12, color="#444444").at(40, 520, anchor="top_left")
        diag.caption(
            "**Figure 1:** The central dogma on one three-codon gene. The mRNA is complementary to the template strand, so it matches the coding strand with U in place of T;\n"
            "each codon specifies one amino acid (AUG Met, GCU Ala, UGG Trp)",
            small_caps=True,
        )
    return diag


def build_diagram(output_dir: Path | str = "examples/biology") -> Path:
    return render_all(diagram(), output_dir, "01_central_dogma")["svg"]


if __name__ == "__main__":
    build_diagram(Path(sys.argv[1]) if len(sys.argv) > 1 else Path("examples/biology"))
