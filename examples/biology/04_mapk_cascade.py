"""The Ras-Raf-MEK-ERK (MAPK) signalling cascade with its inhibitors and feedback.

A growth factor dimerises its receptor tyrosine kinase; the adaptor Grb2 and the exchange factor SOS load Ras
with GTP; active Ras recruits Raf (MAPKKK), which phosphorylates MEK (MAPKK), which phosphorylates ERK (MAPK);
ERK enters the nucleus and activates transcription factors. Arrows are activation (the P badge marks a
phosphorylation); flat-ended bars are inhibition: RasGAP (Ras-GTP to Ras-GDP), the drugs vemurafenib (mutant
BRAF) and trametinib (MEK), the DUSP/MKP phosphatases acting on ERK, and ERK's own feedback onto SOS.
"""
import sys
from pathlib import Path

from diagrams_as_code import Diagram, Style
from diagrams_as_code.output import render_all

INK = "#1F2F57"
RED = "#B03A3A"
KINASE = Style(fill="#DCE6F2", stroke=INK, stroke_width=1.6, radius=8)
SMALL = Style(fill="#F4E9C8", stroke=INK, stroke_width=1.4, radius=8)
DRUG = Style(fill="#F0C4C4", stroke=RED, stroke_width=1.4, radius=8)
GENE = Style(fill="#E9F2E1", stroke="#2E6B3F", stroke_width=1.4, radius=8)
CX, W, H = 340.0, 170.0, 36.0
INH_X, INH_W = 640.0, 200.0
LEFT_X = 90.0


def band(x0, y0, w, h, r):
    """A rounded rectangle as a path (a backdrop, not a node)."""
    x1, y1 = x0 + w, y0 + h
    return (f"M {x0 + r} {y0} L {x1 - r} {y0} Q {x1} {y0} {x1} {y0 + r} L {x1} {y1 - r} Q {x1} {y1} {x1 - r} {y1} "
            f"L {x0 + r} {y1} Q {x0} {y1} {x0} {y1 - r} L {x0} {y0 + r} Q {x0} {y0} {x0 + r} {y0} Z")


