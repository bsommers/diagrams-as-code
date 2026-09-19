---
last_mapped_commit: aa12f844a5d25922af7be204ce6e5ef29d89db57
---

# Architecture

**Analysis Date:** 2026-09-19

## Pattern Overview

**Overall:** Script-based Declarative Diagram Generation with Palette Helpers

**Key Characteristics:**
- Procedural Python scripts declaring Graphviz topologies using the `diagrams` library
- Decoupled icon catalog (`icons/icons.yaml`, `icons/icons.csv`) mapping symbolic names to image assets
- Stateful BOM (Bill of Materials) tracking during diagram construction
- Post-render lifecycle hooks for generating markdown documentation, Git commits, and AWS S3 uploads

## Layers

**1. Configuration & Asset Catalog (`icons/`):**
- Purpose: Provides source-of-truth metadata for architecture nodes (symbol keys, image paths, technical notes)
- Files: `icons/icons.yaml`, `icons/icons.csv`
- Used by: `IIoTPalette` in `iiot_theme.py`

**2. Palette & Theme Layer (`iiot_theme.py`):**
- Purpose: Encapsulates corporate styling (dark/gold colors), icon bootstrapping, node factory methods, and BOM tracking
- Key Class: `IIoTPalette`
- Depends on: `diagrams.custom.Custom`, `pyyaml`, `gitpython`, `boto3`
- Used by: All diagram definition scripts (`main.py`, `themed_main.py`, `one-click-main.py`)

**3. Diagram Definition Scripts (Root level):**
- Purpose: Declare architecture topologies (clusters, nodes, directed edges, protocols)
- Files:
  - `main.py` & `themed_main.py`: General edge-to-cloud topology
  - `diagram-architecture-slide.py`: Multi-cluster reference slide with legend and data flow
  - `diagram-iiot-high-availability.py`: Clustered high-availability broker architecture with load balancer
  - `diagram-sparklplug.py`: Sparkplug B topic namespaces and industrial sensor ingest
  - `diagram-svg-out.py`: Vector output rendering configuration
- Depends on: `diagrams` DSL and `iiot_theme.py`

**4. Publication & Documentation Generation:**
- Purpose: Extracts used symbols into `README.md` Bill of Materials and uploads assets
- Methods: `IIoTPalette.generate_readme()`, `IIoTPalette.push_to_github()`, `IIoTPalette.upload_to_s3()`

## Data Flow

**Execution Lifecycle:**
1. Script initializes `IIoTPalette(config_path)`: Bootstraps `icons/` folder and loads icon definitions.
2. Context manager opens `with Diagram(...)`: Configures canvas direction, background colors, and output format (`svg` or `png`).
3. Script creates nodes and clusters: Calls `palette.get_node(symbol, label)`, which returns a `Custom` node and registers the symbol in `used_symbols`.
4. Nodes connected with `>> Edge(...) >>`: Establishes directed graph relationships and protocol labels.
5. Exit context manager: `diagrams` compiles the AST to Graphviz DOT and invokes system `dot` binary to render graphic file.
6. Documentation hook: Calls `palette.generate_readme()`, outputting formatted Markdown BOM table referencing the generated image.

## Key Abstractions

- `IIoTPalette`: Icon registry, custom node factory, and BOM tracker.
- `Cluster`: Graphviz subgraph boundary grouping nodes logically (e.g., "Production Site", "Control Plane", "Cloud Platform").
- `Edge`: Connection abstraction defining line styling (`dashed`, `dotted`, `solid`), stroke colors, and protocol annotations.
