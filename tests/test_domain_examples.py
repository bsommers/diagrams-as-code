"""Test suite executing and verifying all 70 domain example diagram scripts across 7 domains."""

from __future__ import annotations

import glob
import os
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
EXAMPLE_SCRIPTS = sorted(REPO_ROOT.glob("examples/*/*.py"))

EXPECTED_DOMAINS = {
    "cloud",
    "ai",
    "computer",
    "datacenter",
    "business_process",
    "cybersecurity",
    "network_engineering",
}


def test_example_script_discovery() -> None:
    """Verify that exactly 70 example scripts exist across 7 domains."""
    assert len(EXAMPLE_SCRIPTS) == 70
    domain_counts: dict[str, int] = {}
    for p in EXAMPLE_SCRIPTS:
        domain = p.parent.name
        domain_counts[domain] = domain_counts.get(domain, 0) + 1

    assert set(domain_counts.keys()) == EXPECTED_DOMAINS
    for d, count in domain_counts.items():
        assert count == 10, f"Domain {d} has {count} scripts, expected 10."


@pytest.mark.parametrize(
    "script_path",
    EXAMPLE_SCRIPTS,
    ids=[f"{p.parent.name}/{p.stem}" for p in EXAMPLE_SCRIPTS],
)
def test_example_diagram_execution(script_path: Path) -> None:
    """Execute each example script and verify valid SVG and Markdown BOM generation."""
    # Execute script
    res = subprocess.run(
        [sys.executable, str(script_path)],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
    )
    assert res.returncode == 0, f"Script {script_path} failed:\n{res.stderr}"

    domain = script_path.parent.name
    stem = script_path.stem
    output_dir = REPO_ROOT / "output" / domain

    svg_file = output_dir / f"{stem}.svg"
    png_file = output_dir / f"{stem}.png"
    readme_file = output_dir / f"{stem}_README.md"

    # Verify SVG file exists and has non-zero size
    assert svg_file.exists(), f"SVG output missing: {svg_file}"
    assert svg_file.stat().st_size > 0

    # Verify PNG file exists and has valid magic bytes
    assert png_file.exists(), f"PNG output missing: {png_file}"
    assert png_file.stat().st_size > 0
    assert png_file.read_bytes()[:8] == b"\x89PNG\r\n\x1a\n", f"Invalid PNG magic bytes in {png_file}"

    # Verify SVG XML validity
    svg_content = svg_file.read_text(encoding="utf-8")
    tree = ET.fromstring(svg_content)
    tag = tree.tag.split("}")[-1] if "}" in tree.tag else tree.tag
    assert tag == "svg", f"Expected root <svg> tag in {svg_file}, got {tree.tag}"

    # Verify viewBox and dimensions
    assert "viewBox" in tree.attrib or ("width" in tree.attrib and "height" in tree.attrib)

    # Verify defs exists (markers, gradients, styles)
    defs = [elem for elem in tree.iter() if elem.tag.endswith("defs")]
    assert len(defs) >= 1, f"Missing <defs> section in {svg_file}"

    # Verify README BOM exists and contains required sections
    assert readme_file.exists(), f"README output missing: {readme_file}"
    readme_content = readme_file.read_text(encoding="utf-8")
    assert "## Bill of Materials" in readme_content
    assert "## Connections" in readme_content
    assert f"./{stem}.svg" in readme_content
