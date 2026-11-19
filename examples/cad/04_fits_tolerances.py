"""ISO 286 hole-basis fits for a 25 mm size: clearance, transition, interference.

Fundamental deviations are the standard values for the 18-30 mm range
(micrometres). Limits of size and the resulting fit extremes are computed
from them: clearance = hole - shaft, so a negative value is interference.
"""
from __future__ import annotations

import sys
from pathlib import Path

from diagrams_as_code import Diagram, Style
from diagrams_as_code.draft import Draft
from diagrams_as_code.output import render_all

NOMINAL = 25.0  # mm
HOLE = ("H7", 0, 21)  # lower, upper deviations in um
FITS = [
    ("Clearance", "H7/g6", ("g6", -20, -7), "#2E6B3F", "#DDEBDF"),
    ("Transition", "H7/k6", ("k6", 2, 15), "#9A6A12", "#F3E8CF"),
    ("Interference", "H7/p6", ("p6", 22, 35), "#9C2F2F", "#F1D9D9"),
]
UM = 5.0  # px per micrometre
Y0 = 295.0  # zero line
INK = "#1F2F57"


def y(um: float) -> float:
    return Y0 - um * UM


def box(x0, y0, x1, y1):
    return [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]


def diagram() -> Diagram:
    with Diagram("Fits and tolerances", theme="paper") as diag:
        k = Draft(diag)
        for i, (kind, name, shaft, col, tint) in enumerate(FITS):
            cx = 140.0 + i * 330.0
            sname, slo, shi = shaft
            hl, hu = HOLE[1], HOLE[2]
            # Panel frame, zero line, and the two tolerance zones.
            diag.polygon(box(cx - 140, 40, cx + 150, 490), style=Style(fill="none", stroke="#C5CBD8", stroke_width=0.8), z=-5)
            diag.text(f"{kind} fit  {name}", size=15, color=col).at(cx, 66, anchor="center")
            k.d.path(f"M {cx - 120} {Y0} L {cx + 130} {Y0}", style=Style(fill="none", stroke=INK, stroke_width=1.2))
            diag.text(f"$0$ = basic size $\\emptyset{NOMINAL:g}$", size=11).at(cx - 120, Y0 + 14, anchor="left_center")
            diag.polygon(box(cx - 78, y(hu), cx - 18, y(hl)), style=Style(fill="#DCE6F2", stroke=INK, stroke_width=1.8))
            diag.polygon(box(cx + 18, y(shi), cx + 78, y(slo)), style=Style(fill=tint, stroke=col, stroke_width=1.8))
            diag.text(f"hole {HOLE[0]}", size=12).at(cx - 48, y(hu) - 14, anchor="center")
            diag.text(f"shaft {sname}", size=12, color=col).at(cx + 48, y(shi) - 14, anchor="center")
            # Limit labels outside the zones.
            diag.text(f"${hu:+d}\\,\\mu$m", size=11).at(cx - 84, y(hu), anchor="right_center")
            diag.text(f"${hl:+d}\\,\\mu$m".replace("+0", "0"), size=11).at(cx - 84, y(hl) - 9, anchor="right_center")
            diag.text(f"${shi:+d}\\,\\mu$m", size=11, color=col).at(cx + 84, y(shi), anchor="left_center")
            diag.text(f"${slo:+d}\\,\\mu$m", size=11, color=col).at(cx + 84, y(slo), anchor="left_center")
            # Limits of size, computed.
            h_max, h_min = NOMINAL + (hu / 1000), NOMINAL + (hl / 1000)
            s_max, s_min = NOMINAL + (shi / 1000), NOMINAL + (slo / 1000)
            loosest, tightest = hu - slo, hl - shi
            if tightest >= 0:
                result = f"clearance {tightest} to {loosest} $\\mu$m"
            elif loosest <= 0:
                result = f"interference {-loosest} to {-tightest} $\\mu$m"
            else:
                result = f"{loosest} $\\mu$m clearance to {-tightest} $\\mu$m interference"
            diag.text(
                f"Hole {h_min:.3f} to {h_max:.3f} mm\nShaft {s_min:.3f} to {s_max:.3f} mm\n{result}",
                size=12).at(cx, 450, anchor="center")
        diag.caption(
            "**Figure 4:** ISO hole-basis fits at $\\emptyset25$ mm; the hole zone H7 stays fixed while the shaft zone moves from clearance (g6) through transition (k6) to interference (p6)",
            small_caps=True)
    return diag


def build_diagram(output_dir: Path | str = "examples/cad") -> Path:
    return render_all(diagram(), output_dir, "04_fits_tolerances")["svg"]


if __name__ == "__main__":
    dest = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("examples/cad")
    build_diagram(dest)
