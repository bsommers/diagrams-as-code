from __future__ import annotations

import pytest

from diagrams_as_code import ConstraintSolver, Diagram, Rect, Shape


def test_theme_overrides_keep_every_other_field() -> None:
    base = Diagram(theme="nord").theme
    diag = Diagram(theme="nord", theme_overrides={"accent": "#123456"})
    assert diag.theme.accent == "#123456"
    assert diag.theme.name == "nord_custom"
    assert diag.theme.font_family == base.font_family
    assert diag.theme.background == base.background


def test_unknown_theme_override_is_rejected() -> None:
    with pytest.raises(TypeError):
        Diagram(theme_overrides={"no_such_field": "x"})


def test_explicit_id_is_recorded() -> None:
    diag = Diagram()
    assert diag.shape("A").explicit_id is False
    assert diag.shape("B", id="b").explicit_id is True
    with diag.group("G") as g:
        pass
    assert g.explicit_id is False
    assert Shape("s", "S").explicit_id is True


def test_all_elements_is_public_and_matches_alias() -> None:
    diag = Diagram()
    with diag.group("G"):
        diag.shape("A")
    assert diag.solver.all_elements() == diag.solver._collect_all_elements()
    assert [e.label for e in diag.solver.all_elements()] == ["G", "A"]


def test_lenient_solve_leaves_unresolvable_elements_alone() -> None:
    outside = Shape("out", "Out")
    inner = Shape("in", "In").right_of(outside)
    solver = ConstraintSolver()
    solver.add(inner)
    with pytest.raises(RuntimeError):
        solver.solve()
    solver.solve(strict=False)  # no raise


def test_rect_intersects_excludes_touching_edges() -> None:
    a = Rect(0, 0, 10, 10)
    assert a.intersects(Rect(5, 5, 10, 10))
    assert not a.intersects(Rect(10, 0, 10, 10))
    assert not a.intersects(Rect(0, 20, 10, 10))
