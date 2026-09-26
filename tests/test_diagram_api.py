"""Integration tests for fluent Diagram context manager API and edge operators."""
import os
from pathlib import Path
import pytest

from iiot_diagrams import Diagram, Shape, Group, Edge
from iiot_diagrams.geometry import Rect, Anchor, Point


def test_fluent_diagram_api(tmp_path):
    """Verify fluent Diagram context manager workflow from brief."""
    out_svg = tmp_path / "test_diagram.svg"
    with Diagram("IIoT Architecture", width=1000, height=600) as diag:
        with diag.group("On-Premises Plant", padding=20) as plant:
            plc = diag.shape("PLC Modbus").at(50, 80)
            edge = diag.shape("Edge Gateway").below(plc, margin=40)
            plc >> edge

        with diag.group("IIoT Cloud Platform").right_of(plant, margin=80) as cloud:
            broker = diag.shape("Central Broker").at(50, 80)

        edge >> diag.edge("MQTT TLS") >> broker

    diag.render_svg(str(out_svg))
    assert out_svg.exists()
    content = out_svg.read_text(encoding="utf-8")
    assert "On-Premises Plant" in content
    assert "IIoT Cloud Platform" in content
    assert "MQTT TLS" in content
    assert "<svg" in content
    assert "</svg>" in content


def test_edge_operator_combinations():
    """Verify operator overloading >> for single, chained, lists, and edge builders."""
    with Diagram("Operator Test") as diag:
        s1 = diag.shape("S1").at(10, 10)
        s2 = diag.shape("S2").at(150, 10)
        s3 = diag.shape("S3").at(300, 10)
        s4 = diag.shape("S4").at(450, 10)

        # Direct chain s1 >> s2 >> s3
        res = s1 >> s2 >> s3
        assert res is s3

        # List fan-out: s1 >> [s2, s4]
        s1 >> [s2, s4]

        # List fan-in: [s1, s2] >> s4
        [s1, s2] >> s4

        # EdgeBuilder chaining
        s3 >> diag.edge("MQTT", color="#FF0000", style="dashed") >> s4

        # List fan-in through EdgeBuilder
        [s2, s3] >> diag.edge("OPC UA", color="#00FF00") >> s4

        # List fan-out through EdgeBuilder
        s1 >> diag.edge("Fanout", color="#0000FF") >> [s2, s3]

    # Verify edge count and properties
    labels = [e.label for e in diag.edges]
    assert "MQTT" in labels
    assert "OPC UA" in labels
    assert "Fanout" in labels

    # Find MQTT edge
    mqtt_edges = [e for e in diag.edges if e.label == "MQTT"]
    assert len(mqtt_edges) == 1
    assert mqtt_edges[0].source is s3
    assert mqtt_edges[0].target is s4
    assert mqtt_edges[0].color == "#FF0000"
    assert mqtt_edges[0].style == "dashed"

    # Find OPC UA edges (2 sources fan into s4)
    opc_edges = [e for e in diag.edges if e.label == "OPC UA"]
    assert len(opc_edges) == 2
    assert {e.source for e in opc_edges} == {s2, s3}
    assert all(e.target is s4 for e in opc_edges)

    # Find Fanout edges (s1 fans out to s2 and s3)
    fanout_edges = [e for e in diag.edges if e.label == "Fanout"]
    assert len(fanout_edges) == 2
    assert all(e.source is s1 for e in fanout_edges)
    assert {e.target for e in fanout_edges} == {s2, s3}


def test_nested_group_context_and_membership():
    """Verify nested group contexts automatically establish parent-child hierarchy and membership."""
    with Diagram("Hierarchy Test") as diag:
        with diag.group("Plant") as plant:
            plc = diag.shape("Plant PLC").at(20, 20)
            with diag.group("Cell") as cell:
                robot = diag.shape("Cell Robot").at(40, 40)
            hmi = diag.shape("Plant HMI").at(200, 20)

    # Verify memberships
    assert plc.parent is plant
    assert hmi.parent is plant
    assert cell.parent is plant
    assert robot.parent is cell
    assert plc in plant.children
    assert hmi in plant.children
    assert cell in plant.children
    assert robot in cell.children
    assert robot not in plant.children


