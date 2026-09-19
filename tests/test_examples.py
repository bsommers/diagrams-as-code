"""Tests verifying that all example scripts and main.py execute cleanly and produce valid diagrams."""
from __future__ import annotations

import os
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent


def _run_script(script_rel_path: str, *args: str) -> subprocess.CompletedProcess[str]:
    script_path = REPO_ROOT / script_rel_path
    cmd = [sys.executable, str(script_path), *args]
    env = dict(os.environ)
    src_dir = str(REPO_ROOT / "src")
    existing_pythonpath = env.get("PYTHONPATH", "")
    env["PYTHONPATH"] = f"{src_dir}:{existing_pythonpath}" if existing_pythonpath else src_dir
    result = subprocess.run(
        cmd,
        cwd=str(REPO_ROOT),
        capture_output=True,
        text=True,
        env=env,
    )
    return result


def test_01_mockup_slide_execution(tmp_path: Path) -> None:
    result = _run_script("examples/01_mockup_slide.py", str(tmp_path))
    assert result.returncode == 0, f"Script failed with stderr:\n{result.stderr}"

    svg_path = tmp_path / "mockup_slide.svg"
    assert svg_path.exists(), "Expected mockup_slide.svg in tmp_path"

    svg_content = svg_path.read_text(encoding="utf-8")
    root = ET.fromstring(svg_content)
    assert root.tag.endswith("svg")

    # Assert group labels
    assert "On-Premise (Baltimore)" in svg_content
    assert "IIoT Cloud (Managed)" in svg_content
    assert "Remote Monitoring" in svg_content

    # Assert node labels
    assert "IIoT Edge" in svg_content
    assert "Grafana" in svg_content

    # Assert badges and markers
    assert "Secure MQTT Bridge" in svg_content
    markers = root.findall(".//{http://www.w3.org/2000/svg}marker")
    assert len(markers) > 0, "Expected SVG marker elements for arrowheads"

    # Assert living documentation README was generated in tmp_path
    readme_path = tmp_path / "mockup_slide_README.md"
    assert readme_path.exists(), "Expected mockup_slide_README.md in tmp_path"
    readme_content = readme_path.read_text(encoding="utf-8")
    assert "Bill of Materials" in readme_content
    assert "Connections" in readme_content


def test_02_high_availability_execution(tmp_path: Path) -> None:
    result = _run_script("examples/02_high_availability.py", str(tmp_path))
    assert result.returncode == 0, f"Script failed with stderr:\n{result.stderr}"

    svg_path = tmp_path / "high_availability.svg"
    assert svg_path.exists(), "Expected high_availability.svg in tmp_path"

    svg_content = svg_path.read_text(encoding="utf-8")
    root = ET.fromstring(svg_content)
    assert root.tag.endswith("svg")

    # Assert group labels
    assert "Production Site (Baltimore)" in svg_content
    assert "IIoT HA Cluster" in svg_content

    # Assert node labels
    assert "Load Balancer" in svg_content
    assert "Node 1" in svg_content
    assert "Node 2" in svg_content
    assert "Node 3" in svg_content

    # Assert labels, badges, and dotted discovery lines
    assert "Cluster Discovery" in svg_content
    assert 'stroke-dasharray="2,2"' in svg_content or 'stroke-dasharray="5,5"' in svg_content

    # Assert living documentation README was generated in tmp_path
    readme_path = tmp_path / "high_availability_README.md"
    assert readme_path.exists(), "Expected high_availability_README.md in tmp_path"
    readme_content = readme_path.read_text(encoding="utf-8")
    assert "Bill of Materials" in readme_content
    assert "Connections" in readme_content


def test_03_sparkplug_pipeline_execution(tmp_path: Path) -> None:
    result = _run_script("examples/03_sparkplug_pipeline.py", str(tmp_path))
    assert result.returncode == 0, f"Script failed with stderr:\n{result.stderr}"

    svg_path = tmp_path / "sparkplug_pipeline.svg"
    assert svg_path.exists(), "Expected sparkplug_pipeline.svg in tmp_path"

    svg_content = svg_path.read_text(encoding="utf-8")
    root = ET.fromstring(svg_content)
    assert root.tag.endswith("svg")

    # Assert node labels
    assert "Sensors &amp; PLCs" in svg_content or "Sensors & PLCs" in svg_content
    assert "Kafka" in svg_content
    assert "InfluxDB" in svg_content
    assert "SCADA" in svg_content

    # Assert protocol badges
    assert "spBv1.0" in svg_content
    assert "Modbus" in svg_content or "OPC UA" in svg_content

    # Assert living documentation README was generated in tmp_path
    readme_path = tmp_path / "sparkplug_pipeline_README.md"
    assert readme_path.exists(), "Expected sparkplug_pipeline_README.md in tmp_path"
    readme_content = readme_path.read_text(encoding="utf-8")
    assert "Bill of Materials" in readme_content
    assert "Connections" in readme_content


def test_main_execution(tmp_path: Path) -> None:
    result = _run_script("main.py", str(tmp_path))
    assert result.returncode == 0, f"Script failed with stderr:\n{result.stderr}"

    svg_path = tmp_path / "main_architecture.svg"
    assert svg_path.exists(), "Expected main_architecture.svg in tmp_path"

    svg_content = svg_path.read_text(encoding="utf-8")
    root = ET.fromstring(svg_content)
    assert root.tag.endswith("svg")

    # Assert group and node labels in main diagram
    assert "Plant Floor (Edge Tier)" in svg_content
    assert "Cloud Platform (UNS Tier)" in svg_content
    assert "Enterprise Operations" in svg_content
    assert "Automation PLC" in svg_content
    assert "Enterprise MQTT Broker" in svg_content

    # Assert living documentation README was generated in tmp_path
    readme_path = tmp_path / "main_README.md"
    assert readme_path.exists(), "Expected main_README.md in tmp_path"
    readme_content = readme_path.read_text(encoding="utf-8")
    assert "Bill of Materials" in readme_content
    assert "Connections" in readme_content
    assert "Enterprise MQTT Broker Cluster" in readme_content
    assert "HiveMQ" not in readme_content