def diagram() -> Diagram:
    with Diagram("MAPK signalling cascade", theme="paper") as diag:
        # Plasma membrane band and nuclear envelope.
        diag.path(band(LEFT_X - 50, 120, 640, 30, 4), style=Style(fill="#EFE3C2", stroke="#8A5A00", stroke_width=1.2), z=-2)
        diag.text("plasma membrane", size=11, color="#8A5A00").at(LEFT_X - 40, 152, anchor="top_left")
        diag.path(band(LEFT_X - 50, 612, 640, 130, 22), style=Style(fill="#F3F6FB", stroke=INK, stroke_width=1.4, dash="6,4"), z=-2)
        diag.text("**Nucleus**", size=13).at(LEFT_X - 36, 622, anchor="top_left")

        # Ligand and receptor dimer.
        egf = diag.shape("Growth factor (EGF)", W, H, style=SMALL, fit_label=False).at(CX, 66, anchor="center")
        rec_a = diag.shape("RTK", 70, 44, style=KINASE, fit_label=False).at(CX - 38, 135, anchor="center")
        rec_b = diag.shape("RTK", 70, 44, style=KINASE, fit_label=False).at(CX + 38, 135, anchor="center")
        diag.connect(egf, (CX, 112), routing="direct", width=2.0, color=INK, head="stealth")
        diag.text("binds and dimerises\nthe receptor", size=11, color="#333333").at(CX + 12, 99, anchor="left_center")
        diag.text("autophosphorylated Tyr\nrecruits Grb2", size=11, color="#333333").at(CX + 12, 182, anchor="left_center")

        # The cascade.
        grb = diag.shape("Grb2 / SOS (adaptor, GEF)", W + 20, H, style=SMALL, fit_label=False).at(CX, 225, anchor="center")
        ras = diag.shape("Ras  (GDP to GTP)", W, H, style=KINASE, fit_label=False).at(CX, 300, anchor="center")
        raf = diag.shape("Raf  (MAPKKK)", W, H, style=KINASE, fit_label=False).at(CX, 380, anchor="center")
        mek = diag.shape("MEK1/2  (MAPKK)", W, H, style=KINASE, fit_label=False).at(CX, 460, anchor="center")
        erk = diag.shape("ERK1/2  (MAPK)", W, H, style=KINASE, fit_label=False).at(CX, 540, anchor="center")
        tf = diag.shape("Elk-1, Myc, Fos (transcription factors)", 250, H, style=GENE, fit_label=False).at(CX, 676, anchor="center")
        genes = diag.shape("Cyclin D, growth genes", 170, H, style=GENE, fit_label=False).at(CX + 270, 676, anchor="center")
        diag.connect((CX, 157), grb, routing="direct", width=2.0, color=INK, head="stealth")
        for a, b, y, text in (
            (grb, ras, 262, "SOS swaps GDP for GTP"),
            (ras, raf, 340, "Ras-GTP recruits Raf"),
            (raf, mek, 420, "phosphorylates MEK (Ser/Ser)"),
            (mek, erk, 500, "phosphorylates ERK (Thr/Tyr)"),
        ):
            diag.connect(a, b, routing="direct", width=2.0, color=INK, head="stealth")
            diag.text(text, size=11, color="#333333").at(CX + 24, y, anchor="left_center")
        for y in (420, 500):  # phosphate badges on the two kinase steps
            diag.shape("P", 20, 20, style=Style(fill=RED, stroke=RED, stroke_width=1.0, radius=10, text_color="#FFFFFF"),
                       fit_label=False).at(CX - 14, y, anchor="center")
        diag.connect(erk, tf, routing="direct", width=2.0, color=INK, head="stealth")
        diag.text("enters the nucleus", size=11, color="#333333").at(CX + 24, 586, anchor="left_center")
        diag.connect(tf, genes, routing="direct", width=2.0, color=INK, head="stealth")
        diag.text("proliferation", size=11, color="#333333").at(CX + 270, 700, anchor="top_center")

        # Inhibitors: flat-ended bars.
        for label, target, y in (
            ("RasGAP\n(Ras-GTP to Ras-GDP)", ras, 300),
            ("Vemurafenib\n(mutant BRAF inhibitor)", raf, 380),
            ("Trametinib\n(MEK inhibitor)", mek, 460),
        ):
            box = diag.shape(label, INH_W, 44, style=DRUG, fit_label=False).at(INH_X, y, anchor="center")
            diag.connect(box.anchor("left", 0.5), (CX + W / 2 + 7, y), routing="direct", width=2.2, color=RED, head="bar")
        dusp = diag.shape("DUSP / MKP\n(phosphatase)", INH_W, 44, style=DRUG, fit_label=False).at(INH_X, 540, anchor="center")
        diag.connect(dusp.anchor("left", 0.5), (CX + W / 2 + 7, 540), routing="direct", width=2.2, color=RED, head="bar")
        # ERK feedback onto SOS (negative feedback), routed up the left side.
        fb_x = CX - W / 2 - 54
        diag.connect(erk.anchor("left", 0.5), (CX - (W + 20) / 2 - 7, 225), routing="direct", width=2.2, color=RED, head="bar",
                     via=[(fb_x, 540), (fb_x, 225)])
        diag.text("negative feedback:\nERK phosphorylates SOS", size=11, color=RED).at(fb_x - 8, 380, anchor="right_center")

        # Key.
        diag.connect((LEFT_X - 40, 780), (LEFT_X + 10, 780), routing="direct", width=2.0, color=INK, head="stealth")
        diag.text("activation / phosphorylation", size=11).at(LEFT_X + 20, 780, anchor="left_center")
        diag.connect((LEFT_X + 220, 780), (LEFT_X + 270, 780), routing="direct", width=2.2, color=RED, head="bar")
        diag.text("inhibition", size=11).at(LEFT_X + 280, 780, anchor="left_center")
        diag.caption(
            "**Figure 4:** The MAPK cascade: a three-kinase relay (Raf, MEK, ERK) amplifies a receptor signal into a transcriptional response.\n"
            "Red bar-headed lines mark inhibition by a GAP, drugs, a phosphatase and ERK's own negative feedback",
            small_caps=True,
        )
    return diag


def build_diagram(output_dir: Path | str = "examples/biology") -> Path:
    return render_all(diagram(), output_dir, "04_mapk_cascade")["svg"]


if __name__ == "__main__":
    build_diagram(Path(sys.argv[1]) if len(sys.argv) > 1 else Path("examples/biology"))