def test_decoupled_definition_and_late_placement():
    """Verify shapes can be instantiated without coordinates, moved, cleared, and added."""
    # Instantiated outside any diagram without coordinates
    s_standalone = Shape("sensor_raw", "Pressure Sensor", width=110, height=55)
    assert s_standalone.bounds == Rect(0.0, 0.0, 110.0, 55.0)
    assert s_standalone.constraints == []

    # Stamped/moved with move_to
    s_standalone.move_to(250, 180)
    assert s_standalone.bounds.x == 250
    assert s_standalone.bounds.y == 180

    # Reset placement
    s_standalone.clear_constraints()
    assert s_standalone.constraints == []

    with Diagram("Late Placement") as diag:
        diag.add(s_standalone)
        other = diag.shape("Receiver").at(50, 50)
        s_standalone.right_of(other, margin=60)

    # Diagram auto-solves on exit
    assert s_standalone.bounds.x == 50 + other.bounds.width + 60


def test_shape_cloning_from_template():
    """Verify Shape.clone() creates independent copies with overrides and fresh constraints."""
    tpl = Shape(
        "tpl_drive",
        "VFD Inverter",
        width=140,
        height=70,
        kind="cylinder",
        icon="cpu",
        metadata={"voltage": "480V", "bus": "Modbus"},
    )
    tpl.at(10, 10)  # Template has a constraint

    # Clone with custom ID and label
    d1 = tpl.clone("vfd_1", label="Pump VFD 1")
    assert d1.id == "vfd_1"
    assert d1.label == "Pump VFD 1"
    assert d1.width == 140
    assert d1.height == 70
    assert d1.kind == "cylinder"
    assert d1.icon == "cpu"
    assert d1.metadata["voltage"] == "480V"
    assert d1.constraints == []  # constraints reset

    # Clone with auto-generated ID and metadata override
    d2 = tpl.clone(metadata={"voltage": "240V"})
    assert d2.id.startswith("tpl_drive")
    assert d2.metadata["voltage"] == "240V"
    assert d2.metadata["bus"] == "Modbus"

    # Position clones in diagram
    with Diagram("VFD Cluster") as diag:
        diag.add(d1.at(50, 100))
        diag.add(d2.below(d1, margin=25))

    assert d1.bounds.x == 50
    assert d1.bounds.y == 100
    assert d2.bounds.y == 100 + 70 + 25


def test_solver_graceful_handling_of_unconstrained_elements():
    """Verify solver does not crash on unconstrained elements, keeping their initial bounds."""
    with Diagram("Unconstrained Diagram") as diag:
        s1 = diag.shape("Default Position Shape")
        s2 = diag.shape("Another Free Shape")
        # Explicit bounds without constraints
        s2.bounds = Rect(400, 300, 130, 60)

    assert s1.bounds == Rect(0.0, 0.0, 130.0, 60.0)
    assert s2.bounds == Rect(400.0, 300.0, 130.0, 60.0)


def test_render_svg_string_and_file_creation(tmp_path):
    """Verify render_svg returns SVG string and optionally writes to disk."""
    out_file = tmp_path / "subdir" / "diagram.svg"
    with Diagram("Export Test", width=800, height=500, theme="iiot_dark_gold") as diag:
        diag.shape("Core Controller").at(100, 100)

    # Render to string without file
    svg_str = diag.render_svg()
    assert svg_str.startswith("<svg")
    assert "Core Controller" in svg_str

    # Render to nested path
    svg_written = diag.render_svg(out_file)
    assert out_file.exists()
    assert out_file.read_text(encoding="utf-8") == svg_str
    assert svg_written == svg_str


