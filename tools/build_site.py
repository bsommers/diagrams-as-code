#!/usr/bin/env python3
"""Regenerate the GitHub Pages data: ``docs/assets/site-data.json`` and ``docs/assets/gallery/``.

The landing page (``docs/index.html``) is static; every number and picture it shows
comes from this script, so it cannot drift from the repository.

    uv run python tools/build_site.py          # rewrite
    uv run python tools/build_site.py --check  # exit 1 if the committed files are stale
"""
from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from diagrams_as_code import __version__  # noqa: E402
from diagrams_as_code.shapes import ShapeLibrary  # noqa: E402
from diagrams_as_code.theme import list_themes  # noqa: E402

REPO = "https://github.com/bsommers/diagrams-as-code"
ASSETS = ROOT / "docs" / "assets"
GALLERY = ASSETS / "gallery"

#: Filter group -> domain -> picked example stems (one to three each).
PICKS: dict[str, dict[str, list[str]]] = {
    "AI & Software": {
        "agentic_dev": ["06_supervisor_vs_swarm", "10_coding_agent_harness"],
        "ml_models": ["02_multi_head_attention", "03_mixture_of_experts"],
        "ai": ["03_agentic_tool_orchestration"],
        "sequence": ["03_mcp_tool_call"],
        "devops": ["03_trunk_vs_gitflow_commit_graph", "07_observability_otel_stack"],
        "data_engineering": ["03_kafka_partitions_consumer_groups"],
        "computer_science": ["02_red_black_tree"],
    },
    "Cloud & Network": {
        "cloud": ["03_cdn_multi_region_edge"],
        "network_engineering": ["04_vxlan_evpn_datacenter_fabric"],
        "cybersecurity": ["03_zero_trust_ztna"],
        "datacenter": ["03_leaf_spine_clos_network"],
        "database": ["03_primary_replica_failover"],
    },
    "Industrial & Hardware": {
        "semiconductor": ["01_rtl_to_gdsii_flow", "08_cowos_s_package_stack"],
        "electronics": ["04_buck_converter", "10_pdn_impedance"],
        "iiot": ["01_baltimore_plant_to_cloud"],
        "chemical_engineering": ["02_distillation_column"],
        "cad": ["02_isometric_bracket"],
        "engineering": ["03_beam_shear_moment"],
    },
    "Science & Math": {
        "chemistry": ["05_water_phase_diagram", "06_sn2_mechanism"],
        "biology": ["03_glycolysis_tca"],
        "physics": ["04_thin_lens_rays"],
        "calculus_math": ["02_riemann_sums"],
        "differential_equations": ["08_lotka_volterra"],
        "medical": ["01_heart_chambers"],
    },
    "Business & Org": {
        "project_management": ["01_gantt_critical_path", "08_risk_matrix"],
        "org": ["03_team_topologies"],
        "enterprise_architecture": ["04_c4_container_view"],
        "business_process": ["01_order_to_cash"],
        "finance": ["01_candlestick_chart"],
    },
}


def _title(stem: str) -> str:
    return stem.split("_", 1)[1].replace("_", " ").capitalize()


def build() -> tuple[dict, dict[str, bytes]]:
    files: dict[str, bytes] = {}
    items = []
    for group, domains in PICKS.items():
        for domain, stems in domains.items():
            for stem in stems:
                src = ROOT / "examples" / domain / f"{stem}.svg"
                name = f"{domain}__{stem}.svg"
                files[name] = src.read_bytes()
                items.append({"group": group, "domain": domain, "title": _title(stem),
                              "image": f"assets/gallery/{name}",
                              "source": f"{REPO}/blob/master/examples/{domain}/{stem}.py"})
    scripts = sorted((ROOT / "examples").glob("*/*.py")) + sorted((ROOT / "examples").glob("*.py"))
    domains = {p.parent.name for p in (ROOT / "examples").glob("*/*.py")}
    data = {
        "version": __version__,
        "diagrams": len(scripts),
        "domains": len(domains),
        "themes": len(list_themes()),
        "icons": len(ShapeLibrary._ICON_CATALOG),
        "repo": REPO,
        "groups": list(PICKS),
        "gallery": items,
    }
    return data, files


def main(argv: list[str]) -> int:
    data, files = build()
    text = json.dumps(data, indent=1) + "\n"
    if "--check" in argv:
        stale = (ASSETS / "site-data.json").read_text() != text if (ASSETS / "site-data.json").exists() else True
        for name, blob in files.items():
            p = GALLERY / name
            stale = stale or not p.exists() or p.read_bytes() != blob
        extra = {p.name for p in GALLERY.glob("*.svg")} - set(files) if GALLERY.exists() else set()
        if stale or extra:
            print("docs/assets/site-data.json or gallery is stale: run tools/build_site.py")
            return 1
        print(f"site data up to date ({len(files)} gallery images)")
        return 0
    if GALLERY.exists():
        shutil.rmtree(GALLERY)
    GALLERY.mkdir(parents=True)
    for name, blob in files.items():
        (GALLERY / name).write_bytes(blob)
    (ASSETS / "site-data.json").write_text(text)
    print(f"wrote site-data.json and {len(files)} gallery images")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
