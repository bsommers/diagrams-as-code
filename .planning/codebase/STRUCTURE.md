---
last_mapped_commit: aa12f844a5d25922af7be204ce6e5ef29d89db57
---

# Codebase Structure

**Analysis Date:** 2026-09-19

## Directory Layout

```
.
├── .planning/                          # Planning and codebase intelligence
│   └── codebase/                       # Architectural documentation maps
├── docs/                               # Documentation and specifications
│   └── superpowers/
│       └── plans/                      # Detailed implementation plans
├── icons/                              # Node icon catalogs and metadata
│   ├── icons.csv                       # Tabular icon symbol-path definitions
│   └── icons.yaml                      # YAML icon symbol-path definitions
├── Dockerfile                          # Container environment specification
├── docker_compose.yml                  # Container execution configuration
├── docker-build-n-run.sh               # Container build and launch script
├── RUNNING.md                          # Operational instructions and guide
├── main.py                             # Primary entry point
├── iiot_theme.py                       # Canonical palette and theme implementation
├── themed_main.py                      # Themed reference execution
├── one-click-main.py                   # End-to-end rendering and publication pipeline
├── diagram-architecture-slide.py       # Architecture slide layout
├── diagram-iiot-high-availability.py   # High-availability cluster diagram
├── diagram-sparklplug.py               # Sparkplug B industrial IoT diagram
├── diagram-svg-out.py                  # Standalone SVG rendering script
├── diagrams-1.py                       # Baseline architecture variant 1
├── diagrams-2.py                       # Baseline architecture variant 2
├── diagrams-3.py                       # Baseline architecture variant 3
├── diagrams-hybrid-bridge.py           # Hybrid cloud bridge diagram
├── diagrams-logos.py                   # Logo integration test diagram
├── test_bom.py                         # BOM verification script
├── test_docs_bom.py                    # Documentation generator test script
├── mock-up.txt                         # Target ASCII layout specification
├── bom_out_samp.txt                    # Sample Bill of Materials output
├── Google Gemini.html                  # Historical context log
└── diagrams-chat.txt                   # Historical prompt transcript
```

## Directory Purposes

**`.planning/codebase/`:**
- Purpose: Living system architecture and code intelligence documentation
- Contains: `STACK.md`, `INTEGRATIONS.md`, `ARCHITECTURE.md`, `STRUCTURE.md`, `CONVENTIONS.md`, `TESTING.md`, `CONCERNS.md`

**`docs/superpowers/plans/`:**
- Purpose: Implementation specifications and roadmaps
- Contains: Bite-sized implementation plans following TDD practices

**`icons/`:**
- Purpose: Stores symbol catalogs for node mapping
- Contains: `icons.csv`, `icons.yaml`

## Key File Locations

**Entry Points:**
- `main.py`: Core execution script initializing palette
- `themed_main.py`: Example diagram generation showing industrial edge-to-cloud bridge
- `one-click-main.py`: Full workflow generating diagram, README, and triggering optional Git/S3 publication
- `docker-build-n-run.sh`: Automated Docker container execution script

**Theme & Palette Modules:**
- `iiot_theme.py`: Active theme definition and `IIoTPalette` class
- Legacy/Variant theme files: `enhanced_iiot_themed_main.py`, `iiot_theme-2.py`, `old_iiot_theme.py`, `old2_iiot_theme.py`, `old3_iiot_theme.py`

**Diagram Definitions:**
- `diagram-architecture-slide.py`: Multi-cluster layout with legend
- `diagram-iiot-high-availability.py`: High-availability cluster with load balancing and discovery lines
- `diagram-sparklplug.py`: Sparkplug B topic architecture
- `diagram-svg-out.py`: SVG output configuration

## Naming Conventions

- Python scripts: lowercase with hyphens (`diagram-*.py`) or underscores (`iiot_theme.py`, `main.py`)
- Theme constants: uppercase snake case (`IIOT_YELLOW`, `IIOT_BLACK`, `DARK_GREY`, `GLOBAL_ATTR`)
- Data files: lowercase with standard extensions (`.csv`, `.yaml`, `.txt`)
