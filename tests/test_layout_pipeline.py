from __future__ import annotations

import warnings

import pytest

from diagrams_as_code import Diagram
from diagrams_as_code.layout import LayoutWarning, export_layout


def _bounds(d: Diagram) -> dict[str, tuple[float, float, float, float]]:
    return {e.id: (e.bounds.x, e.bounds.y, e.bounds.width, e.bounds.height) for e in d.all_elements()}


def test_manual_is_the_default_and_leaves_unplaced_shapes_alone() -> None:
    with Diagram() as d:
        a = d.shape("A")
    assert d.layout == "manual"
    assert (a.bounds.x, a.bounds.y) == (0.0, 0.0)


def test_auto_chain_flows_left_to_right_from_the_frame_margin() -> None:
    with Diagram(layout="auto") as d:
        a, b, c = d.shape("A"), d.shape("B"), d.shape("C")
        a >> b >> c
    assert (a.bounds.x, a.bounds.y) == (60.0, 80.0)
    assert a.bounds.right < b.bounds.x < b.bounds.right < c.bounds.x
    assert a.bounds.y == b.bounds.y == c.bounds.y


def test_auto_top_to_bottom() -> None:
    with Diagram(layout="auto", direction="TB") as d:
        a, b = d.shape("A"), d.shape("B")
        a >> b
    assert a.bounds.x == b.bounds.x
    assert a.bounds.bottom < b.bounds.y


def test_groups_are_laid_out_inside_then_placed_as_blocks() -> None:
    with Diagram(layout="auto") as d:
        with d.group("Left") as left:
            a1, a2 = d.shape("A1"), d.shape("A2")
            a1 >> a2
        with d.group("Right") as right:
            b1 = d.shape("B1")
        a2 >> b1
    assert left.bounds.right < right.bounds.x
    for child in (a1, a2):
        assert left.bounds.x < child.bounds.x and child.bounds.right < left.bounds.right
    assert a1.bounds.y > left.bounds.y + left.header_height


def test_pinned_shapes_stay_put_and_can_anchor_to_auto_ones() -> None:
    with Diagram(layout="auto") as d:
        a, b = d.shape("A"), d.shape("B")
        p = d.shape("P").at(900, 600)
        c = d.shape("C").below(b, margin=30, align="left")
        a >> b
    assert (p.bounds.x, p.bounds.y) == (900.0, 600.0)
    assert (c.bounds.x, c.bounds.y) == (b.bounds.x, b.bounds.bottom + 30)


def test_overlap_between_pinned_and_auto_is_warned() -> None:
    with pytest.warns(LayoutWarning, match="'P'.*'A'"):
        with Diagram(layout="auto") as d:
            d.shape("A")
            d.shape("P").at(70, 90)


def test_no_warning_when_nothing_overlaps() -> None:
    with warnings.catch_warnings():
        warnings.simplefilter("error", LayoutWarning)
        with Diagram(layout="auto") as d:
            a, b = d.shape("A"), d.shape("B")
            a >> b


def test_canvas_grows_to_fit_but_never_shrinks() -> None:
    with Diagram(layout="auto", width=400, height=300) as d:
        shapes = [d.shape(f"S{i}") for i in range(8)]
        for s, t in zip(shapes, shapes[1:]):
            s >> t
    assert d.width == shapes[-1].bounds.right + 60.0
    assert d.height == 300.0


def test_solve_is_idempotent() -> None:
    with warnings.catch_warnings():
        warnings.simplefilter("error", LayoutWarning)
        with Diagram(layout="auto") as d:
            with d.group("G"):
                a, b = d.shape("A"), d.shape("B")
                a >> b
            c = d.shape("C").right_of(b, margin=40)
        first = _bounds(d)
        d.solve()
    assert _bounds(d) == first


def test_manual_width_change_persists_across_resolve() -> None:
    with Diagram() as d:
        d.shape("A")
    d.width = 2000.0
    d.solve()
    assert d.width == 2000.0


def test_auto_user_width_larger_than_content_is_kept() -> None:
    with Diagram(layout="auto") as d:
        a, b = d.shape("A"), d.shape("B")
        a >> b
    d.width = 5000.0
    d.solve()
    assert d.width == 5000.0


def test_configure_switches_layout_and_resolves_on_render() -> None:
    with Diagram() as d:
        a, b = d.shape("A"), d.shape("B")
        a >> b
    d.configure(layout="auto")
    d.render_svg()
    assert a.bounds.right < b.bounds.x


def test_invalid_layout_options() -> None:
    with pytest.raises(ValueError, match="layout"):
        Diagram(layout="grid")
    with pytest.raises(ValueError, match="direction"):
        Diagram(direction="RL")


def test_a_layout_file_grows_the_canvas_in_manual_mode(tmp_path) -> None:
    with Diagram(layout="auto", width=400, height=300) as auto:
        a, b, c = auto.shape("A"), auto.shape("B"), auto.shape("C")
        a >> b >> c
    path = export_layout(auto, tmp_path / "chain.layout.json")

    with Diagram(width=400, height=300, layout_file=path) as replay:
        x, y, z = replay.shape("A"), replay.shape("B"), replay.shape("C")
        x >> y >> z

    assert (z.bounds.x, z.bounds.y) == (c.bounds.x, c.bounds.y)
    assert (replay.width, replay.height) == (auto.width, auto.height)
    assert z.bounds.right <= replay.width


def test_manual_canvas_grows_to_fit_content_placed_past_it() -> None:
    """Hand-placed content outside the declared canvas used to be clipped."""
    with Diagram(width=400, height=300) as d:
        a = d.shape("A").at(900, 700)
    assert d.width == a.bounds.right + 60.0
    assert d.height == a.bounds.bottom + 80.0


def test_canvas_that_already_fits_is_left_alone() -> None:
    with Diagram(width=400, height=300) as d:
        d.shape("A").at(60, 80)
    assert (d.width, d.height) == (400.0, 300.0)


def test_group_keeps_a_child_anchored_to_a_shape_outside_it() -> None:
    with warnings.catch_warnings():
        warnings.simplefilter("error", LayoutWarning)
        with Diagram(layout="auto", width=900, height=500) as d:
            anchor = d.shape("Anchor").at(700, 400)
            with d.group("G") as g:
                inside = d.shape("Inside").right_of(anchor, margin=10)
                other = d.shape("Other")
            inside >> other
    assert (inside.bounds.x, inside.bounds.y) == (anchor.bounds.right + 10.0, anchor.bounds.y)
    assert g.bounds.intersects(inside.bounds)
