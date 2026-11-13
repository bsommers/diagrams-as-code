"""The technical figures: the reference reproduction and ten more (EX-01, EX-02)."""
from __future__ import annotations

import importlib.util
import warnings
import xml.etree.ElementTree as ET
from pathlib import Path

import pytest

from diagrams_as_code.audit import audit_findings

REPO = Path(__file__).resolve().parent.parent
SCRIPTS = sorted((REPO / "examples" / "technical").glob("*.py"))

FIGURES = [
    "01_composition_enforcement",
    "02_control_loop",
    "03_transformer_block",
    "04_state_machine",
    "05_protocol_stack",
    "06_memory_layout",
    "07_timing_diagram",
    "08_pipeline_equations",
    "09_tensor_shapes",
    "10_geometric_construction",
    "11_constraint_region",
]


def _load(path: Path):
    spec = importlib.util.spec_from_file_location(f"_technical_{path.stem}", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_the_reference_figure_and_ten_more_are_present():
    assert [p.stem for p in SCRIPTS] == FIGURES


@pytest.mark.parametrize("script", SCRIPTS, ids=lambda p: p.stem)
def test_figure_builds_cleanly(script: Path, tmp_path: Path):
    module = _load(script)
    with warnings.catch_warnings():
        warnings.simplefilter("error")  # no layout warnings in a showcase
        diagram = module.diagram()
        svg_path = module.build_diagram(tmp_path)
    root = ET.fromstring(svg_path.read_text(encoding="utf-8"))
    assert root.tag.endswith("svg")
    assert not audit_findings(diagram), [str(f) for f in audit_findings(diagram)]
    assert diagram.theme.name == "paper"
    assert any(s.kind == "caption" for s in diagram.shapes), "a figure needs a caption"


@pytest.mark.parametrize("script", SCRIPTS, ids=lambda p: p.stem)
def test_committed_output_matches_the_script(script: Path):
    committed = REPO / "output" / "technical" / f"{script.stem}.svg"
    assert committed.exists(), f"run `uv run python {script.relative_to(REPO)}`"
    assert committed.read_text(encoding="utf-8") == _load(script).diagram().render_svg()


def _reference():
    return _load(REPO / "examples" / "technical" / "01_composition_enforcement.py").diagram()


def test_reference_figure_has_every_element_of_the_reference():
    """The checklist the reproduction is held to, element for element."""
    diagram = _reference()
    text = "\n".join((s.label or "") for s in diagram.shapes) + "\n".join(g.label for g in diagram.groups)
    flat = " ".join(text.split())
    for wanted in (
        # four layer bands
        "1. Strategic Governance Layer", "2. Enabling Substrate Layer",
        "3. Trajectory & Lineage Clipping Engine", "4. Endpoint Runtime & Execution Control",
        # governance
        "Intent Registry Specification", "Exact formal definition", "Registered Intent",
        "Red Thread Invariant (Verification)", "Verifiable Provenance Path",
        # substrate
        "Define the 6-tuple", "Super Permission Set", "Capabilities & Tool Primitives",
        "Execution Trajectory", "Dynamic Provenance", "Task Environment", "Allowed Task Topology",
        "(positive Capability Space)",
        # clipping engine
        "(Enforces Constraints)", "Clipping Plane", "Multi-dimensional boundary space",
        "Sinks and sources flow across boundary limits", "Inequality Clipping Constraints",
        "Evaluated Sequence vs. clipping planes", "Compositional Trajectory Evaluation",
        # runtime
        "Local Agent Runtime", "Agentic Runtime & Local Orchestrator", "Dispatched AI Agents / Swarms",
        "Proposed Transition", "2-way", "Policy Decision Function", "Compute safe execution space",
        "Approved Execution / Side Effects", "Deterministic Truncation",
        "FIGURE 1: Endpoint-Native Composition Enforcement Architecture for Agentic Trajectories",
    ):
        assert wanted in flat, wanted
    kinds = [s.kind for s in diagram.shapes]
    assert len(diagram.groups) == 4
    assert kinds.count("solid") == 2  # the cuboid and the clipped polyhedron
    assert kinds.count("bracket") == 1 and kinds.count("caption") == 1
    assert sum(1 for e in diagram.edges if e.arrow_head and e.arrow_tail) == 1
    assert sum(1 for e in diagram.edges if e.ellipsis) == 1
    assert sum(1 for e in diagram.edges if (e.width or 0) >= 3.0) == 6  # the spine and three trajectories


def test_reference_figure_corrects_the_slips_in_the_reference():
    diagram = _reference()
    labels = [" ".join((s.label or "").split()) for s in diagram.shapes]
    assert "Provenance / Taint Tracker" in labels
    assert not any("Tracking Tracker" in label for label in labels)
    # "Sinks and sources flow boundary limits" was used for two different things.
    assert sum("Sinks and sources flow" in label for label in labels) == 1
    # The invariant's formula closes every bracket it opens.
    formula = next(label for label in labels if "Red Thread" in label)
    assert formula.count("(") == formula.count(")")
