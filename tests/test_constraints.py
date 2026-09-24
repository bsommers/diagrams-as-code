from __future__ import annotations
import pytest
from iiot_diagrams.geometry import Anchor, Rect
from iiot_diagrams.elements import Element, Shape
from iiot_diagrams.constraints import ConstraintSolver
import iiot_diagrams

def test_package_exports():
    assert hasattr(iiot_diagrams, "Element")
    assert hasattr(iiot_diagrams, "Shape")
    assert hasattr(iiot_diagrams, "ConstraintSolver")
    assert iiot_diagrams.Element is Element
    assert iiot_diagrams.Shape is Shape
    assert iiot_diagrams.ConstraintSolver is ConstraintSolver

def test_element_defaults_and_metadata():
    el = Element("el1", label="Base Element", width=150, height=80, metadata={"tag": "demo"})
    assert el.id == "el1"
    assert el.label == "Base Element"
    assert el.width == 150
    assert el.height == 80
    assert el.bounds == Rect(0, 0, 150, 80)
    assert el.parent is None
    assert el.metadata == {"tag": "demo"}
    assert el.constraints == []

    s = Shape("s1", label="Default Shape")
    assert s.width == 120
    assert s.height == 60
    assert s.kind == "box"
    assert s.icon is None

def test_absolute_placement():
    solver = ConstraintSolver()
    s1 = Shape("s1", label="Sensor", width=100, height=50)
    s1.at(200, 150)
    solver.add(s1)
    solver.solve()
    assert s1.bounds.x == 200
    assert s1.bounds.y == 150

def test_absolute_placement_with_center_anchor():
    solver = ConstraintSolver()
    s1 = Shape("s1", label="Sensor", width=100, height=50)
    s1.at(200, 150, anchor=Anchor.CENTER)
    solver.add(s1)
    solver.solve()
    assert s1.bounds.x == 150
    assert s1.bounds.y == 125

def test_shape_to_shape_relative_placement():
    solver = ConstraintSolver()
    s1 = Shape("s1", label="PLC", width=100, height=60).at(50, 50)
    s2 = Shape("s2", label="Edge Gateway", width=120, height=60).right_of(s1, margin=30, align="center")
    s3 = Shape("s3", label="Local Historian", width=100, height=60).below(s1, margin=40, align="left")

    solver.add(s1, s2, s3)
    solver.solve()

    # s2 right of s1
    assert s2.bounds.x == 50 + 100 + 30  # 180
    assert s2.bounds.y == 50  # aligned center (both height 60)

    # s3 below s1, aligned left
    assert s3.bounds.x == 50
    assert s3.bounds.y == 50 + 60 + 40  # 150

def test_relative_directions_and_alignments():
    solver = ConstraintSolver()
    # base is at (100, 100), width=100, height=80
    base = Shape("base", label="Base", width=100, height=80).at(100, 100)

    # right_of variations
    r_top = Shape("r_top", label="RTop", width=40, height=20).right_of(base, margin=10, align="top")
    r_bottom = Shape("r_bottom", label="RBot", width=40, height=20).right_of(base, margin=10, align="bottom")
    r_center = Shape("r_center", label="RCtr", width=40, height=20).right_of(base, margin=10, align="center")

    # left_of variations
    l_top = Shape("l_top", label="LTop", width=40, height=20).left_of(base, margin=10, align="top")
    l_bottom = Shape("l_bottom", label="LBot", width=40, height=20).left_of(base, margin=10, align="bottom")
    l_center = Shape("l_center", label="LCtr", width=40, height=20).left_of(base, margin=10, align="center")

    # below variations
    b_left = Shape("b_left", label="BLeft", width=40, height=20).below(base, margin=10, align="left")
    b_right = Shape("b_right", label="BRight", width=40, height=20).below(base, margin=10, align="right")
    b_center = Shape("b_center", label="BCtr", width=40, height=20).below(base, margin=10, align="center")

    # above variations
    a_left = Shape("a_left", label="ALeft", width=40, height=20).above(base, margin=10, align="left")
    a_right = Shape("a_right", label="ARight", width=40, height=20).above(base, margin=10, align="right")
    a_center = Shape("a_center", label="ACtr", width=40, height=20).above(base, margin=10, align="center")

    solver.add(base, r_top, r_bottom, r_center, l_top, l_bottom, l_center,
               b_left, b_right, b_center, a_left, a_right, a_center)
    solver.solve()

    # right_of: x = base.right(200) + 10 = 210
    assert r_top.bounds == Rect(210, 100, 40, 20)
    assert r_bottom.bounds == Rect(210, 100 + 80 - 20, 40, 20)  # y = 160
    assert r_center.bounds == Rect(210, 100 + (80 - 20) / 2.0, 40, 20)  # y = 130

    # left_of: x = base.left(100) - 10 - 40 = 50
    assert l_top.bounds == Rect(50, 100, 40, 20)
    assert l_bottom.bounds == Rect(50, 160, 40, 20)
    assert l_center.bounds == Rect(50, 130, 40, 20)

    # below: y = base.bottom(180) + 10 = 190
    assert b_left.bounds == Rect(100, 190, 40, 20)
    assert b_right.bounds == Rect(100 + 100 - 40, 190, 40, 20)  # x = 160
    assert b_center.bounds == Rect(100 + (100 - 40) / 2.0, 190, 40, 20)  # x = 130

    # above: y = base.top(100) - 10 - 20 = 70
    assert a_left.bounds == Rect(100, 70, 40, 20)
    assert a_right.bounds == Rect(160, 70, 40, 20)
    assert a_center.bounds == Rect(130, 70, 40, 20)

