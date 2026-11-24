"""Punnett squares: a monohybrid cross (Tt x Tt) and a dihybrid cross (RrYy x RrYy).

The squares are computed, not typed: each cell combines one gamete from each parent and orders the
alleles dominant first, then the genotype and phenotype ratios are counted from the cells.
Monohybrid: T (tall) is dominant to t (short), giving 1 TT : 2 Tt : 1 tt and 3 tall : 1 short.
Dihybrid: R (round) is dominant to r (wrinkled) and Y (yellow) to y (green); the two genes assort
independently, giving 9 round yellow : 3 round green : 3 wrinkled yellow : 1 wrinkled green.
"""
import itertools
import sys
from collections import Counter
from pathlib import Path

from diagrams_as_code import Diagram, Style
from diagrams_as_code.output import render_all

INK = "#1F2F57"
HEAD = Style(fill="#1F2F57", stroke="#FFFFFF", stroke_width=1.4, text_color="#FFFFFF")
MONO_FILL = {"tall": "#CFE6C4", "short": "#F4D9A8"}
DI_FILL = {
    "round yellow": "#FBF1B8", "round green": "#CFE6C4",
    "wrinkled yellow": "#F4D9A8", "wrinkled green": "#D8C6E6",
}


def order(pair):
    """Alleles of one gene, dominant (upper case) first."""
    return "".join(sorted(pair, key=lambda a: (a.islower(), a)))


def cross(gametes_a, gametes_b):
    """Genotype of each cell of the square (rows follow parent B, columns parent A)."""
    rows = []
    for gb in gametes_b:
        row = []
        for ga in gametes_a:
            genes = [order(ga[i] + gb[i]) for i in range(len(ga))]
            row.append("".join(genes))
        rows.append(row)
    return rows


def grid(diag, x0, y0, cw, ch, cols, rows_labels, cells, fills, size=14):
    """A header row, a header column and the body of the square."""
    diag.shape("", cw, ch, style=HEAD, fit_label=False).at(x0, y0, anchor="top_left")
    for j, g in enumerate(cols):
        diag.shape(f"**{g}**", cw, ch, style=HEAD, fit_label=False).at(x0 + (j + 1) * cw, y0, anchor="top_left")
    for i, g in enumerate(rows_labels):
        diag.shape(f"**{g}**", cw, ch, style=HEAD, fit_label=False).at(x0, y0 + (i + 1) * ch, anchor="top_left")
        for j, text in enumerate(cells[i]):
            diag.shape(text, cw, ch, style=Style(fill=fills[i][j], stroke="#8A93A8", stroke_width=1.2, font_size=size),
                       fit_label=False).at(x0 + (j + 1) * cw, y0 + (i + 1) * ch, anchor="top_left")


def swatch_row(diag, x, y, items):
    for k, (fill, text) in enumerate(items):
        diag.shape("", 16, 16, style=Style(fill=fill, stroke="#8A93A8", stroke_width=1.0), fit_label=False).at(x, y + k * 24, anchor="top_left")
        diag.text(text, size=12).at(x + 24, y + 8 + k * 24, anchor="left_center")


def diagram() -> Diagram:
    # ---- monohybrid -------------------------------------------------------
    gam = ["T", "t"]
    mono = cross(gam, gam)
    mono_pheno = [["tall" if "T" in c else "short" for c in row] for row in mono]
    mono_gen = Counter(c for row in mono for c in row)
    mono_ph = Counter(p for row in mono_pheno for p in row)
    # ---- dihybrid ---------------------------------------------------------
    dgam = ["".join(p) for p in itertools.product("Rr", "Yy")]  # RY, Ry, rY, ry
    di = cross(dgam, dgam)

    def phenotype(g):
        shape = "round" if "R" in g else "wrinkled"
        colour = "yellow" if "Y" in g else "green"
        return f"{shape} {colour}"

    di_pheno = [[phenotype(c) for c in row] for row in di]
    di_ph = Counter(p for row in di_pheno for p in row)

    with Diagram("Punnett squares", theme="paper") as diag:
        diag.text("**Monohybrid cross**  $Tt \\times Tt$", size=15).at(60, 78, anchor="top_left")
        diag.text("T tall is dominant to t short", size=12, color="#555555").at(60, 100, anchor="top_left")
        grid(diag, 60, 135, 90, 58, gam, gam, mono, [[MONO_FILL[p] for p in row] for row in mono_pheno], size=16)
        diag.text("Gametes of one parent across the top, of the other down the side.", size=11, color="#555555").at(60, 135 + 3 * 58 + 10, anchor="top_left")
        y = 135 + 3 * 58 + 44
        diag.text(f"**Genotypes** 1 TT : 2 Tt : 1 tt   (counted: {mono_gen['TT']} : {mono_gen['Tt']} : {mono_gen['tt']})", size=12).at(60, y, anchor="top_left")
        diag.text(f"**Phenotypes** 3 tall : 1 short   (counted: {mono_ph['tall']} : {mono_ph['short']})", size=12).at(60, y + 22, anchor="top_left")
        swatch_row(diag, 60, y + 56, [(MONO_FILL["tall"], "tall (TT, Tt)"), (MONO_FILL["short"], "short (tt)")])

        x0 = 440
        diag.text("**Dihybrid cross**  $RrYy \\times RrYy$", size=15).at(x0, 78, anchor="top_left")
        diag.text("R round > r wrinkled; Y yellow > y green; independent assortment", size=12, color="#555555").at(x0, 100, anchor="top_left")
        grid(diag, x0, 135, 84, 48, dgam, dgam, di, [[DI_FILL[p] for p in row] for row in di_pheno], size=13)
        y = 135 + 5 * 48 + 22
        diag.text(f"**Phenotypes** 9 : 3 : 3 : 1   (counted: {di_ph['round yellow']} : {di_ph['round green']} : "
                  f"{di_ph['wrinkled yellow']} : {di_ph['wrinkled green']})", size=12).at(x0, y, anchor="top_left")
        swatch_row(diag, x0, y + 30, [
            (DI_FILL["round yellow"], f"round yellow  ({di_ph['round yellow']}/16)"),
            (DI_FILL["round green"], f"round green  ({di_ph['round green']}/16)"),
            (DI_FILL["wrinkled yellow"], f"wrinkled yellow  ({di_ph['wrinkled yellow']}/16)"),
            (DI_FILL["wrinkled green"], f"wrinkled green  ({di_ph['wrinkled green']}/16)"),
        ])
        diag.caption(
            "**Figure 8:** Punnett squares. A heterozygous monohybrid cross gives a 3:1 phenotype ratio and a 1:2:1 genotype ratio;\n"
            "a dihybrid cross of double heterozygotes gives 9:3:3:1 because the two genes assort independently",
            small_caps=True,
        )
    return diag


def build_diagram(output_dir: Path | str = "examples/biology") -> Path:
    return render_all(diagram(), output_dir, "08_punnett_squares")["svg"]


if __name__ == "__main__":
    build_diagram(Path(sys.argv[1]) if len(sys.argv) > 1 else Path("examples/biology"))
