"""Regression tests for the Phase 12 defect list (plan: docs/plans/2026-11-12-…, R1–R14)."""
from __future__ import annotations

import random

import pytest

from diagrams_as_code import Diagram, Port, Shape
from diagrams_as_code.geometry import PathKind, Point

from routing_invariants import edge_problems


def _problems(d: Diagram) -> list[tuple[str, str]]:
    out = []
    for e in d.edges:
        others = [s.bounds for s in d.shapes if s is not e.source and s is not e.target]
        out += [(f"{e.source.id}->{e.target.id}", p) for p in edge_problems(e, d.routes[e], others)]
    return out


def _two(ax, ay, bx, by, w=200, h=60, **edge_kw) -> Diagram:
    with Diagram("t", theme="monochrome") as d:
        a = d.add(Shape("a", "A", width=w, height=h)).at(ax, ay)
        b = d.add(Shape("b", "B", width=w, height=h)).at(bx, by)
        d.connect(a, b, **edge_kw)
    d.solve()
    return d


# R2 ---------------------------------------------------------------------
def test_auto_ports_use_the_free_axis_when_boxes_overlap_on_the_other():
    d = _two(100, 100, 250, 200)
    assert _problems(d) == []
    pts = d.routes[d.edges[0]].points
    assert pts[0].y == 160 and pts[-1].y == 200  # south -> north


def test_explicit_facing_ports_with_target_behind_wrap_around():
    d = _two(400, 100, 100, 100, w=120, source_port=Port.EAST, target_port=Port.WEST)
    assert _problems(d) == []


def test_explicit_south_to_east_does_not_cross_target():
    d = _two(300, 100, 280, 300, w=190, source_port=Port.SOUTH, target_port=Port.EAST)
    assert _problems(d) == []


# R1 ---------------------------------------------------------------------
def test_detour_arrives_perpendicular_to_target_port():
    with Diagram("t", theme="monochrome") as d:
        a = d.add(Shape("a", "A")).at(700, 100)
        mid = d.add(Shape("m", "M")).at(400, 100)
        b = d.add(Shape("b", "B")).at(100, 100)
        d.connect(a, b)
    d.solve()
    assert _problems(d) == []
    pts = d.routes[d.edges[0]].points
    assert pts[-2].y == pts[-1].y  # last segment horizontal into the east side


@pytest.mark.parametrize("routing", ["orthogonal", "direct"])
def test_fuzzed_layouts_keep_routing_invariants(routing):
    rng = random.Random(1234)
    bad = []
    for trial in range(120):
        with Diagram("t", theme="monochrome", routing=routing) as d:
            shapes = []
            for i in range(5):
                for _ in range(50):
                    x, y = rng.randrange(60, 900, 10), rng.randrange(60, 600, 10)
                    s = Shape(f"n{i}", f"N{i}", width=rng.choice([80, 120, 200]), height=60)
                    s.at(x, y)
                    if not any(s.bounds.expand(20).intersects(o.bounds) for o in shapes):
                        shapes.append(d.add(s))
                        break
            for _ in range(5):
                a, b = rng.sample(shapes, 2)
                d.connect(a, b)
        d.solve()
        kinds = {"through_own_endpoint", "tangent_arrival", "non_finite", "degenerate"}
        if routing == "direct":
            kinds -= {"tangent_arrival"}
        bad += [(trial, *p) for p in _problems(d) if p[1] in kinds]
    assert bad == []


# R3 ---------------------------------------------------------------------
@pytest.mark.parametrize("routing", ["orthogonal", "curve", "direct"])
def test_self_loop_is_drawn_outside_the_node(routing):
    with Diagram("t", theme="monochrome", routing=routing) as d:
        a = d.add(Shape("a", "A")).at(300, 300)
        d.connect(a, a)
    d.solve()
    path = d.routes[d.edges[0]]
    assert len(path.points) >= 4
    assert _problems(d) == []
    bb = path.bbox()
    assert bb.right > a.bounds.right and bb.y < a.bounds.top


# R8 ---------------------------------------------------------------------
def test_opposite_edges_between_a_pair_do_not_coincide():
    with Diagram("t", theme="monochrome") as d:
        a = d.add(Shape("a", "A")).at(100, 100)
        b = d.add(Shape("b", "B")).at(400, 100)
        d.connect(a, b, label="go")
        d.connect(b, a, label="back")
    d.solve()
    p1, p2 = (d.routes[e] for e in d.edges)
    assert set(p1.points).isdisjoint(p2.points)
    assert p1.label_anchor() != p2.label_anchor()
    # both stay straight: same slot on both nodes
    assert len(p1.points) == 2 and len(p2.points) == 2


def test_fan_out_from_one_side_still_shares_its_anchor():
    with Diagram("t", theme="monochrome") as d:
        a = d.add(Shape("a", "A")).at(100, 200)
        b = d.add(Shape("b", "B")).at(400, 100)
        c = d.add(Shape("c", "C")).at(400, 300)
        d.connect(a, b)
        d.connect(a, c)
    d.solve()
    assert d.routes[d.edges[0]].points[0] == d.routes[d.edges[1]].points[0]


