---
last_mapped_commit: 24c06772a5a54fc91d84877ee767ee933a39e761
---

# Codebase Structure

**Analysis Date:** 2026-09-22 (v0.4.0)

## Repository Root Directory Tree

```
diagrams-as-code/
├── .planning/                  # GSD planning directory (codebase maps, roadmap, state)
├── .claude/                    # Checkpoint tracking and project rules
├── docs/                       # Architecture, running guide, how-tos, specs, changelog
│   ├── diagrams/               # Architecture diagrams (ASCII, Mermaid, Draw.io)
│   ├── superpowers/            # Specs and implementation plans
│   ├── reviews/                # Architecture reviews
│   ├── CAPABILITIES.md         # Living capability manifest (twin of capabilities.json)
│   ├── capabilities.json       # Machine-readable capability registry
│   └── CHANGELOG.md            # Master changelog (Keep a Changelog format)
├── examples/                   # Reference architecture topologies (88 total across 8 domains)
│   ├── ai/                     # 11 AI & LLM architectures
│   ├── business_process/       # 11 Enterprise workflows
│   ├── cloud/                  # 11 Cloud infrastructure & serverless
│   ├── computer/               # 11 Hardware & workstation peripherals
│   ├── cybersecurity/          # 11 SOC, SIEM, zero-trust topologies
│   ├── datacenter/             # 11 Bare-metal & power topologies
│   ├── iiot/                   # 11 Industrial IoT & edge architectures
│   └── network_engineering/    # 11 Campus core, WAN, and routing
├── icons/                      # 60 built-in SVG vector icons categorized by domain
├── output/                     # Generated diagram SVGs, PNGs, and BOM markdown tables
├── src/
│   ├── diagrams_as_code/       # Canonical pure-Python engine
│   │   ├── layout/             # Layered layout engine, graph builder, pipeline, sidecar
│   │   │   ├── __init__.py     # Layout package exports
│   │   │   ├── base.py         # Protocol, dataclasses (LayoutNode, LayoutEdge, LayoutGraph)
│   │   │   ├── graph.py        # Scope graph extraction, edge lifting, pin detection
│   │   │   ├── layered.py      # Sugiyama layered placement algorithm
│   │   │   ├── pipeline.py     # Unified execution pipeline (run_layout)
│   │   │   └── sidecar.py      # Editable JSON layout file export/import
│   │   ├── __init__.py         # Public API re-exports and __version__
│   │   ├── __main__.py         # Module execution entry (python -m diagrams_as_code)
│   │   ├── bom.py              # Bill of Materials generator
│   │   ├── cli.py              # CLI argument parser and command dispatcher
│   │   ├── connections.py      # Edge definition and Port enums
│   │   ├── constraints.py      # DAG relative constraint solver
│   │   ├── context.py          # Active diagram context stack
│   │   ├── diagram.py          # Diagram fluent context manager
│   │   ├── elements.py         # Element and Shape base models
│   │   ├── geometry.py         # Immutable Point, Size, Rect, Anchor, UnitBasis
│   │   ├── groups.py           # Hierarchical Group container and auto-bounding
│   │   ├── icon_glyphs.py      # Pre-compiled icon SVG path table
│   │   ├── metrics.py          # Label and typography spatial metrics
│   │   ├── output.py           # File emission engine (render_all)
│   │   ├── rasterize.py        # Headless PNG rasterizer fallback chain
│   │   ├── renderer_svg.py     # Pure Python SVG XML generator
│   │   ├── router.py           # Orthogonal Manhattan router
│   │   ├── shapes.py           # ShapeLibrary and vector primitive renderers
│   │   └── theme.py            # Theme definitions and presets
│   └── iiot_diagrams/          # Backward-compatibility facade package
│       └── __init__.py         # Re-exports canonical symbols
├── tests/                      # 29 test suites (431 total tests)
├── tools/                      # Repository maintenance tools (generate_icons.py)
├── pyproject.toml              # Project configuration and packaging metadata
└── uv.lock                     # Deterministic dependency lockfile
```
