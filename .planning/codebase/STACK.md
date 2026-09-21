---
last_mapped_commit: aa12f844a5d25922af7be204ce6e5ef29d89db57
---

# Technology Stack

**Analysis Date:** 2026-09-19

## Languages

**Primary:**
- Python 3.11+ - All diagram scripts, utilities, asset palettes, and test files (`*.py`)

**Secondary:**
- Shell (Bash) - Container build and execution scripts (`docker-build-n-run.sh`)
- YAML - Icon metadata and Docker Compose definitions (`icons/icons.yaml`, `docker-compose.yml`)
- CSV - Tabular icon mappings (`icons/icons.csv`)

## Runtime

**Environment:**
- Python 3.10+ runtime (`ghcr.io/astral-sh/uv:python3.12-bookworm-slim` in container)
- Zero external binary dependencies (no Graphviz, Cairo, or ImageMagick required)

**Package Manager & Execution Tool:**
- `uv` (Astral) managing virtual environment (`.venv/`), lockfile (`uv.lock`), and execution (`uv run`)
- PEP 517 build backend via `hatchling` declared in `pyproject.toml`

## Frameworks

**Core:**
- `diagrams` (mingrammer/diagrams) - Diagram-as-code rendering library wrapping Graphviz DOT

**Supporting Libraries:**
- `pyyaml` - Parsing and serializing icon definitions (`icons/icons.yaml`)
- `gitpython` - Git repository automation for committing and pushing diagrams (`Repo`)
- `boto3` - AWS SDK for uploading generated diagram SVG/PNG and documentation to S3

**Testing:**
- Test suite runner: `uv run pytest` configured via `pyproject.toml`
- 139 automated tests in `tests/` covering geometry, constraints, routing, SVG rendering, and BOM.

**Build/Dev:**
- `uv` - Dependency resolution, environment virtualization, and execution runner
- Docker (`Dockerfile`) - Multi-stage container packaging Astral `uv:python3.12-bookworm-slim`
- Docker Compose (`docker-compose.yml`) - Container orchestration mounting output volume

## Key Dependencies

**Critical:**
- `diagrams`: Core diagram generation engine producing Graphviz DOT representations
- `pyyaml`: Configuration serialization for icon catalogs
- `gitpython`: Version control integration to push rendered assets directly to Git origins
- `boto3`: Cloud artifact publication to Amazon S3 buckets

**System Dependencies:**
- `graphviz`: Underlying layout engine required by `diagrams` library
- `libgraphviz-dev`: Development headers for Graphviz compilation
- `git`: Required by GitPython runtime

## Configuration

**Application Config:**
- `icons/icons.yaml` - Structured YAML icon mapping dictionary with symbol, path, and technical notes
- `icons/icons.csv` - Comma-delimited fallback icon definitions

**Environment Variables:**
- `AWS_ACCESS_KEY_ID`: AWS authentication for S3 asset publication
- `AWS_SECRET_ACCESS_KEY`: AWS secret key for S3 asset publication
