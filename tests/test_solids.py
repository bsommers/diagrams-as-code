"""PRIM-07: convex solids in parallel projection."""
from __future__ import annotations

import pytest

from diagrams_as_code import Diagram, Solid, Style, isometric, oblique
from diagrams_as_code.solids import plane_points

BOX = Solid.box(4, 3, 2)
# Faces of Solid.box: 0 front (z=0), 1 back, 2 bottom, 3 top, 4 left, 5 right.


def _front(solid, projection):
    faces, _ = solid.project(projection)
    return {f.index for f in faces if f.front}


def test_oblique_box_shows_front_top_and_right():
    assert _front(BOX, oblique()) == {0, 3, 5}


def test_isometric_box_shows_top_and_the_two_near_sides():
    assert _front(BOX, isometric()) == {1, 3, 5}


@pytest.mark.parametrize("projection", [oblique(), oblique(30, 1.0), isometric()])
def test_box_has_nine_visible_edges_and_three_hidden(projection):
    _, edges = BOX.project(projection)
    assert sum(e.visible for e in edges) == 9 and sum(not e.visible for e in edges) == 3
    # The hidden ones meet at the far corner.
    hidden = [e for e in edges if not e.visible]
    shared = set.intersection(*[{(round(e.a.x, 6), round(e.a.y, 6)), (round(e.b.x, 6), round(e.b.y, 6))} for e in hidden])
    assert len(shared) == 1


def test_oblique_front_face_is_drawn_true_size_and_depth_is_foreshortened():
    faces, _ = Solid.box(40, 30, 20).project(oblique(45, 0.5))
    front = next(f for f in faces if f.index == 0)
    xs, ys = [p.x for p in front.points], [p.y for p in front.points]
    assert (max(xs) - min(xs), max(ys) - min(ys)) == pytest.approx((40.0, 30.0))
    allx = [p.x for f in faces for p in f.points]
    assert max(allx) - min(allx) == pytest.approx(40.0 + 20 * 0.5 * 2**-0.5)


def test_faces_are_ordered_back_to_front():
    faces, _ = BOX.project(oblique())
    assert [f.front for f in faces] == [False, False, False, True, True, True]


def test_scale_multiplies_the_projection():
    a, _ = BOX.project(oblique())
    b, _ = BOX.project(oblique(), scale=10)
    assert b[0].points[1].x == pytest.approx(a[0].points[1].x * 10)


def test_face_winding_does_not_change_visibility():
    flipped = Solid(BOX.vertices, tuple(tuple(reversed(f)) for f in BOX.faces))
    assert _front(flipped, oblique()) == _front(BOX, oblique())


def test_hull_of_a_box_merges_coplanar_triangles_into_six_quads():
    hull = Solid.hull(list(BOX.vertices) + [(2, 1.5, 1), (2, 1.5, 1)])  # an interior point, twice
    assert len(hull.vertices) == 8 and sorted(len(f) for f in hull.faces) == [4] * 6


def test_hull_of_an_octahedron():
    octa = Solid.hull([(1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0), (0, 0, 1), (0, 0, -1)])
    assert len(octa.faces) == 8 and len(octa.edges()) == 12
    assert all(len(meeting) == 2 for meeting in octa.edges().values())


def test_hull_needs_a_solid():
    with pytest.raises(ValueError):
        Solid.hull([(0, 0, 0), (1, 0, 0), (0, 1, 0), (1, 1, 0)])


def test_section_is_the_cut_polygon():
    cut = BOX.section((2, 0, 0), (1, 0, 0))
    assert len(cut) == 4 and {p[0] for p in cut} == {2.0}
    assert sorted((p[1], p[2]) for p in cut) == [(0.0, 0.0), (0.0, 2.0), (3.0, 0.0), (3.0, 2.0)]
    assert BOX.section((10, 0, 0), (1, 0, 0)) == []


