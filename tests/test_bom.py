"""Tests for Bill of Materials (BOM) & Living Documentation Generator."""
import json
from pathlib import Path
import pytest

from iiot_diagrams import Diagram
from iiot_diagrams.bom import BOMGenerator
from iiot_diagrams.connections import Port, Routing


def test_generate_bom_brief_contract():
    """Verify basic BOM generation matching task brief specification."""
    with Diagram("Baltimore Plant Architecture") as diag:
        plc = diag.shape("PLC Allen-Bradley", kind="sensor").at(10, 10)
        plc.metadata = {
            "model": "ControlLogix",
            "vendor": "Rockwell",
            "protocol": "EtherNet/IP",
        }
        edge = diag.shape("Edge Gateway", kind="gateway").right_of(plc, margin=30)
        edge.metadata = {"hardware": "Industrial IPC", "os": "Linux"}
        plc >> diag.edge("Modbus/TCP") >> edge

    bom = BOMGenerator(diag)

    # Default table with standard columns
    md_default = bom.to_markdown()
    assert (
        "| Symbol / ID | Label | Kind | Group | Technical Notes / Metadata |"
        in md_default
    )
    assert "ControlLogix" in md_default
    assert "Industrial IPC" in md_default
    assert "PLC Allen-Bradley" in md_default
    assert "Edge Gateway" in md_default

    # Custom column subset matching brief schema
    md_brief = bom.to_markdown(columns=["Symbol / ID", "Label", "Kind", "Metadata"])
    assert "| Symbol / ID | Label | Kind | Metadata |" in md_brief
    assert "ControlLogix" in md_brief
    assert "Industrial IPC" in md_brief


def test_bom_items_extraction():
    """Verify detailed item extraction including shapes, metadata, and parent groups."""
    with Diagram("Factory Automation") as diag:
        with diag.group("Cell 1") as g1:
            s1 = diag.shape("Robot Arm", kind="robot", model="KUKA KR6").at(20, 20)
            s2 = diag.shape("Conveyor Sensor", kind="sensor").below(s1, margin=20)
        s3 = diag.shape("Cloud Ingestion", kind="cloud").right_of(g1, margin=100)

    bom = BOMGenerator(diag)
    items = bom.items()

    assert len(items) == 3
    # Check s1
    item1 = next(it for it in items if it["id"] == s1.id)
    assert item1["label"] == "Robot Arm"
    assert item1["kind"] == "robot"
    assert item1["group"] == "Cell 1"
    assert item1["metadata"]["model"] == "KUKA KR6"

    # Check s2
    item2 = next(it for it in items if it["id"] == s2.id)
    assert item2["label"] == "Conveyor Sensor"
    assert item2["kind"] == "sensor"
    assert item2["group"] == "Cell 1"

    # Check s3 (ungrouped)
    item3 = next(it for it in items if it["id"] == s3.id)
    assert item3["label"] == "Cloud Ingestion"
    assert item3["kind"] == "cloud"
    assert item3["group"] is None


def test_bom_connections_extraction():
    """Verify connection extraction with endpoints, protocol labels, ports, and styling."""
    with Diagram("Network Topo") as diag:
        s1 = diag.shape("PLC").at(0, 0)
        s2 = diag.shape("Historian").at(200, 0)
        s3 = diag.shape("MES").at(200, 200)

        s1 >> diag.edge(
            "OPC UA",
            color="#FFC000",
            style="dashed",
            source_port=Port.EAST,
            target_port=Port.WEST,
            routing=Routing.ORTHOGONAL,
            metadata={"port_num": 4840, "encryption": "Basic256Sha256"},
        ) >> s2

        s2 >> diag.edge("SQL TLS", style="dotted", routing=Routing.DIRECT) >> s3

    bom = BOMGenerator(diag)
    conns = bom.connections()

    assert len(conns) == 2
    c1 = conns[0]
    assert c1["source"] == s1.id
    assert c1["source_label"] == "PLC"
    assert c1["target"] == s2.id
    assert c1["target_label"] == "Historian"
    assert c1["protocol"] == "OPC UA"
    assert c1["label"] == "OPC UA"
    assert c1["color"] == "#FFC000"
    assert c1["style"] == "dashed"
    assert c1["routing"] == "orthogonal"
    assert c1["source_port"] == "east"
    assert c1["target_port"] == "west"
    assert c1["metadata"]["port_num"] == 4840
    assert c1["metadata"]["encryption"] == "Basic256Sha256"

    c2 = conns[1]
    assert c2["source"] == s2.id
    assert c2["target"] == s3.id
    assert c2["protocol"] == "SQL TLS"
    assert c2["style"] == "dotted"
    assert c2["routing"] == "direct"


def test_bom_to_dict_and_to_json():
    """Verify dictionary export and JSON serialization."""
    with Diagram("Telemetry Platform") as diag:
        with diag.group("Edge"):
            s1 = diag.shape("Smart Meter", kind="meter", baud_rate=9600).at(10, 10)
        s2 = diag.shape("MQTT Broker", kind="server").at(200, 10)
        s1 >> diag.edge("MQTT") >> s2

    bom = BOMGenerator(diag)
    d = bom.to_dict()

    assert d["title"] == "Telemetry Platform"
    assert d["total_components"] == 2
    assert d["total_connections"] == 1
    assert len(d["items"]) == 2
    assert len(d["connections"]) == 1
    assert len(d["groups"]) == 1
    assert d["groups"][0]["label"] == "Edge"
    assert s1.id in d["groups"][0]["children"]

    json_str = bom.to_json(indent=2)
    parsed = json.loads(json_str)
    assert parsed["title"] == "Telemetry Platform"
    assert parsed["total_components"] == 2
    assert parsed["items"][0]["label"] == "Smart Meter"


