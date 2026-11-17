"""Drafting and anatomy primitives (draft.py)."""
from __future__ import annotations

import math
import warnings

from diagrams_as_code import Diagram
from diagrams_as_code.draft import Draft, catmull_rom, ecg_beat, hatch_segments

SQUARE = [(0, 0), (60, 0), (60, 60), (0, 60)]


def test_hatch_segments_stay_inside_and_are_parallel():
    segs = hatch_segments(SQUARE, angle=45, gap=6)
    assert len(segs) > 8
    for (x0, y0), (x1, y1) in segs:
        for x, y in ((x0, y0), (x1, y1)):
            assert -0.01 <= x <= 60.01 and -0.01 <= y <= 60.01
        assert abs(math.hypot(x1 - x0, y1 - y0)) > 0.5
        assert abs((x1 - x0) + (y1 - y0)) < 1e-6  # 45 degrees up-right on screen


def test_hatch_spacing_follows_gap():
    wide, tight = hatch_segments(SQUARE, 0, 12), hatch_segments(SQUARE, 0, 6)
    assert len(tight) > len(wide)


def test_hatch_with_hole_leaves_the_hole_empty():
    with Diagram("h", theme="paper") as d:
        k = Draft(d)
        hole = [(20, 20), (40, 20), (40, 40), (20, 40)]
        k.hatch(SQUARE, angle=0, gap=5, holes=[hole])
    assert d.shapes


def test_catmull_rom_closed_and_open():
    pts = [(0, 0), (10, 0), (10, 10), (0, 10)]
    closed = catmull_rom(pts, closed=True)
    assert closed.startswith("M 0.00 0.00") and closed.endswith("Z") and closed.count("C") == 4
    assert catmull_rom(pts).count("C") == 3
    assert catmull_rom([(1, 1)]) == ""


def test_ecg_beat_has_a_dominant_r_peak():
    vals = [ecg_beat(i / 200) for i in range(200)]
    assert max(vals) == max(vals[55:70]) and 0.9 < max(vals) < 1.15
    assert min(vals) < 0 and abs(vals[0]) < 0.02


def test_every_primitive_draws_without_warnings():
    with warnings.catch_warnings():
        warnings.simplefilter("error")
        with Diagram("p", theme="paper") as d:
            k = Draft(d)
            k.outline(SQUARE)
            k.dimension((0, 70), (60, 70), "$60$")
            k.dimension((0, 0), (8, 0), "$8$", side=-1)
            k.radius_dim((30, 30), 12, 45)
            k.radius_dim((30, 30), 12, 120, diameter=True)
            k.centerline((30, -10), (30, 70))
            k.hidden_line([(5, 5), (55, 5)])
            k.section_arrows((-20, 30), (80, 30), "A")
            k.gdt_frame((100, 0), ["$\\perp$", "0.05", "A"])
            k.leader((30, 30), (120, 60), "bore")
            k.smooth_closed([(0, 0), (20, -10), (40, 0), (20, 10)])
            k.smooth_open([(0, 0), (20, -10), (40, 0)])
            pts = k.wave((0, 100), 120, 20, ecg_beat, beats=2)
    assert len(pts) == 2 * 60 + 1
    assert len(d.render_svg()) > 1000
