"""LAYOUT-01: the canvas is fitted to the content unless the user sizes it."""
from __future__ import annotations

from diagrams_as_code import Diagram
from diagrams_as_code.audit import audit_diagram
from diagrams_as_code.layout.pipeline import FIT_MARGIN_MIN, FRAME_X, FRAME_Y


def _two_boxes(**kwargs) -> Diagram:
    with Diagram("t", theme="monochrome", **kwargs) as d:
        a = d.shape("A", width=100, height=50).at(60, 80)
        b = d.shape("B", width=100, height=50).at(300, 80)
        a >> b
    d.solve()
    return d


def test_unsized_canvas_fits_content_with_mirrored_margin():
    d = _two_boxes()
    assert (d.width, d.height) == (400 + FRAME_X, 130 + FRAME_Y)
    assert "canvas_mostly_empty" not in audit_diagram(d)


def test_explicit_size_is_kept():
    d = _two_boxes(width=1200, height=800)
    assert (d.width, d.height) == (1200, 800)


def test_axes_are_fitted_independently():
    d = _two_boxes(width=900)
    assert (d.width, d.height) == (900, 130 + FRAME_Y)


def test_explicit_size_still_grows_when_content_would_be_clipped():
    d = _two_boxes(width=200, height=100)
    assert d.width == 400 + FRAME_X and d.height == 130 + FRAME_Y


def test_content_near_origin_keeps_a_minimum_margin():
    with Diagram("t", theme="monochrome") as d:
        d.shape("A", width=100, height=50).at(4, 4)
    d.solve()
    assert (d.width, d.height) == (104 + FIT_MARGIN_MIN, 54 + FIT_MARGIN_MIN)


def test_fit_is_stable_across_resolves_and_tracks_new_content():
    d = _two_boxes()
    first = (d.width, d.height)
    d.solve()
    assert (d.width, d.height) == first
    with d:
        d.shape("C", width=100, height=50).at(600, 300)
    d.solve()
    assert (d.width, d.height) == (700 + FRAME_X, 350 + FRAME_Y)


def test_setting_width_after_a_solve_pins_that_axis():
    d = _two_boxes()
    d.width = 1000.0
    d.solve()
    assert d.width == 1000.0 and d.height == 130 + FRAME_Y


def test_edge_badge_is_inside_the_fitted_canvas():
    with Diagram("t", theme="monochrome") as d:
        a = d.shape("A", width=60, height=40).at(60, 80)
        b = d.shape("B", width=60, height=40).at(60, 300)
        d.connect(a, b, label="a rather long edge label here")
    d.solve()
    assert "content_clipped" not in audit_diagram(d)
    assert d.width > 120 + FIT_MARGIN_MIN
