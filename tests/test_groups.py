from __future__ import annotations

import pytest

from iiot_diagrams import Group
import iiot_diagrams
from iiot_diagrams.constraints import ConstraintSolver
from iiot_diagrams.elements import Shape
from iiot_diagrams.geometry import Anchor, Rect


def test_package_exports() -> None:
    assert hasattr(iiot_diagrams, "Group")
    assert "Group" in iiot_diagrams.__all__
    assert iiot_diagrams.Group is Group


def test_group_initialization_defaults_and_properties() -> None:
    g = Group("g1", label="Edge Factory", metadata={"tier": "edge"})
    assert g.id == "g1"
    assert g.label == "Edge Factory"
    assert g.padding == 25.0
    assert g.header_height == 35.0
    assert g.is_auto_sized is True
    assert g.children == []
    assert g.parent is None
    assert g.metadata == {"tier": "edge"}
    assert g.bounds == Rect(0.0, 0.0, 120.0, 60.0)


def test_group_add_elements() -> None:
    g = Group("g1", label="Factory")
    s1 = Shape("s1", label="PLC")
    s2 = Shape("s2", label="HMI")

    ret = g.add(s1, s2)
    assert ret is g
    assert g.children == [s1, s2]
    assert s1.parent is g
    assert s2.parent is g

    # Adding duplicate should not duplicate entry
    g.add(s1)
    assert len(g.children) == 2

    # Adding via sequence
    s3 = Shape("s3", label="Sensor")
    g.add([s3])
    assert s3 in g.children
    assert s3.parent is g


def test_group_empty_calculate_bounds() -> None:
    g = Group("g_empty", label="Empty Container", padding=20.0, header_height=30.0)
    b = g.calculate_bounds()
    assert b == Rect(0.0, 0.0, 120.0, 60.0)
    assert g.auto_bounds() == Rect(0.0, 0.0, 120.0, 60.0)


def test_group_calculate_bounds_single_child() -> None:
    g = Group("g1", label="Single Cell", padding=20.0, header_height=30.0)
    s = Shape("s1", label="Robot", width=100.0, height=50.0).at(50.0, 40.0)
    s.bounds = Rect(50.0, 40.0, 100.0, 50.0)
    g.add(s)

    b = g.calculate_bounds()
    # left: 50 - 20 = 30
    # top: 40 - 20 - 30 = -10
    # width: 100 + 40 = 140
    # height: 50 + 40 + 30 = 120
    assert b.left == 30.0
    assert b.top == -10.0
    assert b.width == 140.0
    assert b.height == 120.0
    assert b.right == 170.0
    assert b.bottom == 110.0
    assert g.bounds == b
    assert g.width == 140.0
    assert g.height == 120.0


def test_group_auto_bounds() -> None:
    solver = ConstraintSolver()
    g1 = Group("g1", label="Edge Factory", padding=20.0)
    s1 = Shape("s1", label="PLC", width=100.0, height=50.0).at(100.0, 100.0)
    s2 = Shape("s2", label="Gateway", width=100.0, height=50.0).below(
        s1, margin=30.0, align="left"
    )
    g1.add(s1, s2)

    solver.add(g1, s1, s2)
    solver.solve()

    # Children span x: 100..200, y: 100..230 (100 + 50 + 30 + 50)
    # With padding 20 and header room (35), g1 bounds are calculated
    assert g1.bounds.left <= 80.0
    assert g1.bounds.right >= 220.0
    assert g1.bounds.bottom >= 250.0


def test_group_to_group_flow_placement() -> None:
    solver = ConstraintSolver()
    g1 = Group("g1", label="Plant Site", padding=20.0)
    s1 = Shape("s1", label="PLC").at(50.0, 50.0)
    g1.add(s1)

    g2 = Group("g2", label="Cloud Platform", padding=20.0).right_of(g1, margin=100.0)
    s2 = Shape("s2", label="Broker", width=120.0, height=60.0)
    g2.add(s2)

    solver.add(g1, s1, g2, s2)
    solver.solve()

    assert g2.bounds.left == g1.bounds.right + 100.0