def test_clipped_keeps_the_side_behind_the_plane():
    half = BOX.clipped((2, 0, 0), (1, 0, 0))
    assert max(v[0] for v in half.vertices) == pytest.approx(2.0)
    assert len(half.faces) == 6
    wedge = BOX.clipped((2, 1.5, 1), (1, 1, 0))
    assert len(wedge.faces) == 5 or len(wedge.faces) == 6


def test_prism_and_pyramid():
    prism = Solid.prism([(0, 0), (4, 0), (2, 3)], 5)
    assert len(prism.faces) == 5 and len(prism.edges()) == 9
    pyramid = Solid.pyramid([(0, 0), (4, 0), (4, 4), (0, 4)], (2, 5, 2))
    assert len(pyramid.faces) == 5 and len(pyramid.edges()) == 8
    with pytest.raises(ValueError):
        Solid.prism([(0, 0), (1, 1)], 2)


def test_bad_faces_are_rejected():
    with pytest.raises(ValueError):
        Solid(((0, 0, 0), (1, 0, 0), (0, 1, 0)), ((0, 1),))
    with pytest.raises(ValueError):
        Solid(((0, 0, 0), (1, 0, 0), (0, 1, 0)), ((0, 1, 7),))


def test_plane_patch_is_a_parallelogram_centred_on_the_point():
    pts = plane_points((0, 0, 0), (0, 1, 0), 10, oblique())
    assert len(pts) == 4
    assert sum(p.x for p in pts) == pytest.approx(0.0) and sum(p.y for p in pts) == pytest.approx(0.0)


def _paths(svg: str, element_id: str) -> list[str]:
    block = svg[svg.index(f'<g id="{element_id}"'):].split("</g>", 1)[0]
    return [line for line in block.splitlines() if "<path" in line]


def test_cuboid_draws_dashed_hidden_edges_and_solid_visible_ones():
    with Diagram("t", theme="paper") as d:
        box = d.cuboid("crate", 80, 60, 40, id="crate").at(50, 50)
    paths = _paths(d.render_svg(), "crate")
    dashed = [p for p in paths if "stroke-dasharray" in p]
    solid = [p for p in paths if 'fill="none"' in p and "stroke-dasharray" not in p]
    assert len(dashed) == 3 and len(solid) == 9
    # Opaque: only the three faces towards the viewer are filled.
    assert len([p for p in paths if 'fill="none"' not in p]) == 3
    assert box.bounds.width == pytest.approx(80 + 40 * 0.5 * 2**-0.5)
    assert (box.bounds.x, box.bounds.y) == (50, 50)


def test_translucent_solid_fills_every_face_and_hidden_can_be_dropped():
    with Diagram("t", theme="paper") as d:
        d.cuboid(id="glass", style=Style(fill="#CCDDEE", fill_opacity=0.5)).at(50, 50)
        d.cuboid(id="plain", hidden="none").at(300, 50)
    svg = d.render_svg()
    assert len([p for p in _paths(svg, "glass") if "fill-opacity" in p]) == 6
    assert not [p for p in _paths(svg, "plain") if "stroke-dasharray" in p]


def test_cut_plane_and_section_are_drawn_and_counted_in_the_size():
    octa = Solid.hull([(60, 0, 0), (-60, 0, 0), (0, 70, 0), (0, -70, 0), (0, 0, 60), (0, 0, -60)])
    with Diagram("t", theme="paper") as d:
        bare = d.solid(octa, id="bare").at(50, 50)
        cut = d.solid(octa, id="cut", cut=((0, 10, 0), (0, 1, 0)), cut_size=120).at(400, 50)
    assert cut.bounds.width > bare.bounds.width
    assert len(_paths(d.render_svg(), "cut")) == len(_paths(d.render_svg(), "bare")) + 2


def test_solid_can_be_an_edge_endpoint_and_stays_out_of_the_bom():
    with Diagram("t", theme="paper") as d:
        a = d.cuboid("A").at(50, 50)
        b = d.shape("B").at(300, 60)
        a >> b
    assert d.routes[d.edges[0]].points[0].x == pytest.approx(a.bounds.right)
    assert [item["label"] for item in d.bom.items()] == ["B"]
