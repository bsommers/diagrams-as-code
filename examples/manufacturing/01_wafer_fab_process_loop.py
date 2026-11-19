"""Front-end wafer fab process loop, with a cross-section under each patterning step.

One mask layer of a CMOS front end is drawn as six steps along the top: film
deposition, resist coat, exposure, develop, etch and resist strip. Under each
step a cross-section shows the wafer at that point. The return path along the
bottom passes through the modules a wafer visits between patterning steps and
re-enters deposition for the next mask layer: the re-entrant flow that makes
a wafer fab unlike a straight assembly line.
"""
from __future__ import annotations

import sys
from pathlib import Path

from diagrams_as_code import Diagram, Style
from diagrams_as_code.output import render_all

X0, Y0 = 60.0, 90.0  # top-left of the first step box
W, H, GAP = 140.0, 52.0, 30.0  # step box size and the gap between steps
XS_TOP = Y0 + H + 26  # top of the cross-sections
SUB, FILM, RESIST = 18.0, 12.0, 14.0  # layer thicknesses in the cross-sections
BLOCK = Style(fill="#ECECEF", font_size=12)
SUBSTRATE = Style(fill="#B8B8C0", stroke_width=0.8)
OXIDE = Style(fill="#9DB8DA", stroke_width=0.8)
PHOTORESIST = Style(fill="#E7B36A", stroke_width=0.8)
EXPOSED = Style(fill="#F6E2BF", stroke_width=0.8, dash="2,2")
MASK = Style(fill="#333333", stroke="#333333")
LIGHT = Style(fill="none", stroke="#7A4FA0", stroke_width=1.0)

STEPS = [
    ("**1 Deposit film**", "CVD, ALD or oxidation"),
    ("**2 Coat resist**", "track: spin, soft bake"),
    ("**3 Expose**", "scanner: DUV / EUV"),
    ("**4 Develop**", "track: PEB, develop"),
    ("**5 Etch**", "plasma RIE"),
    ("**6 Strip resist**", "O$_2$ plasma ash"),
]
RETURN = [
    ("**Wet clean**", "particle / metal removal"),
    ("**Metrology & inspection**", "CD, overlay, defects"),
    ("**Ion implant + anneal**", "doping layers only"),
    ("**CMP**", "planarise before next film"),
]


def step_x(i: int) -> float:
    return X0 + i * (W + GAP)


def diagram() -> Diagram:
    with Diagram("Front-End Wafer Fab Re-entrant Process Loop", theme="paper") as diag:
        steps = [
            diag.shape(f"{title}\n{sub}", W, H, style=BLOCK).at(step_x(i), Y0)
            for i, (title, sub) in enumerate(STEPS)
        ]
        for a, b in zip(steps, steps[1:]):
            a >> diag.edge(width=1.2) >> b

        # Cross-sections: which layers each step leaves on the wafer.
        base = XS_TOP + 26 + RESIST + FILM + SUB  # bottom of every cross-section
        y_sub, y_film, y_res = base - SUB, base - SUB - FILM, base - SUB - FILM - RESIST
        open_l, open_r = 0.38, 0.62  # the patterned opening, as fractions of the width

        def rect(x: float, y: float, w: float, h: float, style: Style) -> None:
            diag.polygon([(x, y), (x + w, y), (x + w, y + h), (x, y + h)], style=style)

        def split(x: float, y: float, h: float, style: Style) -> None:
            rect(x, y, W * open_l, h, style)
            rect(x + W * open_r, y, W * (1 - open_r), h, style)

        for i in range(len(STEPS)):
            x = step_x(i)
            rect(x, y_sub, W, SUB, SUBSTRATE)
            if i <= 3:
                rect(x, y_film, W, FILM, OXIDE)
            else:
                split(x, y_film, FILM, OXIDE)
            if i in (1, 2):
                rect(x, y_res, W, RESIST, PHOTORESIST)
            if i == 2:
                rect(x + W * open_l, y_res, W * (open_r - open_l), RESIST, EXPOSED)
                # Reticle above the wafer and light through its clear window.
                split(x, XS_TOP, 5, MASK)
                for f in (0.44, 0.5, 0.56):
                    lx = x + W * f
                    diag.polyline([(lx, XS_TOP - 10), (lx, y_res - 3)], style=LIGHT)
            if i in (3, 4):
                split(x, y_res, RESIST, PHOTORESIST)

        # Return path: right to left under the cross-sections, back into step 1.
        y_ret = base + 58
        ret = []
        for k, (title, sub) in enumerate(RETURN):
            x = step_x(5) - k * (W + GAP) * 5 / 3 + 0
            ret.append(diag.shape(f"{title}\n{sub}", W + 20, H, style=BLOCK).at(x - 10, y_ret))
        right = step_x(5) + W + 36
        left = X0 - 30
        diag.connect(steps[-1].anchor("right", 0.5), ret[0].anchor("right", 0.5),
                     via=[(right, Y0 + H / 2), (right, y_ret + H / 2)], width=1.2)
        for a, b in zip(ret, ret[1:]):
            a.anchor("left", 0.5) >> diag.edge(width=1.2) >> b.anchor("right", 0.5)
        diag.connect(ret[-1].anchor("left", 0.5), steps[0].anchor("left", 0.5),
                     via=[(left, y_ret + H / 2), (left, Y0 + H / 2)], width=1.2, style="dashed")
        diag.text("next mask layer", size=11, italic=True).at(left - 6, (Y0 + y_ret + H) / 2, anchor="right_center")

        # Legend for the cross-section fills.
        ly = y_ret + H + 34
        for k, (name, style) in enumerate(
            (("silicon substrate", SUBSTRATE), ("film (SiO$_2$ / Si$_3$N$_4$)", OXIDE),
             ("photoresist", PHOTORESIST), ("exposed resist", EXPOSED), ("reticle chrome", MASK))
        ):
            lx = X0 + k * 200
            rect(lx, ly, 22, 12, style)
            diag.text(name, size=11).at(lx + 30, ly + 6, anchor="left_center")

        diag.caption(
            "**Figure 1:** One patterning layer of a wafer fab. The loop repeats for every mask level, "
            "several dozen times for an advanced logic device",
            small_caps=True,
        )
    return diag


def build_diagram(output_dir: Path | str = "examples/manufacturing") -> Path:
    return render_all(diagram(), output_dir, "01_wafer_fab_process_loop")["svg"]


if __name__ == "__main__":
    dest = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("examples/manufacturing")
    build_diagram(dest)