def test_group_flow_placement_directions_and_alignments() -> None:
    solver = ConstraintSolver()
    g1 = Group("g1", label="Plant 1", padding=20.0, header_height=30.0)
    s1 = Shape("s1", label="Node 1", width=100.0, height=50.0).at(100.0, 100.0)
    g1.add(s1)

    # g2 below g1, align left (default for below)
    g2 = Group("g2", label="Plant 2", padding=20.0, header_height=30.0).below(
        g1, margin=40.0, align="left"
    )
    s2 = Shape("s2", label="Node 2", width=100.0, height=50.0)
    g2.add(s2)

    # g3 right of g1, align top (default for right_of)
    g3 = Group("g3", label="Plant 3", padding=20.0, header_height=30.0).right_of(
        g1, margin=60.0, align="top"
    )
    s3 = Shape("s3", label="Node 3", width=100.0, height=50.0)
    g3.add(s3)

    # g4 left of g1, align bottom
    g4 = Group("g4", label="Plant 4", padding=20.0, header_height=30.0).left_of(
        g1, margin=50.0, align="bottom"
    )
    s4 = Shape("s4", label="Node 4", width=100.0, height=50.0)
    g4.add(s4)

    # g5 above g1, align right
    g5 = Group("g5", label="Plant 5", padding=20.0, header_height=30.0).above(
        g1, margin=30.0, align="right"
    )
    s5 = Shape("s5", label="Node 5", width=100.0, height=50.0)
    g5.add(s5)

    solver.add(g1, s1, g2, s2, g3, s3, g4, s4, g5, s5)
    solver.solve()

    # Verify g2 below g1, align left
    assert g2.bounds.top == g1.bounds.bottom + 40.0
    assert g2.bounds.left == g1.bounds.left

    # Verify g3 right of g1, align top
    assert g3.bounds.left == g1.bounds.right + 60.0
    assert g3.bounds.top == g1.bounds.top

    # Verify g4 left of g1, align bottom
    assert g4.bounds.right == g1.bounds.left - 50.0
    assert g4.bounds.bottom == g1.bounds.bottom

    # Verify g5 above g1, align right
    assert g5.bounds.bottom == g1.bounds.top - 30.0
    assert g5.bounds.right == g1.bounds.right


def test_child_coordinate_translation_when_parent_group_moves() -> None:
    solver = ConstraintSolver()
    g1 = Group("g1", label="Plant Site", padding=25.0, header_height=35.0)
    s1 = Shape("s1", label="PLC", width=100.0, height=50.0).at(100.0, 100.0)
    g1.add(s1)

    g2 = Group("g2", label="Cloud Platform", padding=30.0, header_height=40.0).right_of(
        g1, margin=80.0, align="top"
    )
    s2 = Shape("s2", label="Broker", width=120.0, height=60.0)
    s3 = Shape("s3", label="Historian", width=120.0, height=60.0).below(
        s2, margin=20.0, align="left"
    )
    g2.add(s2, s3)

    solver.add(g1, s1, g2, s2, s3)
    solver.solve()

    # Check g2 positioned correctly relative to g1
    assert g2.bounds.left == g1.bounds.right + 80.0
    assert g2.bounds.top == g1.bounds.top

    # Check s2 child translated inside g2 with padding and header room
    assert s2.bounds.left == g2.bounds.left + g2.padding
    assert s2.bounds.top == g2.bounds.top + g2.padding + g2.header_height

    # Check s3 translated with s2 and preserved internal offset
    assert s3.bounds.left == s2.bounds.left
    assert s3.bounds.top == s2.bounds.bottom + 20.0

    # Check g2 bounds encompass both s2 and s3 plus padding
    assert g2.bounds.right == s2.bounds.right + g2.padding
    assert g2.bounds.bottom == s3.bounds.bottom + g2.padding


def test_nested_groups_bounds_and_translation() -> None:
    solver = ConstraintSolver()

    outer = Group("outer", label="Enterprise Site", padding=40.0, header_height=50.0).at(
        200.0, 200.0, anchor=Anchor.TOP_LEFT
    )
    inner = Group("inner", label="Control Zone", padding=20.0, header_height=30.0)
    s1 = Shape("s1", label="Safety Controller", width=100.0, height=50.0)
    inner.add(s1)
    outer.add(inner)

    solver.add(outer, inner, s1)
    solver.solve()

    # outer at 200, 200
    assert outer.bounds.left == 200.0
    assert outer.bounds.top == 200.0

    # inner nested inside outer
    assert inner.bounds.left == outer.bounds.left + outer.padding
    assert inner.bounds.top == outer.bounds.top + outer.padding + outer.header_height

    # s1 nested inside inner
    assert s1.bounds.left == inner.bounds.left + inner.padding
    assert s1.bounds.top == inner.bounds.top + inner.padding + inner.header_height

    # outer wraps inner with padding
    assert outer.bounds.right == inner.bounds.right + outer.padding
    assert outer.bounds.bottom == inner.bounds.bottom + outer.padding


