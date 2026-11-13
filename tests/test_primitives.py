"""PRIM-01..04, 08, 09: text, captions, brackets, outlines, bands, nesting, z-order, arranging."""
from __future__ import annotations

import warnings

import pytest

from diagrams_as_code import (
    Band,
    Bracket,
    Caption,
    Diagram,
    Path,
    Polygon,
    Polyline,
    Style,
    Text,
    align,
    distribute,
)
from diagrams_as_code.audit import audit_diagram
from diagrams_as_code.text import TextStyle, layout


def _block(svg: str, element_id: str) -> str:
    return svg[svg.index(f'<g id="{element_id}"'):].split("</g>", 1)[0]


# ------------------------------------------------------------------ PRIM-01 text


def test_text_is_exactly_the_size_of_its_text_and_has_no_box():
    with Diagram("t", theme="paper") as d:
        note = d.text("Hello **world**", id="note", size=14).at(40, 50)
    want = layout("Hello **world**", TextStyle(size=14))
    assert (note.bounds.width, note.bounds.height) == pytest.approx((want.width, want.height))
    block = _block(d.render_svg(), "note")
    assert "<rect" not in block and "world" in block and 'font-weight="700"' in block


def test_text_wraps_aligns_and_pads():
    left = Text("a", "one two three four five six", max_width=80)
    assert left.bounds.width <= 80 and left.bounds.height > 30
    padded = Text("b", "label", padding=4)
    bare = Text("c", "label")
    assert padded.bounds.width == pytest.approx(bare.bounds.width + 8)
    with Diagram("t", theme="paper") as d:
        right = d.add(Text("r", "right", align="right")).at(100, 20)
        mid = d.add(Text("m", "mid", align="center")).at(100, 60)
    svg = d.render_svg()
    assert 'text-anchor="end"' in _block(svg, "r") and f'x="{round(right.bounds.right, 2):g}"' in _block(svg, "r")
    assert 'text-anchor="middle"' in _block(svg, "m")


def test_serif_text_uses_the_theme_serif_stack_and_pins_its_width():
    with Diagram("t", theme="paper") as d:
        d.text("remark", id="s", font="serif", italic=True).at(10, 10)
    block = _block(d.render_svg(), "s")
    assert "serif" in block and "Times" in block and "textLength" in block and 'font-style="italic"' in block


def test_text_takes_math_and_resizes_when_its_text_changes():
    with Diagram("t", theme="paper") as d:
        t = d.text("$x_i$", id="m").at(10, 10)
    assert "<path" in _block(d.render_svg(), "m")  # math is drawn as outlines
    before = t.bounds.width
    t.label = "a much longer line of text"
    d.solve()
    assert t.bounds.width > before


@pytest.mark.parametrize("kwargs", [{"align": "justify"}, {"font": "comic"}])
def test_text_rejects_unknown_options(kwargs):
    with pytest.raises(ValueError):
        Text("x", "y", **kwargs)


def test_text_is_an_obstacle_but_not_a_component():
    with Diagram("t", theme="paper") as d:
        a = d.shape("A").at(40, 100)
        b = d.shape("B").at(400, 100)
        d.text("do not cross this note", id="note").at(190, 121)
        a >> b
    assert not audit_diagram(d)
    assert [i["label"] for i in d.bom.items()] == ["A", "B"]


# --------------------------------------------------------------- PRIM-01 caption


def test_caption_is_centred_under_everything_and_the_canvas_holds_it():
    with Diagram("t", theme="paper") as d:
        a = d.shape("A").at(60, 60)
        b = d.shape("B").at(400, 200)
        cap = d.caption("**Figure 1:** A and B")
    assert cap.bounds.center.x == pytest.approx((a.bounds.left + b.bounds.right) / 2)
    assert cap.bounds.top == pytest.approx(b.bounds.bottom + cap.gap)
    assert d.height >= cap.bounds.bottom and d.width >= cap.bounds.right
    assert not audit_diagram(d)


