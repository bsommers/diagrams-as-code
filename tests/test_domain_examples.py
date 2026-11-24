"""Test suite executing and verifying all 143 domain example diagram scripts across 13 domains."""

from __future__ import annotations

import glob
import os
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
EXPECTED_DOMAINS = {
    "cloud",
    "ai",
    "computer",
    "datacenter",
    "business_process",
    "cybersecurity",
    "network_engineering",
    "iiot",
    "database",
    "enterprise_architecture",
    "manufacturing",
    "mind_map",
    "computer_science",
}

#: The domain galleries. Other example sets (``examples/primitives``) have their own tests.
EXAMPLE_SCRIPTS = sorted(
    p for p in REPO_ROOT.glob("examples/*/*.py") if p.parent.name in EXPECTED_DOMAINS
)


def _load_diagram(script_path: Path):
    """The diagram ``script_path`` builds, without rendering it."""
    import importlib.util

    spec = importlib.util.spec_from_file_location(f"_domain_{script_path.stem}", script_path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.diagram()


def test_example_script_discovery() -> None:
    """Verify that exactly 143 example scripts exist across 13 domains."""
    assert len(EXAMPLE_SCRIPTS) == 143
    domain_counts: dict[str, int] = {}
    for p in EXAMPLE_SCRIPTS:
        domain = p.parent.name
        domain_counts[domain] = domain_counts.get(domain, 0) + 1

    assert set(domain_counts.keys()) == EXPECTED_DOMAINS
    for d, count in domain_counts.items():
        assert count == 11, f"Domain {d} has {count} scripts, expected 11."


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
    output_dir = REPO_ROOT / "examples" / domain

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

    # Verify that shapes are not all stacked at (0, 0)
    rects = []
    for g in tree.findall(".//{http://www.w3.org/2000/svg}g"):
        gid = g.attrib.get("id", "")
        if gid and not gid.startswith("group_") and gid != "shadow":
            r = g.find("{http://www.w3.org/2000/svg}rect")
            if r is not None:
                rects.append((float(r.attrib.get("x", 0)), float(r.attrib.get("y", 0))))
    if len(rects) > 1:
        assert not all(x == 0.0 and y == 0.0 for x, y in rects), f"Shapes stacked at (0,0) in {svg_file}"

    # Verify README BOM exists and contains required sections
    assert readme_file.exists(), f"README output missing: {readme_file}"
    readme_content = readme_file.read_text(encoding="utf-8")
    assert "## Bill of Materials" in readme_content
    # Figures without edges (a chart, say) get no Connections section.
    if _load_diagram(script_path).edges:
        assert "## Connections" in readme_content
    else:
        assert "## Connections" not in readme_content
    assert f"./{stem}.svg" in readme_content


def test_domain_theme_variety() -> None:
    """Verify that each domain showcases at least 3 to 5 distinct theme varieties across its examples."""
    import re

    domain_themes: dict[str, set[str]] = {}
    for p in EXAMPLE_SCRIPTS:
        domain = p.parent.name
        content = p.read_text(encoding="utf-8")
        match = re.search(r'theme="([^"]+)"', content)
        if match:
            theme_name = match.group(1)
            domain_themes.setdefault(domain, set()).add(theme_name)

    for domain in EXPECTED_DOMAINS:
        themes = domain_themes.get(domain, set())
        assert len(themes) >= 3, f"Domain '{domain}' has only {len(themes)} themes ({themes}), expected at least 3-5 varieties."



#: Galleries added after the 13 reference domains. Each is checked for one thing here:
#: the committed SVG is exactly what its script renders today. (``chemistry`` is covered by
#: ``test_textbook_examples.py``.)
NEWER_GALLERIES = (
    "agentic_dev", "semiconductor", "data_engineering", "ml_models", "devops", "biology",
    "chemical_engineering", "org", "electronics", "sequence", "project_management",
)
NEWER_SCRIPTS = sorted(
    p for d in NEWER_GALLERIES for p in (REPO_ROOT / "examples" / d).glob("*.py")
)


def test_newer_gallery_discovery() -> None:
    """Each newer gallery has its scripts (ten each; sequence 3, project_management 11)."""
    counts: dict[str, int] = {}
    for p in NEWER_SCRIPTS:
        counts[p.parent.name] = counts.get(p.parent.name, 0) + 1
    expected = {d: 10 for d in NEWER_GALLERIES}
    expected.update(sequence=3, project_management=12)
    assert counts == expected


@pytest.mark.parametrize(
    "script_path",
    NEWER_SCRIPTS,
    ids=[f"{p.parent.name}/{p.stem}" for p in NEWER_SCRIPTS],
)
def test_newer_gallery_committed_svg_matches_script(script_path: Path) -> None:
    """The committed SVG beside each script is exactly what the script renders."""
    committed = script_path.with_suffix(".svg")
    assert committed.exists(), f"run `uv run python {script_path.relative_to(REPO_ROOT)}`"
    assert committed.read_text(encoding="utf-8") == _load_diagram(script_path).render_svg()