def test_diagram_add_multiple_and_sequences():
    """Verify diag.add accepts multiple shapes, lists, and groups."""
    with Diagram("Batch Add") as diag:
        s1 = Shape("b1", "Batch 1")
        s2 = Shape("b2", "Batch 2")
        s3 = Shape("b3", "Batch 3")
        g = Group("bg", "Batch Group")

        diag.add(s1)
        diag.add(s2, s3)
        diag.add(g)

    assert s1 in diag.shapes
    assert s2 in diag.shapes
    assert s3 in diag.shapes
    assert g in diag.groups


def test_group_context_move_to_and_relative_chaining():
    """Verify group context supports move_to, clear_constraints, and flow placement."""
    with Diagram("Group Move Test") as diag:
        with diag.group("Source Group").move_to(100, 100) as g1:
            diag.shape("S1").at(120, 120)

        with diag.group("Target Group").below(g1, margin=60) as g2:
            diag.shape("S2").at(120, 250)

    assert g1.bounds.top == 100.0
    assert g2.bounds.top >= g1.bounds.bottom + 60.0


def test_render_png_missing_library_raises_runtime_error(tmp_path):
    """Verify render_png raises informative RuntimeError if PNG backends are missing."""
    with Diagram("PNG Test") as diag:
        diag.shape("Node").at(10, 10)

    png_path = tmp_path / "out.png"
    # When cairosvg / resvg are not installed, raises RuntimeError
    try:
        diag.render_png(png_path)
    except RuntimeError as exc:
        assert "PNG rendering requires" in str(exc)


def test_diagram_context_exception_handling_restores_stack():
    """Verify diagram context restores active stack even when an exception is raised."""
    assert Diagram.get_current() is None
    with pytest.raises(ValueError, match="Intentional failure"):
        with Diagram("Failing Diagram"):
            assert Diagram.get_current() is not None
            raise ValueError("Intentional failure")

    assert Diagram.get_current() is None


def test_edge_builder_validation_and_errors():
    """Verify EdgeBuilder enforces source presence and type constraints."""
    with Diagram("Builder Error Test") as diag:
        s = diag.shape("Node")
        b = diag.edge("Label")
        with pytest.raises(ValueError, match="requires a source"):
            b >> s

        with pytest.raises(TypeError, match="Expected Element"):
            "invalid" >> b >> s  # type: ignore

        with pytest.raises(TypeError, match="Expected Element"):
            s >> b >> "invalid"  # type: ignore


def test_diagram_add_invalid_type_raises_type_error():
    """Verify diag.add rejects non-Element types."""
    with Diagram("Invalid Add") as diag:
        with pytest.raises(TypeError, match="Expected Element"):
            diag.add(12345)  # type: ignore


def test_auto_id_avoids_duplicate_explicit_id():
    """Verify auto-generation increments when an explicit ID already exists."""
    with Diagram("ID Collisions") as diag:
        s1 = diag.shape("Shape 1", id="shape_1")
        s2 = diag.shape("Shape 2")  # Auto ID should advance past shape_1 to shape_2
        assert s1.id == "shape_1"
        assert s2.id == "shape_2"
        assert s1.id != s2.id


def test_diag_add_nested_groups_and_edges():
    """Verify diag.add() recursively registers nested groups, child shapes, and edges."""
    parent = Group("g_parent", "Parent Group")
    child = Group("g_child", "Child Group")
    s1 = Shape("s1", "Sensor 1")
    s2 = Shape("s2", "Sensor 2")
    child.add(s1)
    parent.add(child, s2)
    edge = Edge(s1, s2, label="Direct")

    with Diagram("Recursive Add Test") as diag:
        diag.add(parent, edge)

    assert parent in diag.groups
    assert child in diag.groups
    assert s1 in diag.shapes
    assert s2 in diag.shapes
    assert edge in diag.edges
    assert parent in diag.solver.elements
    assert child in diag.solver.elements
    assert s1 in diag.solver.elements
    assert s2 in diag.solver.elements


