---
last_mapped_commit: 24c06772a5a54fc91d84877ee767ee933a39e761
---

# Code Conventions & Invariants

**Analysis Date:** 2026-09-22 (v0.4.0)

## Universal Tooling Rule: Always Use `uv`

- **Environment & Sync:** `uv sync`
- **Script Execution:** `uv run python <script.py>`
- **Test Execution:** `uv run pytest`
- **Dependencies:** `uv add --dev <package>` / `uv remove <package>`
- **Never:** Invoke bare `pip`, `python`, or `pytest` outside of `uv`.

## Architecture & Code Rules

1. **Zero External Runtime Dependencies:**
   - The core engine is 100% Python standard library.
   - `dependencies = []` in `pyproject.toml` remains strictly empty.
   - Optional rasterizers (`resvg-py`) are dev-dependencies only.

2. **Strict Layering & Import Direction:**
   - Evaluated by `tests/test_module_boundaries.py` using AST parsing.
   - Lower layers (`geometry`, `context`) cannot import higher layers (`elements`, `diagram`, `layout`).
   - Function-level imports are prohibited unless specifically allowlisted in the boundary test.

3. **Public API & Backward Compatibility:**
   - `diagrams_as_code` is canonical.
   - `iiot_diagrams` is an exact forwarding facade mirroring `diagrams_as_code.__all__`.
   - `tests/test_public_api.py` enforces symbol parity between both packages.

4. **Deterministic & Byte-Identical Output:**
   - SVG generation is deterministic across runs and platforms.
   - Output diff gate: `git diff --exit-code -- output/ icons/ README.md docs/`.
   - Engine changes must run the full test suite to regenerate `output/` before commit.

5. **Python Compatibility:**
   - Code must execute identically on Python 3.10, 3.11, 3.12, and 3.13.
   - Use `from __future__ import annotations` in all source files.