def test_caption_clears_labels_drawn_outside_their_shape():
    with Diagram("t", theme="paper") as d:
        box = d.cuboid("a label under the solid").at(60, 60)
        cap = d.caption("Figure")
    assert cap.bounds.top > box.bounds.bottom + cap.gap  # the label, not the solid, sets the gap


def test_positioned_caption_stays_put_and_auto_layout_ignores_captions():
    with Diagram("t", theme="paper") as d:
        d.shape("A").at(60, 60)
        cap = d.caption("Figure").at(300, 20)
    assert (cap.bounds.x, cap.bounds.y) == (300, 20)
    with warnings.catch_warnings():
        warnings.simplefilter("error")
        with Diagram("t", theme="paper", layout="auto") as d:
            a, b = d.shape("A"), d.shape("B")
            a >> b
            cap = d.caption("Figure")
    assert cap.bounds.top > max(a.bounds.bottom, b.bounds.bottom)
    assert a.bounds.y == b.bounds.y  # the caption was not laid out as a third node


def test_caption_is_serif_small_caps_on_request_and_edges_may_pass_it():
    cap = Caption("c", "Figure 2", small_caps=True)
    assert cap.font == "serif" and cap.obstacle is False and cap.block.lines[0].runs[0].text == "FIGURE 2"


# -------------------------------------------------------------- PRIM-01 bracket


@pytest.mark.parametrize("side", ["left", "right", "top", "bottom"])
def test_bracket_spans_its_targets_on_its_side(side):
    with Diagram("t", theme="paper") as d:
        a = d.shape("A", 100, 40).at(200, 200)
        b = d.shape("B", 100, 40).at(260, 300)
        br = d.bracket(side=side).spanning(a, b, gap=10)
    box = a.bounds.union(b.bounds)
    if side in ("left", "right"):
        assert br.length == pytest.approx(box.height) and br.bounds.top == pytest.approx(box.top)
        assert (br.bounds.left == pytest.approx(box.right + 10)) if side == "right" else (
            br.bounds.right == pytest.approx(box.left - 10))
    else:
        assert br.length == pytest.approx(box.width) and br.bounds.left == pytest.approx(box.left)
        assert (br.bounds.top == pytest.approx(box.bottom + 10)) if side == "bottom" else (
            br.bounds.bottom == pytest.approx(box.top - 10))


@pytest.mark.parametrize("shape", Bracket.SHAPES)
def test_bracket_outline_opens_towards_its_content(shape):
    with Diagram("t", theme="paper") as d:
        br = d.add(Bracket("br", side="right", shape=shape, length=100, depth=10)).at(50, 20)
    item = br.draw(Style(stroke="#000", stroke_width=1.0), d.theme)[0]
    cmds = item.commands
    assert cmds[0][1:] == (50.0, 20.0) and cmds[-1][-2:] == (50.0, 120.0)  # both tips on the content side
    assert item.bbox().right == pytest.approx(60.0, abs=0.2) and item.fill is None


def test_bracket_label_sits_beyond_the_bracket_and_counts_in_its_size():
    plain = Bracket("p", side="right", length=100)
    named = Bracket("n", "three states", side="right", length=100)
    assert named.bounds.width > plain.bounds.width and named.bounds.height == plain.bounds.height
    under = Bracket("u", "wide label under a short bracket", side="bottom", length=40)
    assert under.bounds.width > 40 and under.length == 40
    with pytest.raises(ValueError):
        Bracket("x", side="diagonal")
    with pytest.raises(ValueError):
        Bracket("x", shape="wavy")


# -------------------------------------------------------- PRIM-02 outlines