def test_shape_extra_kwargs_and_clone_metadata():
    """Verify diag.shape and shape.clone accept arbitrary kwargs into metadata."""
    with Diagram("Extra Kwargs Test") as diag:
        db = diag.shape("DB", fill="blue", vendor="postgres")
        assert db.metadata["fill"] == "blue"
        assert db.metadata["vendor"] == "postgres"

        db2 = db.clone("db2", fill="red")
        assert db2.id == "db2"
        assert db2.metadata["fill"] == "red"
        assert db2.metadata["vendor"] == "postgres"


def test_unit_basis_property_on_diagram():
    """Verify unit_basis property returns valid UnitBasis sized to canvas."""
    with Diagram("Unit Basis Canvas", width=800, height=400) as diag:
        ub = diag.unit_basis
        assert ub.reference_size.width == 800.0
        assert ub.reference_size.height == 400.0
        pt = ub.to_absolute(0.5, 0.25)
        assert pt == Point(400.0, 100.0)


def test_atomic_validation_in_operator_lists():
    """Verify operator list connections fail atomically without partial side effects."""
    with Diagram("Atomic Validation") as diag:
        s1 = diag.shape("S1")
        s2 = diag.shape("S2")
        initial_edges = len(diag.edges)

        with pytest.raises(TypeError, match="Target must be Element"):
            s1 >> [s2, "invalid"]  # type: ignore
        assert len(diag.edges) == initial_edges

        with pytest.raises(TypeError, match="Source must be Element"):
            [s2, "invalid"] >> s1  # type: ignore
        assert len(diag.edges) == initial_edges

        with pytest.raises(TypeError, match="Expected Element in targets"):
            s1 >> diag.edge("Test") >> [s2, "invalid"]  # type: ignore
        assert len(diag.edges) == initial_edges

        with pytest.raises(TypeError, match="Expected Element in sources"):
            [s2, "invalid"] >> diag.edge("Test") >> s1  # type: ignore
        assert len(diag.edges) == initial_edges


def test_diagram_corner_radius_cascade_and_override() -> None:
    """Verify Diagram corner_radius cascades to fluent and connect edges, and allows explicit overrides."""
    with Diagram("Cascade Test", corner_radius=15.0) as diag:
        assert diag.corner_radius == 15.0
        assert diag.arc_radius == 15.0

        s1 = diag.shape("S1").at(0, 0)
        s2 = diag.shape("S2").at(200, 0)
        s3 = diag.shape("S3").at(400, 0)
        s4 = diag.shape("S4").at(600, 0)

        # Cascaded fluent edge (s1 >> s2)
        s1 >> s2

        # Explicit override with sharp corner (0.0)
        s2 >> diag.edge(corner_radius=0.0) >> s3

        # Explicit override with custom radius (25.0) via arc_radius alias
        s3 >> diag.edge(arc_radius=25.0) >> s4

    # On exit, diagram solves and edges are in diag.edges
    assert len(diag.edges) == 3
    e_cascaded, e_sharp, e_custom = diag.edges

    # First edge inherits diagram corner_radius
    assert e_cascaded.corner_radius == 15.0
    assert e_cascaded.arc_radius == 15.0

    # Second edge preserves explicit sharp override
    assert e_sharp.corner_radius == 0.0

    # Third edge preserves explicit custom override
    assert e_custom.corner_radius == 25.0

    # Test configure() update
    diag.configure(corner_radius=8.0)
    assert diag.corner_radius == 8.0
    assert diag.arc_radius == 8.0

    # Test setter validation on Diagram
    with pytest.raises(ValueError, match="non-negative finite float"):
        diag.corner_radius = -5.0
    with pytest.raises(ValueError, match="non-negative finite float"):
        diag.arc_radius = "invalid"  # type: ignore