def test_group_internal_layouts() -> None:
    # 1. Vertical Flow
    g_v = Group("gv", label="Vertical Flow", padding=20.0, header_height=30.0)
    v1 = Shape("v1", "V1", 80.0, 40.0)
    v2 = Shape("v2", "V2", 80.0, 40.0)
    v3 = Shape("v3", "V3", 80.0, 40.0)
    g_v.add(v1, v2, v3).vertical_flow(margin=15.0, align="left")

    solver_v = ConstraintSolver()
    solver_v.add(g_v, v1, v2, v3)
    solver_v.solve()

    assert v2.bounds.top == v1.bounds.bottom + 15.0
    assert v3.bounds.top == v2.bounds.bottom + 15.0
    assert v1.bounds.left == v2.bounds.left == v3.bounds.left

    # 2. Horizontal Flow
    g_h = Group("gh", label="Horizontal Flow", padding=20.0, header_height=30.0)
    h1 = Shape("h1", "H1", 60.0, 40.0)
    h2 = Shape("h2", "H2", 60.0, 40.0)
    h3 = Shape("h3", "H3", 60.0, 40.0)
    g_h.add(h1, h2, h3).horizontal_flow(margin=25.0, align="top")

    solver_h = ConstraintSolver()
    solver_h.add(g_h, h1, h2, h3)
    solver_h.solve()

    assert h2.bounds.left == h1.bounds.right + 25.0
    assert h3.bounds.left == h2.bounds.right + 25.0
    assert h1.bounds.top == h2.bounds.top == h3.bounds.top

    # 3. Grid
    g_g = Group("gg", label="Grid Layout", padding=20.0, header_height=30.0)
    g1 = Shape("g1", "G1", 50.0, 30.0)
    g2 = Shape("g2", "G2", 50.0, 30.0)
    g3 = Shape("g3", "G3", 50.0, 30.0)
    g4 = Shape("g4", "G4", 50.0, 30.0)
    g_g.add(g1, g2, g3, g4).grid(columns=2, margin_x=10.0, margin_y=15.0)

    solver_g = ConstraintSolver()
    solver_g.add(g_g, g1, g2, g3, g4)
    solver_g.solve()

    # Row 0: g1, g2
    assert g2.bounds.left == g1.bounds.right + 10.0
    assert g2.bounds.top == g1.bounds.top
    # Row 1: g3, g4
    assert g3.bounds.top == g1.bounds.bottom + 15.0
    assert g3.bounds.left == g1.bounds.left
    assert g4.bounds.left == g3.bounds.right + 10.0
    assert g4.bounds.top == g3.bounds.top


def test_solver_auto_resolves_unregistered_children() -> None:
    solver = ConstraintSolver()
    g1 = Group("g1", label="Auto Add Group", padding=20.0)
    s1 = Shape("s1", label="Child Shape", width=100.0, height=50.0)
    g1.add(s1)

    # Only g1 added to solver, not s1 explicitly
    solver.add(g1)
    solver.solve()

    assert s1 in g1.children
    assert s1.bounds.width == 100.0
    assert s1.bounds.height == 50.0
    assert g1.bounds.width == 100.0 + 40.0


def test_group_to_shape_and_shape_to_group_placement() -> None:
    solver = ConstraintSolver()

    # Shape placed absolutely
    s_lead = Shape("s_lead", "Leader", 100.0, 50.0).at(50.0, 50.0)

    # Group placed right of shape
    g = Group("g", label="Follower Group", padding=20.0, header_height=30.0).right_of(
        s_lead, margin=40.0, align="top"
    )
    s_child = Shape("s_child", "Child", 80.0, 40.0)
    g.add(s_child)

    # Another shape placed right of group
    s_trail = Shape("s_trail", "Trailer", 90.0, 45.0).right_of(
        g, margin=30.0, align="center"
    )

    solver.add(s_lead, g, s_child, s_trail)
    solver.solve()

    assert g.bounds.left == s_lead.bounds.right + 40.0
    assert g.bounds.top == s_lead.bounds.top
    assert s_trail.bounds.left == g.bounds.right + 30.0
    assert s_trail.bounds.center.y == pytest.approx(g.bounds.center.y)