def test_polygon_is_drawn_where_its_points_say_until_it_is_moved():
    pts = [(100, 80), (160, 80), (130, 20)]
    with Diagram("t", theme="paper") as d:
        fixed = d.polygon(pts, id="fixed")
        moved = d.polygon(pts, id="moved").at(300, 200)
    assert (fixed.bounds.x, fixed.bounds.y, fixed.bounds.width, fixed.bounds.height) == (100, 20, 60, 60)
    assert (moved.bounds.x, moved.bounds.y) == (300, 200)
    svg = d.render_svg()
    assert 'd="M 100 80 L 160 80 L 130 20 Z"' in _block(svg, "fixed")
    assert 'd="M 300 260 L 360 260 L 330 200 Z"' in _block(svg, "moved")


def test_polygon_is_filled_polyline_is_not_and_styles_apply():
    with Diagram("t", theme="paper") as d:
        d.polygon([(0, 0), (40, 0), (20, 30)], id="poly", style=Style(fill="#EEE", dash="4,2", fill_opacity=0.5)).at(50, 50)
        d.polyline([(0, 0), (40, 0), (20, 30)], id="line", style=Style(fill="#EEE", stroke_width=3)).at(150, 50)
    svg = d.render_svg()
    poly, line = _block(svg, "poly"), _block(svg, "line")
    assert 'fill="#EEE"' in poly and 'stroke-dasharray="4,2"' in poly and 'fill-opacity="0.5"' in poly
    assert 'fill="none"' in line and 'stroke-width="3"' in line and " Z" not in line


def test_path_takes_svg_path_data_with_curves_and_a_centred_label():
    with Diagram("t", theme="paper") as d:
        p = d.path("M 0 40 A 60 60 0 0 1 100 40 A 60 60 0 0 1 0 40 Z", "lens", id="lens").at(50, 50)
    assert p.bounds.width == pytest.approx(100.0)
    assert p.bounds.height == pytest.approx(2 * (60 - (60**2 - 50**2) ** 0.5), abs=0.05)
    block = _block(d.render_svg(), "lens")
    assert " C " in block and ">lens</text>" in block


def test_outlines_reject_too_few_points_and_are_pinned_under_auto_layout():
    with pytest.raises(ValueError):
        Polygon("p", [(0, 0), (1, 1)])
    with pytest.raises(ValueError):
        Polyline("p", [(0, 0)])
    with pytest.raises(ValueError):
        Path("p", "")
    with Diagram("t", theme="paper", layout="auto") as d:
        a, b = d.shape("A"), d.shape("B")
        a >> b
        tri = d.polygon([(500, 400), (560, 400), (530, 340)], obstacle=False)
    assert (tri.bounds.x, tri.bounds.y) == (500, 340)


def test_shapes_can_be_placed_relative_to_an_outline_and_connected_to_it():
    with Diagram("t", theme="paper") as d:
        tri = d.polygon([(0, 60), (60, 60), (30, 0)]).at(50, 50)
        box = d.shape("B").right_of(tri, margin=80)
        tri >> box
    assert box.bounds.left == pytest.approx(tri.bounds.right + 80)
    assert not audit_diagram(d)


# ------------------------------------------------------------------ PRIM-03 band


def test_band_is_a_dashed_square_unfilled_frame_with_a_bold_title():
    with Diagram("t", theme="iiot_dark_gold") as d:
        with d.band("Runtime layer", id="rt"):
            d.shape("A").at(100, 100)
    block = _block(d.render_svg(), "rt")
    assert 'rx="0"' in block and 'fill="none"' in block and 'stroke-dasharray="6,4"' in block
    assert "Runtime layer" in block and 'font-weight="700"' in block


