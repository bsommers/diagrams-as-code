"""The backend-neutral drawing layer: paths, arcs, arrowheads, lengths."""
from __future__ import annotations

import math

import pytest

from diagrams_as_code import mm, pt, to_px
from diagrams_as_code.drawing import (
    PathItem,
    arrow_length,
    arrow_trim,
    arrowhead,
    commands_bbox,
    ellipse,
    parse_path,
    polyline,
    svg_d,
    translate,
)
from diagrams_as_code.geometry import Point


def test_relative_and_shorthand_commands_become_absolute_lines_and_cubics():
    cmds = parse_path("M 10 10 h 20 v 20 l -5 5 H 0 V 10 z")
    assert [c[0] for c in cmds] == ["M", "L", "L", "L", "L", "L", "Z"]
    assert cmds[1] == ("L", 30.0, 10.0) and cmds[3] == ("L", 25.0, 35.0)
    assert cmds[4] == ("L", 0.0, 35.0) and cmds[5] == ("L", 0.0, 10.0)


def test_implicit_lineto_after_moveto_and_compact_numbers():
    assert parse_path("M0,0 10,0 10-5") == (("M", 0.0, 0.0), ("L", 10.0, 0.0), ("L", 10.0, -5.0))


def test_quadratic_becomes_cubic_with_same_ends_and_peak():
    cmds = parse_path("M 0 0 Q 50 100 100 0")
    assert cmds[1][0] == "C" and cmds[1][5:] == (100.0, 0.0)
    assert commands_bbox(cmds).bottom == pytest.approx(50.0)  # a quadratic peaks halfway to its control


def test_smooth_curve_reflects_the_previous_control_point():
    cmds = parse_path("M 0 0 C 0 10 10 10 10 0 S 20 -10 20 0")
    assert cmds[2][1:3] == (10.0, -10.0)


@pytest.mark.parametrize("sweep, expected_y", [(0, 50.0), (1, -50.0)])
def test_half_circle_arc_goes_the_way_the_sweep_flag_says(sweep, expected_y):
    box = commands_bbox(parse_path(f"M 0 0 A 50 50 0 1 {sweep} 100 0"))
    assert (box.x, box.right) == (pytest.approx(0.0), pytest.approx(100.0))
    extreme = box.bottom if expected_y > 0 else box.top
    assert extreme == pytest.approx(expected_y, abs=0.05)


def test_arc_points_stay_on_the_circle():
    cmds = parse_path("M 100 50 A 50 50 0 0 1 50 100")
    (_, x1, y1, x2, y2, x, y) = cmds[1]
    # The curve's midpoint is on the circle centred (50, 50) to within a hair.
    mx = (100 + 3 * x1 + 3 * x2 + x) / 8
    my = (50 + 3 * y1 + 3 * y2 + y) / 8
    assert math.hypot(mx - 50, my - 50) == pytest.approx(50.0, abs=0.02)


def test_arc_with_too_small_radius_is_scaled_up_not_rejected():
    box = commands_bbox(parse_path("M 0 0 A 1 1 0 0 1 100 0"))
    assert box.width == pytest.approx(100.0)


@pytest.mark.parametrize("bad", ["10 10 L 5 5", "M 0 0 L 5", "M 0 0 X 5 5", "M 0 0 L a b"])
def test_malformed_path_data_is_rejected(bad):
    with pytest.raises(ValueError):
        parse_path(bad)


def test_translate_and_svg_round_trip():
    cmds = translate(polyline([(0, 0), (10, 0), (10, 10)], closed=True), 5, 7)
    assert svg_d(cmds) == "M 5.0 7.0 L 15.0 7.0 L 15.0 17.0 Z"
    assert parse_path(svg_d(cmds)) == cmds


def test_ellipse_bbox():
    box = commands_bbox(ellipse(50, 40, 30, 10))
    assert (box.x, box.y, box.width, box.height) == pytest.approx((20, 30, 60, 20))


def test_path_item_svg_omits_what_is_not_set():
    svg = PathItem(polyline([(0, 0), (4, 0)]), stroke="#000", stroke_width=1.5, dash="2,2").to_svg()
    assert 'fill="none"' in svg and 'stroke-width="1.5"' in svg and 'stroke-dasharray="2,2"' in svg
    assert "opacity" not in svg
    assert "stroke=" not in PathItem(polyline([(0, 0), (4, 0), (4, 4)], True), fill="#ccc").to_svg()


@pytest.mark.parametrize("style", ["triangle", "stealth", "open", "diamond", "circle", "bar"])
def test_arrowhead_has_its_point_at_the_tip_and_lies_behind_it(style):
    tip, length = Point(100.0, 50.0), 12.0
    items = arrowhead(tip, Point(1.0, 0.0), style, length, "#000", 1.0)
    assert items
    box = items[0].bbox()
    assert box.right == pytest.approx(100.0, abs=0.01)
    assert box.left >= 100.0 - length - 0.01
    assert box.center.y == pytest.approx(50.0, abs=0.01)


def test_arrowhead_follows_the_direction():
    box = arrowhead(Point(0.0, 0.0), Point(0.0, -2.0), "triangle", 10.0, "#000", 1.0)[0].bbox()
    assert (box.top, box.bottom) == pytest.approx((0.0, 10.0))


def test_none_draws_nothing_and_unknown_is_an_error():
    assert arrowhead(Point(0, 0), Point(1, 0), "none", 10, "#000", 1) == []
    with pytest.raises(ValueError):
        arrowhead(Point(0, 0), Point(1, 0), "fancy", 10, "#000", 1)


def test_arrow_size_scales_with_weight_but_has_a_floor():
    assert arrow_length(1.0) == arrow_length(0.5) == 9.0
    assert arrow_length(3.0) == 18.0 and arrow_length(3.0, 2.0) == 36.0
    assert arrow_trim("open", 10.0) == 0.0 and arrow_trim("triangle", 10.0) > 0.0


def test_lengths_with_units():
    assert to_px(12) == 12.0 and to_px("12") == 12.0 and to_px(" 12px ") == 12.0
    assert to_px("72pt") == pytest.approx(96.0) and to_px("1in") == 96.0
    assert to_px("25.4mm") == pytest.approx(96.0) and to_px("2.54cm") == pytest.approx(96.0)
    assert mm(25.4) == pytest.approx(96.0) and pt(72) == pytest.approx(96.0)
    for bad in (True, None, [1]):
        with pytest.raises(TypeError):
            to_px(bad)
    with pytest.raises(ValueError):
        to_px("12 furlongs")