# R11 / R12 --------------------------------------------------------------
def test_manual_waypoint_edges_inherit_diagram_corner_radius():
    with Diagram("t", theme="monochrome", corner_radius=20) as d:
        a = d.add(Shape("a", "A")).at(100, 100)
        b = d.add(Shape("b", "B")).at(400, 300)
        d.connect(a, b)
        d.edges[0].manual_waypoints = [Point(220, 130), Point(300, 130), Point(300, 330), Point(400, 330)]
    d.solve()
    assert d.routes[d.edges[0]].corner_radius == 20.0


def test_bom_reports_diagram_level_routing():
    with Diagram("t", theme="monochrome", routing="direct") as d:
        a = d.add(Shape("a", "A")).at(100, 100)
        b = d.add(Shape("b", "B")).at(400, 300)
        d.connect(a, b)
    d.solve()
    assert d.bom.connections()[0]["routing"] == "direct"


# R9 / R10 ---------------------------------------------------------------
def test_elements_and_edges_added_after_a_solve_are_laid_out():
    with Diagram("t", theme="monochrome") as d:
        a = d.add(Shape("a", "A")).at(300, 300)
    d.render_svg()
    b = d.add(Shape("b", "B")).right_of(a, margin=50)
    e = d.connect(a, b)
    d.render_svg()
    assert b.bounds.x == a.bounds.right + 50
    assert e in d.routes and d.routes[e].points[0].x == a.bounds.right


def test_resizing_a_shape_after_a_solve_survives_the_next_solve():
    with Diagram("t", theme="monochrome") as d:
        a = d.add(Shape("a", "A", width=100)).at(100, 100)
        b = d.add(Shape("b", "B")).right_of(a, margin=40)
    d.render_svg()
    a.width = 300
    d.render_svg()
    assert a.bounds.width == 300
    assert b.bounds.x == a.bounds.right + 40


# R5 / R6 / R13 ----------------------------------------------------------
_SCRIPT = '''
from diagrams_as_code import Diagram, Shape
{extra}
def diagram():
    with Diagram("t", theme="monochrome") as d:
        d.add(Shape("a", "A")).at(100, 100)
    return d
'''


def _script(path, extra=""):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(_SCRIPT.format(extra=extra), encoding="utf-8")
    return path


def test_layout_file_rejects_non_finite_coordinates(tmp_path):
    from diagrams_as_code import load_layout_file

    f = tmp_path / "l.json"
    f.write_text('{"version": 1, "positions": {"A": {"x": NaN, "y": Infinity}}}')
    with pytest.raises(ValueError, match="non-finite"):
        load_layout_file(f)


def test_cli_reports_a_missing_layout_file(tmp_path, capsys):
    from diagrams_as_code.cli import main

    s = _script(tmp_path / "x.py")
    rc = main(["render", str(s), "--out", str(tmp_path / "out"), "--layout-file", str(tmp_path / "typo.json")])
    assert rc == 2
    assert "typo.json does not exist" in capsys.readouterr().err


def test_cli_refuses_to_overwrite_a_same_named_output(tmp_path, capsys):
    from diagrams_as_code.cli import main

    a, b = _script(tmp_path / "a" / "x.py"), _script(tmp_path / "b" / "x.py")
    rc = main(["render", str(a), str(b), "--out", str(tmp_path / "out"), "--format", "svg"])
    assert rc == 1
    assert "already written by" in capsys.readouterr().err


def test_cli_scripts_can_import_sibling_helpers(tmp_path):
    from diagrams_as_code.cli import main

    (tmp_path / "dac_helper_mod.py").write_text("VALUE = 1\n")
    s = _script(tmp_path / "x.py", extra="import dac_helper_mod")
    assert main(["render", str(s), "--out", str(tmp_path / "out"), "--format", "svg"]) == 0


def test_cli_contains_sys_exit_inside_a_script(tmp_path, capsys):
    from diagrams_as_code.cli import main

    bad = _script(tmp_path / "a_bad.py", extra="import sys; sys.exit(7)")
    good = _script(tmp_path / "b_good.py")
    rc = main(["render", str(bad), str(good), "--out", str(tmp_path / "out"), "--format", "svg"])
    assert rc == 1
    assert (tmp_path / "out" / "b_good.svg").exists()
    assert "sys.exit(7)" in capsys.readouterr().err


def test_cli_reports_an_empty_directory(tmp_path, capsys):
    from diagrams_as_code.cli import main

    (tmp_path / "empty").mkdir()
    assert main(["render", str(tmp_path / "empty"), "--out", str(tmp_path / "out")]) == 1
    assert "no diagram scripts found" in capsys.readouterr().err


def test_cli_layout_export_blames_output_when_it_is_a_directory(tmp_path, capsys):
    from diagrams_as_code.cli import main

    s = _script(tmp_path / "x.py")
    assert main(["layout", "export", str(s), "-o", str(tmp_path)]) == 2
    assert "--output" in capsys.readouterr().err