def test_band_notes_get_their_own_column_outside_the_content():
    def build(**kwargs):
        with Diagram("t", theme="paper") as d:
            with d.band("Layer", id="band", **kwargs) as band:
                shape = d.shape("A", 120, 50).at(100, 100)
        return d, band, shape

    _, bare, _ = build()
    d, right, shape = build(notes=["first note", "a second, longer note that wraps"], note_width=120)
    assert right.bounds.width == pytest.approx(bare.bounds.width + 120 + right.padding)
    assert right.bounds.left == pytest.approx(bare.bounds.left)
    items = right.note_items(d.theme)
    assert len(items) == 2 and all(i.bbox().left >= shape.bounds.right + right.padding - 0.01 for i in items)
    assert all(i.bbox().right <= right.bounds.right - right.padding + 0.01 for i in items)
    assert items[1].bbox().top >= items[0].bbox().bottom
    assert "first note" in _block(d.render_svg(), "band") and 'font-style="italic"' in _block(d.render_svg(), "band")

    d, left, shape = build(notes="on the left", note_side="left", note_width=120)
    assert left.bounds.left == pytest.approx(shape.bounds.left - 120 - 2 * left.padding)
    assert left.note_items(d.theme)[0].bbox().right <= shape.bounds.left - left.padding + 0.01


def test_band_min_size_and_tall_notes_grow_it():
    with Diagram("t", theme="paper") as d:
        with d.band("One", min_width=500, min_height=200) as one:
            d.shape("A").at(100, 100)
        with d.band("Two", notes=["note " * 40], note_width=100) as two:
            d.shape("B").at(100, 500)
    assert (one.bounds.width, one.bounds.height) == (500, 200)
    notes = two.note_items(d.theme)
    assert notes[0].bbox().bottom <= two.bounds.bottom
    assert not audit_diagram(d)
    assert isinstance(two, Band) and two.note("more") is two
    with pytest.raises(ValueError):
        Band("b", "x", note_side="top")


def test_band_style_can_be_overridden_and_bands_stack():
    with Diagram("t", theme="paper") as d:
        with d.band("Top", id="top", style=Style(dash="2,2", fill="#FAFAFA")) as top:
            d.shape("A").at(100, 100)
        with d.band("Bottom") as bottom:
            d.shape("B")
        bottom.below(top, margin=30)
    assert bottom.bounds.top == pytest.approx(top.bounds.bottom + 30)
    block = _block(d.render_svg(), "top")
    assert 'stroke-dasharray="2,2"' in block and 'fill="#FAFAFA"' in block


# --------------------------------------------------- PRIM-04 nesting, double


def test_nested_shape_is_pinned_to_its_container_and_moves_with_it():
    with Diagram("t", theme="paper") as d:
        outer = d.shape("Outer", 300, 200, label_position="top").at(100, 100)
        centred = d.shape("C", 80, 40).inside(outer)
        corner = d.shape("K", 80, 40).inside(outer, "top_left", 10, 30)
        low = d.shape("L", 80, 40).inside(outer, "bottom_right", -10, -10)
    assert centred.bounds.center == outer.bounds.center
    assert (corner.bounds.x, corner.bounds.y) == (110, 130)
    assert (low.bounds.right, low.bounds.bottom) == (390, 290)
    assert centred.parent is outer and outer.children == [centred, corner, low]
    outer.move_to(400, 300)
    d.solve()
    assert (corner.bounds.x, corner.bounds.y) == (410, 330)
    assert not audit_diagram(d)


def test_nesting_inside_a_group_and_three_levels_deep():
    with Diagram("t", theme="paper") as d:
        with d.group("G") as g:
            outer = d.shape("Outer", 300, 220, label_position="top").at(100, 100)
            mid = d.shape("Mid", 200, 120, label_position="top").inside(outer, "bottom_center", 0, -20)
            leaf = d.shape("Leaf", 90, 40).inside(mid, "bottom_center", 0, -15)
    assert g.children == [outer]  # nested shapes belong to their container, not the group
    assert g.bounds.left == pytest.approx(outer.bounds.left - g.padding)
    assert mid.bounds.bottom == outer.bounds.bottom - 20 and leaf.bounds.bottom == mid.bounds.bottom - 15
    assert not audit_diagram(d)


