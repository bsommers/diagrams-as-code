---
last_mapped_commit: 24c06772a5a54fc91d84877ee767ee933a39e761
---

# External Integrations & Tooling

**Analysis Date:** 2026-09-22 (v0.4.0)

## Runtime & Service Integrations

- **Cloud / Network Services:** None. The framework operates 100% offline and air-gapped without remote API calls, telemetry, or network dependencies.
- **Operating Systems:** Linux, macOS, Windows supported via pure Python standard library.

## Optional Rasterization Backends

For converting vector SVG diagrams to PNG bitmaps, `rasterize.py` attempts backends in this deterministic order:
1. `resvg` (via `resvg-py` dev dependency) - Recommended fast Rust-based renderer.
2. `cairosvg` - Python Cairo wrapper (if installed system-wide).
3. `inkscape` - Command-line binary (`inkscape --export-filename=...`).
4. `magick` / `convert` - ImageMagick CLI.

If no rasterizer is present, SVG output is still generated cleanly, while PNG rendering raises an instructive `RuntimeError` advising installation.

## Container & CI Tooling

- **Container Image:** `ghcr.io/astral-sh/uv:python3.12-bookworm-slim` packaging `fonts-dejavu-core` to guarantee consistent typography rendering across host platforms.
- **Docker Compose:** `docker-compose.yml` mounts local `output/` into `/app/output`.
- **CI / CD Workflows:** GitHub Actions matrix running:
  - Python 3.10, 3.11, 3.12, 3.13 unit tests.
  - Docker container build and example execution.
  - Post-execution diff gate on `output/`, `icons/`, `docs/`, `README.md`.