def test_bom_to_markdown_formatting_and_escaping():
    """Verify markdown table formatting, pipe escaping, and title options."""
    with Diagram("Safe Escaping") as diag:
        s1 = diag.shape("Sensor | Alpha", kind="sensor").at(0, 0)
        s1.metadata = {"range": "0|100 bar", "note": "High | Precision"}

    bom = BOMGenerator(diag)
    md = bom.to_markdown(title="Equipment Inventory")

    assert "## Equipment Inventory" in md
    assert r"Sensor \| Alpha" in md
    assert r"0\|100 bar" in md
    assert r"High \| Precision" in md

    # Without title
    md_notitle = bom.to_markdown(title="")
    assert "##" not in md_notitle
    assert "| Symbol / ID |" in md_notitle


def test_bom_to_markdown_with_image_file():
    """Verify image embedding in markdown output."""
    with Diagram("Visual Diag") as diag:
        diag.shape("Server").at(0, 0)

    bom = BOMGenerator(diag)
    md = bom.to_markdown(image_file="docs/architecture.svg")

    assert "![Architecture Diagram](./docs/architecture.svg)" in md
    assert "## Bill of Materials" in md


def test_bom_connections_to_markdown():
    """Verify connection table generation in markdown."""
    with Diagram("Bus Diagram") as diag:
        s1 = diag.shape("PLC").at(0, 0)
        s2 = diag.shape("HMI").at(100, 0)
        s1 >> diag.edge("Modbus RTU", style="dashed") >> s2

    bom = BOMGenerator(diag)
    md_conns = bom.connections_to_markdown()

    assert "## Connections" in md_conns
    assert "| Source | Target | Protocol / Label | Style | Routing |" in md_conns
    assert "PLC" in md_conns
    assert "HMI" in md_conns
    assert "Modbus RTU" in md_conns
    assert "dashed" in md_conns


def test_bom_generate_readme_file_output(tmp_path: Path):
    """Verify generate_readme produces complete living doc file on disk."""
    out_file = tmp_path / "docs" / "README.md"
    with Diagram("Plant Architecture") as diag:
        with diag.group("Shop Floor"):
            s1 = diag.shape("Drive Controller", kind="drive", vendor="ABB").at(10, 10)
        s2 = diag.shape("Edge Node", kind="gateway").at(200, 10)
        s1 >> diag.edge("EtherNet/IP") >> s2

    bom = BOMGenerator(diag)
    content = bom.generate_readme(
        diagram_name="Plant_Architecture",
        image_file="plant.svg",
        output_path=str(out_file),
    )

    assert out_file.exists()
    file_text = out_file.read_text(encoding="utf-8")
    assert file_text == content

    assert "# Plant Architecture" in file_text
    assert "![Architecture Diagram](./plant.svg)" in file_text
    assert "## Bill of Materials" in file_text
    assert "Drive Controller" in file_text
    assert "Shop Floor" in file_text
    assert "ABB" in file_text


def test_diagram_bom_property_and_generate_readme(tmp_path: Path):
    """Verify Diagram context manager exposes diag.bom and diag.generate_readme."""
    readme_path = tmp_path / "README.md"
    with Diagram("Distributed SCADA") as diag:
        s1 = diag.shape("RTU").at(0, 0)
        s2 = diag.shape("MTU").at(150, 0)
        s1 >> diag.edge("DNP3") >> s2

        # Verify diag.bom property
        assert isinstance(diag.bom, BOMGenerator)
        assert len(diag.bom.items()) == 2

        # Verify diag.generate_readme()
        returned_md = diag.generate_readme(
            image_file="scada.png", output_path=readme_path
        )

    assert readme_path.exists()
    assert "# Distributed SCADA" in returned_md
    assert "![Architecture Diagram](./scada.png)" in returned_md
    assert "DNP3" not in returned_md  # DNP3 is on the edge, BOM table lists components
    assert "RTU" in returned_md
    assert "MTU" in returned_md


def test_bom_empty_diagram():
    """Verify BOM behavior on an empty diagram without errors."""
    with Diagram("Empty System") as diag:
        pass

    bom = BOMGenerator(diag)
    assert bom.items() == []
    assert bom.connections() == []

    d = bom.to_dict()
    assert d["total_components"] == 0
    assert d["total_connections"] == 0

    md = bom.to_markdown()
    assert "## Bill of Materials" in md
    assert (
        "| Symbol / ID | Label | Kind | Group | Technical Notes / Metadata |" in md
    )


def test_package_re_export():
    """Verify BOMGenerator is properly re-exported in package __all__."""
    import iiot_diagrams

    assert hasattr(iiot_diagrams, "BOMGenerator")
    assert "BOMGenerator" in iiot_diagrams.__all__
    assert iiot_diagrams.BOMGenerator is BOMGenerator

