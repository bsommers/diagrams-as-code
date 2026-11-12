"""The gallery's visual defect counts may only go down (see tools/audit_gallery.py)."""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

from diagrams_as_code import Diagram, Shape
from diagrams_as_code.audit import DEFECTS, audit_diagram

REPO = Path(__file__).resolve().parent.parent


def _tool():
    spec = importlib.util.spec_from_file_location("audit_gallery", REPO / "tools" / "audit_gallery.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_gallery_defect_counts_do_not_exceed_baseline():
    total, _affected, per_script = _tool().run()
    baseline = json.loads((REPO / "tools" / "audit_baseline.json").read_text())
    assert set(baseline) == set(DEFECTS)
    worse = {n: (total[n], baseline[n]) for n in DEFECTS if total[n] > baseline[n]}
    assert not worse, f"visual defects rose above baseline (now, baseline): {worse}"
    assert len(per_script) >= 92


def test_routing_defects_stay_at_zero():
    total, _, _ = _tool().run()
    for name in ("edge_through_node", "edge_through_own_endpoint", "tangent_arrival", "node_overlap", "content_clipped"):
        assert total[name] == 0, name


def test_audit_detects_a_label_overflow_and_a_badge_over_a_node():
    with Diagram("t", theme="monochrome") as d:
        a = d.add(Shape("a", "An extremely long label that cannot fit in this box", width=80, height=30)).at(100, 100)
        b = d.add(Shape("b", "B")).at(200, 100)
        d.connect(a, b, label="a long protocol label")
    counts = audit_diagram(d)
    assert counts["label_overflow"] == 1
    assert counts["badge_over_node"] >= 1


def test_audit_is_clean_for_a_simple_diagram():
    with Diagram("t", theme="monochrome", width=520, height=260) as d:
        a = d.add(Shape("a", "A")).at(100, 100)
        b = d.add(Shape("b", "B")).at(340, 100)
        d.connect(a, b, label="ok")
    assert audit_diagram(d) == {}