def test_group_flow_invalid_direction_raises_value_error() -> None:
    solver = ConstraintSolver()
    g1 = Group("g1", "G1", padding=20.0).at(0.0, 0.0)
    g2 = Group("g2", "G2", padding=20.0)
    g2.constraints.append(
        {
            "type": "relative_dir",
            "target": g1,
            "direction": "diagonal",
            "margin": 10.0,
            "align": "top",
        }
    )
    solver.add(g1, g2)
    with pytest.raises(ValueError, match="Unknown direction"):
        solver.solve()


def test_group_flow_invalid_align_raises_value_error() -> None:
    solver = ConstraintSolver()
    g1 = Group("g1", "G1", padding=20.0).at(0.0, 0.0)
    g2 = Group("g2", "G2", padding=20.0)
    g2.constraints.append(
        {
            "type": "relative_dir",
            "target": g1,
            "direction": "right",
            "margin": 10.0,
            "align": "invalid_align",
        }
    )
    solver.add(g1, g2)
    with pytest.raises(ValueError, match="Unknown align"):
        solver.solve()


def test_group_cycle_raises_runtime_error() -> None:
    solver = ConstraintSolver()
    g1 = Group("g1", "G1", padding=20.0)
    g2 = Group("g2", "G2", padding=20.0)
    g1.right_of(g2)
    g2.right_of(g1)
    solver.add(g1, g2)
    with pytest.raises(RuntimeError, match="Unresolved constraints"):
        solver.solve()


def test_group_duplicate_child_id_raises_value_error() -> None:
    solver = ConstraintSolver()
    g1 = Group("g1", "G1")
    g2 = Group("g2", "G2")
    s1 = Shape("clash_id", "S1")
    s2 = Shape("clash_id", "S2")
    g1.add(s1)
    g2.add(s2)

    solver.add(g1, g2)
    with pytest.raises(ValueError, match="Duplicate element id 'clash_id'"):
        solver.solve()


def test_group_add_invalid_type_raises_type_error() -> None:
    g = Group("g", "G")
    with pytest.raises(TypeError, match="Expected Element"):
        g.add("not an element")  # type: ignore

    with pytest.raises(TypeError, match="Expected Element"):
        g.add([123])  # type: ignore


def test_three_level_deep_nested_groups() -> None:
    solver = ConstraintSolver()

    root_g = Group("root", label="Level 1", padding=30.0, header_height=40.0).at(
        100.0, 100.0
    )
    mid_g = Group("mid", label="Level 2", padding=20.0, header_height=30.0)
    leaf_g = Group("leaf", label="Level 3", padding=10.0, header_height=20.0)
    item = Shape("item", label="Item", width=60.0, height=30.0)

    leaf_g.add(item)
    mid_g.add(leaf_g)
    root_g.add(mid_g)

    solver.add(root_g)
    solver.solve()

    assert root_g.bounds.left == 100.0
    assert root_g.bounds.top == 100.0

    # mid inside root
    assert mid_g.bounds.left == root_g.bounds.left + 30.0
    assert mid_g.bounds.top == root_g.bounds.top + 30.0 + 40.0

    # leaf inside mid
    assert leaf_g.bounds.left == mid_g.bounds.left + 20.0
    assert leaf_g.bounds.top == mid_g.bounds.top + 20.0 + 30.0

    # item inside leaf
    assert item.bounds.left == leaf_g.bounds.left + 10.0
    assert item.bounds.top == leaf_g.bounds.top + 10.0 + 20.0


def test_group_self_addition_raises_value_error() -> None:
    g = Group("g_self", "Self Group")
    with pytest.raises(ValueError, match="Cannot add group 'g_self' to itself"):
        g.add(g)


def test_group_cyclic_ancestry_raises_value_error() -> None:
    g_parent = Group("g_parent", "Parent Group")
    g_child = Group("g_child", "Child Group")
    g_grandchild = Group("g_grandchild", "Grandchild Group")

    g_parent.add(g_child)
    g_child.add(g_grandchild)

    # Attempting to add g_parent to g_grandchild creates an ancestry cycle
    with pytest.raises(ValueError, match="Cyclic group hierarchy detected"):
        g_grandchild.add(g_parent)


def test_group_reparenting_detaches_from_old_parent() -> None:
    g1 = Group("g1", "Old Group")
    g2 = Group("g2", "New Group")
    s = Shape("s", "Item")

    g1.add(s)
    assert s in g1.children
    assert s.parent is g1

    g2.add(s)
    assert s in g2.children
    assert s.parent is g2
    assert s not in g1.children