def test_cannot_nest_a_shape_in_itself_or_its_descendant():
    with Diagram("t", theme="paper") as d:
        a = d.shape("A", 200, 200)
        b = d.shape("B").inside(a)
        with pytest.raises(ValueError):
            a.inside(a)
        with pytest.raises(ValueError):
            a.inside(b)
        with pytest.raises(TypeError):
            b.inside("not a shape")


def test_edges_cross_a_container_border_and_are_not_hidden_by_its_fill():
    with Diagram("t", theme="paper") as d:
        outer = d.shape("Outer", 260, 160, id="outer", label_position="top", style=Style(fill="#EEE")).at(100, 100)
        inner = d.shape("Inner", 100, 40, id="inner").inside(outer)
        outside = d.shape("Outside", 100, 40, id="outside").at(500, 160)
        inner >> outside
        peer = d.shape("Peer", 60, 30, id="peer").inside(outer, "bottom_left", 10, -10)
        peer >> inner
    with warnings.catch_warnings():
        warnings.simplefilter("error")
        d.solve()
    route = d.routes[d.edges[0]]
    assert route.points[0].x == pytest.approx(inner.bounds.right) and route.points[-1].x == 500
    assert not audit_diagram(d)
    svg = d.render_svg()
    # Painted: container, then the edge, then the shapes it joins.
    assert svg.index('<g id="outer"') < svg.index("marker-end") < svg.index('<g id="inner"')


def test_top_label_sits_under_the_top_edge():
    with Diagram("t", theme="paper") as d:
        box = d.shape("Heading", 200, 150, id="box", label_position="top").at(50, 50)
        d.shape("x", 60, 30).inside(box)
    y = float(_block(d.render_svg(), "box").split('<text')[1].split(' y="')[1].split('"')[0])
    assert box.bounds.top < y < box.bounds.top + 25


def test_double_border_draws_an_inset_second_outline():
    with Diagram("t", theme="paper") as d:
        d.shape("Vault", 120, 80, id="v", style=Style(double=5, radius=8)).at(50, 50)
        d.shape("Plain", 120, 80, id="p").at(250, 50)
        d.shape("Tiny", 8, 8, id="tiny", style=Style(double=5), fit_label=False).at(450, 50)
    svg = d.render_svg()
    rects = [ln for ln in _block(svg, "v").splitlines() if "<rect" in ln]
    assert len(rects) == 2
    assert 'x="55" y="55" width="110" height="70" rx="3" fill="none"' in rects[1]
    assert _block(svg, "p").count("<rect") == 1 and _block(svg, "tiny").count("<rect") == 1
    with pytest.raises(ValueError):
        Style(double=-1)


# ----------------------------------------------------------------- PRIM-08 z


def test_paint_order_follows_z_then_declaration():
    with Diagram("t", theme="paper") as d:
        d.shape("top", id="top", z=5, obstacle=False).at(60, 60)
        d.shape("first", id="first", obstacle=False).at(70, 70)
        d.shape("second", id="second", obstacle=False).at(80, 80)
        d.shape("backdrop", 400, 300, id="backdrop", z=-1, obstacle=False, fit_label=False).at(20, 20)
        a = d.shape("A", id="a").at(500, 60)
        b = d.shape("B", id="b").at(700, 60)
        a >> b
        d.connect((500, 300), (700, 300), routing="direct", z=1, color="#123456")
    svg = d.render_svg()
    order = [svg.index(f'<g id="{name}"') for name in ("backdrop", "first", "second", "top")]
    assert order == sorted(order)
    under, over = svg.index("marker-end"), svg.index('stroke="#123456"')
    assert svg.index('<g id="backdrop"') < under < svg.index('<g id="a"') < over


def test_non_obstacles_do_not_bend_edges_or_trip_the_audit():
    with Diagram("t", theme="paper") as d:
        a = d.shape("A").at(60, 100)
        b = d.shape("B").at(500, 100)
        d.polygon([(250, 60), (350, 60), (350, 200), (250, 200)], z=-1, obstacle=False)
        a >> b
    assert len(d.routes[d.edges[0]].points) == 2
    assert not audit_diagram(d)


