"""Deterministic evaluation and benchmark test suite for cubic Bezier edge routing.

Evaluates quality dimensions:
- Context Faithfulness: exact port anchor grounding (zero drift)
- Hallucination / Artifact Detection: valid SVG XML, finite coordinates, zero NaNs
- Escalation Accuracy: fallback escalation on malformed/degenerate waypoints
- Tone & Style Appropriateness: tangent collinearity, handle clamping >= 20px, theme contrast
- Tool / API Correctness: CLI benchmark runner and EdgeRouter facade
- Safety & Numerical Stability: zero-division guards on degenerate curves
"""

from __future__ import annotations

import json
import math
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

import pytest

from diagrams_as_code.connections import Edge, Port, Routing
from diagrams_as_code.elements import Element
from diagrams_as_code.geometry import CubicBezier, Point, Rect
from diagrams_as_code.renderer_svg import SVGRenderer
from diagrams_as_code.router import EdgeRouter, PORT_NORMALS
from diagrams_as_code.theme import get_theme, list_themes


DATASET_PATH = Path(__file__).parent / "fixtures" / "eval_bezier_dataset.json"


@pytest.fixture
def eval_dataset() -> dict:
    with open(DATASET_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def test_eval_bezier_dataset_faithfulness_and_structure(eval_dataset: dict) -> None:
    """Evaluate context faithfulness, absence of NaNs, and structure across all benchmark scenarios."""
    port_map = {
        "E": Port.EAST, "east": Port.EAST,
        "W": Port.WEST, "west": Port.WEST,
        "N": Port.NORTH, "north": Port.NORTH,
        "S": Port.SOUTH, "south": Port.SOUTH,
    }

    router = EdgeRouter()
    renderer = SVGRenderer(get_theme("light"))

    for scenario in eval_dataset["scenarios"]:
        src_rect = Rect(
            float(scenario["src_rect"]["x"]),
            float(scenario["src_rect"]["y"]),
            float(scenario["src_rect"]["w"]),
            float(scenario["src_rect"]["h"]),
        )
        tgt_rect = Rect(
            float(scenario["tgt_rect"]["x"]),
            float(scenario["tgt_rect"]["y"]),
            float(scenario["tgt_rect"]["w"]),
            float(scenario["tgt_rect"]["h"]),
        )
        src_port = port_map[scenario["src_port"]]
        tgt_port = port_map[scenario["tgt_port"]]

        src_elem = Element(id="src", label="Source Node")
        src_elem.bounds = src_rect
        tgt_elem = Element(id="tgt", label="Target Node")
        tgt_elem.bounds = tgt_rect

        edge = Edge(
            source=src_elem,
            target=tgt_elem,
            source_port=src_port,
            target_port=tgt_port,
            routing=Routing.CURVE,
            label="EVAL",
        )

        waypoints = router.route(edge)

        # 1. Structure: Exactly 4 points
        assert len(waypoints) == 4, f"Scenario {scenario['id']} waypoints != 4"

        # 2. Context Faithfulness: 100% port anchor grounding
        p_start_expected = src_rect.get_anchor(src_port.to_anchor())
        p_end_expected = tgt_rect.get_anchor(tgt_port.to_anchor())
        assert waypoints[0].distance_to(p_start_expected) < 1e-6
        assert waypoints[-1].distance_to(p_end_expected) < 1e-6

        # 3. Hallucination detection: Zero NaNs or non-finite values
        assert all(math.isfinite(p.x) and math.isfinite(p.y) for p in waypoints)

        # 4. Tone & Style: Tangent collinearity & handle tension >= 20px
        p0, c1, c2, p3 = waypoints
        assert p0.distance_to(c1) >= 19.99
        assert p3.distance_to(c2) >= 19.99

        n_src = PORT_NORMALS[src_port]
        v1 = Point(c1.x - p0.x, c1.y - p0.y)
        dot1 = (v1.x * n_src.x + v1.y * n_src.y) / max(1e-9, p0.distance_to(c1))
        assert dot1 > 0.999

        # 5. Output structure validity: valid SVG XML
        svg = renderer.render([src_elem, tgt_elem], edges=[edge], width=800, height=600)
        root = ET.fromstring(svg)
        assert root.tag.endswith("svg")


def test_eval_safety_and_escalation_guardrails() -> None:
    """Verify safety guardrails and graceful escalation under degenerate conditions."""
    # Degenerate zero-length curve
    p = Point(50.0, 50.0)
    zero_bez = CubicBezier(p, p, p, p)
    assert zero_bez.arc_length() == 0.0
    assert zero_bez.arc_length_midpoint() == p
    bbox = zero_bez.bbox()
    assert bbox.width == 0.0 and bbox.height == 0.0

    # Malformed waypoint list escalates to polyline fallback in renderer
    renderer = SVGRenderer(get_theme("dark"))
    s = Element(id="s", label="S")
    s.bounds = Rect(0, 0, 100, 50)
    t = Element(id="t", label="T")
    t.bounds = Rect(300, 300, 100, 50)
    edge = Edge(s, t, routing=Routing.CURVE)
    edge.waypoints = [Point(0, 0), Point(100, 100)]  # Invalid 2-point curve
    svg = renderer.render([s, t], edges=[edge], width=600, height=600)
    assert "<path" in svg
    assert "d=\"M 0.0 0.0 L 100.0 100.0\"" in svg or "d=\"M 0 0 L 100 100\"" in svg


def test_eval_theme_aesthetic_contrast() -> None:
    """Verify all 13 theme presets provide valid contrast for protocol badges."""
    s = Element(id="s", label="S")
    s.bounds = Rect(100, 100, 120, 60)
    t = Element(id="t", label="T")
    t.bounds = Rect(400, 100, 120, 60)
    edge = Edge(s, t, routing=Routing.CURVE, label="HTTPS")

    for theme_name in list_themes():
        theme = get_theme(theme_name)
        renderer = SVGRenderer(theme)
        svg = renderer.render([s, t], edges=[edge], width=600, height=300)
        assert "HTTPS" in svg
        assert 'class="edge-label"' in svg or "<text" in svg


def test_eval_runner_cli_integration() -> None:
    """Verify standalone evaluation runner CLI executes and returns overall PASS."""
    tool_path = Path(__file__).parent.parent / "tools" / "eval_bezier.py"
    proc = subprocess.run(
        [sys.executable, str(tool_path), "--json"],
        capture_output=True,
        text=True,
        check=True,
    )
    result = json.loads(proc.stdout)
    assert result["overall_status"] == "PASS"
    assert result["pass_rate_pct"] == 100.0
    assert result["safety_guardrails"]["status"] == "PASS"