def test_relative_chain_topological_resolution():
    solver = ConstraintSolver()
    s1 = Shape("s1", "S1", 100, 50).at(0, 0)
    s2 = Shape("s2", "S2", 100, 50).right_of(s1, margin=10)
    s3 = Shape("s3", "S3", 100, 50).right_of(s2, margin=10)
    s4 = Shape("s4", "S4", 100, 50).right_of(s3, margin=10)

    # Add in reverse order
    solver.add(s4, s3, s2, s1)
    solver.solve()

    assert s1.bounds.x == 0
    assert s2.bounds.x == 110
    assert s3.bounds.x == 220
    assert s4.bounds.x == 330

def test_unresolved_cycle_raises_runtime_error():
    solver = ConstraintSolver()
    s1 = Shape("s1", "S1", 100, 50)
    s2 = Shape("s2", "S2", 100, 50)
    s1.right_of(s2, margin=10)
    s2.right_of(s1, margin=10)

    solver.add(s1, s2)
    with pytest.raises(RuntimeError, match="Unresolved constraints"):
        solver.solve()

def test_missing_target_raises_runtime_error():
    solver = ConstraintSolver()
    s1 = Shape("s1", "S1", 100, 50)  # not placed
    s2 = Shape("s2", "S2", 100, 50).right_of(s1)
    solver.add(s2)
    with pytest.raises(RuntimeError, match="Unresolved constraints"):
        solver.solve()

def test_invalid_direction_raises_value_error():
    solver = ConstraintSolver()
    s1 = Shape("s1", "S1", 100, 50).at(0, 0)
    s2 = Shape("s2", "S2", 100, 50)
    s2.constraints.append({"type": "relative_dir", "target": s1, "direction": "diagonal", "margin": 10, "align": "center"})
    solver.add(s1, s2)
    with pytest.raises(ValueError, match="Unknown direction"):
        solver.solve()

def test_invalid_align_raises_value_error():
    solver = ConstraintSolver()
    s1 = Shape("s1", "S1", 100, 50).at(0, 0)
    s2 = Shape("s2", "S2", 100, 50)
    s2.constraints.append({"type": "relative_dir", "target": s1, "direction": "right", "margin": 10, "align": "diagonal"})
    solver.add(s1, s2)
    with pytest.raises(ValueError, match="Unknown align"):
        solver.solve()

def test_solver_add_sequence_input():
    solver = ConstraintSolver()
    s1 = Shape("s1", "S1", 100, 50).at(0, 0)
    s2 = Shape("s2", "S2", 100, 50).right_of(s1)
    s3 = Shape("s3", "S3", 100, 50).below(s1)
    s4 = Shape("s4", "S4", 100, 50).right_of(s3)

    # Test list and tuple inputs
    solver.add([s1, s2])
    solver.add((s3, s4))
    solver.solve()

    assert s1.bounds.x == 0
    assert s2.bounds.x == 120
    assert s3.bounds.y == 70
    assert s4.bounds.x == 120

def test_absolute_placement_with_string_anchor():
    solver = ConstraintSolver()
    s = Shape("s1", "S1", 100, 50)
    s.at(100, 100, anchor="top_right")
    solver.add(s)
    solver.solve()

    # top_right at (100, 100) means x = 100 - 100 = 0, y = 100 - 0 = 100
    assert s.bounds.x == 0
    assert s.bounds.y == 100

def test_solver_add_type_validation():
    solver = ConstraintSolver()
    with pytest.raises(TypeError, match="Expected Element or sequence of Elements"):
        solver.add("invalid_element")  # type: ignore

    with pytest.raises(TypeError, match="Expected Element"):
        solver.add([Shape("s1", "S1"), 123])  # type: ignore