# ------------------------------------------------------- PRIM-09 arranging


def test_align_gives_every_element_the_first_ones_edge():
    for edge, attr in (("left", "left"), ("right", "right"), ("top", "top"), ("bottom", "bottom")):
        with Diagram("t", theme="paper") as d:
            ref = d.shape("ref", 100, 50).at(200, 200)
            others = [d.shape("a", 60, 30).at(20, 20), d.shape("b", 140, 90).at(400, 400)]
            align([ref, *others], edge)
        assert {getattr(o.bounds, attr) for o in others} == {getattr(ref.bounds, attr)}, edge
    with Diagram("t", theme="paper") as d:
        ref = d.shape("ref", 100, 50).at(200, 200)
        a, b = d.shape("a", 60, 30).at(20, 20), d.shape("b", 60, 30).at(400, 400)
        align([ref, a], "center")
        align([ref, b], "middle")
    assert a.bounds.center.x == ref.bounds.center.x and a.bounds.y == 20
    assert b.bounds.center.y == ref.bounds.center.y and b.bounds.x == 400
    with pytest.raises(ValueError):
        align([ref, a], "diagonal")


@pytest.mark.parametrize("direction", ["right", "left", "below", "above"])
def test_distribute_chains_elements_with_equal_gaps(direction):
    with Diagram("t", theme="paper") as d:
        items = [d.shape("a", 80, 40).at(400, 400), d.shape("b", 120, 60), d.shape("c", 50, 90)]
        distribute(items, direction, gap=25)
    for prev, cur in zip(items, items[1:]):
        gap = {
            "right": cur.bounds.left - prev.bounds.right, "left": prev.bounds.left - cur.bounds.right,
            "below": cur.bounds.top - prev.bounds.bottom, "above": prev.bounds.top - cur.bounds.bottom,
        }[direction]
        assert gap == pytest.approx(25)
        if direction in ("right", "left"):
            assert cur.bounds.center.y == pytest.approx(prev.bounds.center.y)
        else:
            assert cur.bounds.center.x == pytest.approx(prev.bounds.center.x)


def test_distribute_alignment_and_bad_direction():
    with Diagram("t", theme="paper") as d:
        items = [d.shape("a", 80, 40).at(100, 300), d.shape("b", 80, 100)]
        distribute(items, "right", gap="10mm", align="bottom")
    assert items[1].bounds.bottom == items[0].bounds.bottom
    assert items[1].bounds.left - items[0].bounds.right == pytest.approx(37.795, abs=0.01)
    with pytest.raises(ValueError):
        distribute(items, "sideways")


def test_grid_snaps_corners_and_resolving_is_stable():
    with Diagram("t", theme="paper", grid=10) as d:
        a = d.shape("A", 100, 40).at(63, 47)
        b = d.shape("B", 100, 40).right_of(a, margin=33)
        with d.group("G") as g:
            c = d.shape("C", 100, 40).at(207, 213)
    assert (a.bounds.x, a.bounds.y) == (60, 50) and (c.bounds.x, c.bounds.y) == (210, 210)
    assert b.bounds.x % 10 == 0
    assert g.bounds.left == c.bounds.left - g.padding  # the group follows its snapped child
    first = [(s.bounds.x, s.bounds.y) for s in d.shapes]
    d.solve()
    assert [(s.bounds.x, s.bounds.y) for s in d.shapes] == first
    d.grid = 25
    d.render_svg()
    assert a.bounds.x % 25 == 0 and a.bounds.y % 25 == 0


def test_sizes_and_positions_accept_units():
    with Diagram("t", theme="paper") as d:
        s = d.shape("S", "72pt", "1in", fit_label=False).at("25.4mm", "2.54cm")
    assert (s.bounds.x, s.bounds.y, s.bounds.width, s.bounds.height) == pytest.approx((96, 96, 96, 96))
