---
last_mapped_commit: aa12f844a5d25922af7be204ce6e5ef29d89db57
---

# Testing Patterns

**Analysis Date:** 2026-09-19

## Test Framework

**Current State:**
- Ad-hoc procedural test scripts:
  - `test_bom.py`: Attempts to instantiate `IIoTPalette` and print BOM to console
  - `test_docs_bom.py`: Instantiates `IIoTPalette`, builds a small diagram, and runs `generate_readme()`
- No formal test runner configuration or CI test harness currently present in root

**Target Framework:**
- `pytest` (executed via `uv run pytest`)
- Standard `assert` statements for geometry, constraint solving, and SVG structure validation
- Configuration declared in `pyproject.toml` (`testpaths = ["tests"]`, `pythonpath = ["src"]`)

**Run Commands:**
```bash
# Provision environment
uv sync

# Run complete test suite
uv run pytest

# Run individual test modules
uv run pytest tests/test_geometry.py
uv run pytest tests/test_routing.py
```

## Test File Organization

**Location:**
- Legacy test files reside in repository root (`test_bom.py`, `test_docs_bom.py`)
- Target location for structured tests: `tests/` directory (`tests/test_*.py`)

**Naming:**
- Files: `test_<module_name>.py`
- Functions: `test_<behavior_under_test>()`

## Current Test Deficiencies & Gaps

1. **Defective Method Call:**
   - `test_bom.py` line 14 calls `palette.print_bom()`, but `IIoTPalette` in `iiot_theme.py` only implements `generate_readme()`. Running `python test_bom.py` results in `AttributeError: 'IIoTPalette' object has no attribute 'print_bom'`.

2. **No Visual / Golden File Regression Testing:**
   - Diagrams are output as raw SVG/PNG without automated visual comparison or SVG structural XML parsing.

3. **No Mocks for External Services:**
   - `push_to_github()` and `upload_to_s3()` in `iiot_theme.py` call live `Repo` and `boto3.client('s3')` without test fixtures or mocks.

4. **Missing Unit Tests:**
   - No automated tests for icon bootstrap fallbacks, CSV/YAML parsing edge cases, or missing file paths.