def test_solver_add_duplicate_id_raises_value_error():
    solver = ConstraintSolver()
    s1 = Shape("s1", "S1", 100, 50)
    s2 = Shape("s1", "S1 Duplicate", 100, 50)
    solver.add(s1)
    with pytest.raises(ValueError, match="Duplicate element id"):
        solver.add(s2)


def test_typed_constraint_dataclasses_and_coercion():
    from diagrams_as_code.constraints import (
        AbsoluteConstraint,
        AlignConstraint,
        Constraint,
        RelativeConstraint,
        to_constraint,
    )

    # 1. AbsoluteConstraint typed and dict behavior
    abs_c = AbsoluteConstraint(100.0, 50.0, anchor=Anchor.CENTER)
    assert abs_c.type == "absolute"
    assert abs_c.x == 100.0
    assert abs_c.y == 50.0
    assert abs_c.anchor == Anchor.CENTER
    assert abs_c["x"] == 100.0
    assert abs_c["type"] == "absolute"
    assert "_source" not in abs_c
    assert abs_c.get("_source") is None
    abs_c["_source"] = "auto"
    assert abs_c["_source"] == "auto"
    assert abs_c.get("_source") == "auto"
    assert "_source" in abs_c
    abs_c._source = None
    assert "_source" not in abs_c

    # 2. RelativeConstraint
    target = Shape("t1", "Target")
    rel_c = RelativeConstraint(target=target, direction="right", margin=30.0, align="top")
    assert rel_c.type == "relative_dir"
    assert rel_c.target is target
    assert rel_c.direction == "right"
    assert rel_c.margin == 30.0
    assert rel_c.align == "top"
    assert rel_c["direction"] == "right"
    assert rel_c["margin"] == 30.0

    # 3. AlignConstraint
    align_c = AlignConstraint(target=target, align="center", axis="horizontal")
    assert align_c.type == "align"
    assert align_c.target is target
    assert align_c.align == "center"
    assert align_c.axis == "horizontal"
    assert align_c["align"] == "center"

    # 4. to_constraint coercion
    d = {"type": "absolute", "x": 10.0, "y": 20.0, "anchor": "top_left"}
    coerced = to_constraint(d)
    assert isinstance(coerced, AbsoluteConstraint)
    assert coerced.x == 10.0 and coerced.y == 20.0
    assert to_constraint(abs_c) is abs_c

    d_rel = {"type": "relative_dir", "target": target, "direction": "below", "margin": 15.0, "align": "center"}
    coerced_rel = to_constraint(d_rel)
    assert isinstance(coerced_rel, RelativeConstraint)
    assert coerced_rel.direction == "below" and coerced_rel.margin == 15.0

    d_align = {"type": "align", "target": target, "align": "left", "axis": "horizontal"}
    coerced_align = to_constraint(d_align)
    assert isinstance(coerced_align, AlignConstraint)
    assert coerced_align.align == "left"

    # 5. Methods appending typed dataclasses
    s = Shape("s", "S")
    s.at(10.0, 20.0)
    assert isinstance(s.constraints[0], AbsoluteConstraint)
    s.right_of(target)
    assert isinstance(s.constraints[1], RelativeConstraint)
    s.align_with(target)
    assert isinstance(s.constraints[2], AlignConstraint)


def test_align_with_constraint_solving():
    solver = ConstraintSolver()
    base = Shape("base", "Base", width=100.0, height=80.0).at(100.0, 100.0)

    # Centered horizontally: target x=100, width=100. Shape width=40. Expected x = 100 + (100 - 40)/2 = 130
    c_x = Shape("c_x", "CX", width=40.0, height=30.0).at(0.0, 200.0).align_with(base, align="center", axis="horizontal")

    # Left aligned: Expected x = 100
    l_x = Shape("l_x", "LX", width=40.0, height=30.0).at(0.0, 250.0).align_with(base, align="left")

    # Right aligned: Expected x = 100 + 100 - 40 = 160
    r_x = Shape("r_x", "RX", width=40.0, height=30.0).at(0.0, 300.0).align_with(base, align="right")

    # Top aligned: Expected y = 100
    t_y = Shape("t_y", "TY", width=40.0, height=30.0).at(300.0, 0.0).align_with(base, align="top")

    # Bottom aligned: Expected y = 100 + 80 - 30 = 150
    b_y = Shape("b_y", "BY", width=40.0, height=30.0).at(300.0, 0.0).align_with(base, align="bottom")

    solver.add(base, c_x, l_x, r_x, t_y, b_y)
    solver.solve()

    assert c_x.bounds.x == 130.0
    assert l_x.bounds.x == 100.0
    assert r_x.bounds.x == 160.0
    assert t_y.bounds.y == 100.0
    assert b_y.bounds.y == 150.0