def test_group_manual_sizing_with_is_auto_sized_false() -> None:
    g = Group("g_fixed", "Fixed Group", padding=20.0, header_height=30.0)
    g.bounds = Rect(50.0, 50.0, 300.0, 200.0)
    g.width = 300.0
    g.height = 200.0
    g.is_auto_sized = False

    s = Shape("s", "Item", width=50.0, height=30.0).at(0.0, 0.0)
    s.bounds = Rect(0.0, 0.0, 50.0, 30.0)
    g.add(s)

    b = g.calculate_bounds()
    # Should not recalculate bounds from children when is_auto_sized=False
    assert b == Rect(50.0, 50.0, 300.0, 200.0)
    assert g.bounds == Rect(50.0, 50.0, 300.0, 200.0)


def test_group_flow_layout_engines_and_custom_pluggable() -> None:
    from diagrams_as_code.elements import RelativeConstraint
    from diagrams_as_code.layout import (
        GridLayout,
        HorizontalFlowLayout,
        VerticalFlowLayout,
    )

    # 1. VerticalFlowLayout
    g1 = Group("g1", "Vertical Group")
    s1 = Shape("s1", "S1", width=100.0, height=50.0)
    s2 = Shape("s2", "S2", width=100.0, height=50.0)
    s3 = Shape("s3", "S3", width=100.0, height=50.0)
    g1.add(s1, s2, s3)
    g1.flow(VerticalFlowLayout(margin=30.0, align="center"))

    assert len(s2.constraints) == 1
    assert isinstance(s2.constraints[0], RelativeConstraint)
    assert s2.constraints[0].direction == "below"
    assert s2.constraints[0].margin == 30.0
    assert s2.constraints[0].align == "center"
    assert s2.constraints[0]._auto_layout is True

    # 2. HorizontalFlowLayout
    g2 = Group("g2", "Horizontal Group")
    h1 = Shape("h1", "H1", width=100.0, height=50.0)
    h2 = Shape("h2", "H2", width=100.0, height=50.0)
    g2.add(h1, h2)
    g2.flow(HorizontalFlowLayout(margin=15.0, align="bottom"))

    assert len(h2.constraints) == 1
    assert isinstance(h2.constraints[0], RelativeConstraint)
    assert h2.constraints[0].direction == "right"
    assert h2.constraints[0].margin == 15.0
    assert h2.constraints[0].align == "bottom"

    # 3. GridLayout
    g3 = Group("g3", "Grid Group")
    shapes = [Shape(f"g_{i}", f"G{i}", width=50.0, height=30.0) for i in range(4)]
    g3.add(*shapes)
    g3.flow(GridLayout(columns=2, margin_x=10.0, margin_y=20.0))

    # shapes[1] is col 1, row 0 -> right of shapes[0]
    assert shapes[1].constraints[0].direction == "right"
    assert shapes[1].constraints[0].target is shapes[0]
    # shapes[2] is col 0, row 1 -> below shapes[0]
    assert shapes[2].constraints[0].direction == "below"
    assert shapes[2].constraints[0].target is shapes[0]
    # shapes[3] is col 1, row 1 -> right of shapes[2]
    assert shapes[3].constraints[0].direction == "right"
    assert shapes[3].constraints[0].target is shapes[2]

    # 4. Adding a new child dynamically reapplies layout
    h3 = Shape("h3", "H3", width=100.0, height=50.0)
    g2.add(h3)
    assert len(h3.constraints) == 1
    assert h3.constraints[0].target is h2
    assert h3.constraints[0].direction == "right"

    # 5. Custom pluggable layout engine
    class ReverseVerticalLayout:
        mode = "reverse_vertical"

        def apply(self, group: Group) -> None:
            children = group.children
            for ch in children:
                ch.constraints = [c for c in ch.constraints if not c.get("_auto_layout")]
            for i in range(1, len(children)):
                prev = children[i - 1]
                curr = children[i]
                curr.constraints.append(
                    RelativeConstraint(
                        target=prev,
                        direction="above",
                        margin=10.0,
                        align="center",
                        _auto_layout=True,
                    )
                )

    g_custom = Group("g_custom", "Custom Group")
    c1 = Shape("c1", "C1")
    c2 = Shape("c2", "C2")
    g_custom.add(c1, c2)
    g_custom.flow(ReverseVerticalLayout())
    assert c2.constraints[0].direction == "above"

