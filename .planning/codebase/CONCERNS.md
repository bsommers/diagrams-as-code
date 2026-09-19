---
last_mapped_commit: aa12f844a5d25922af7be204ce6e5ef29d89db57
---

# Codebase Concerns

**Analysis Date:** 2026-09-19

## Tech Debt

**Architecture Sprawl & Code Duplication:**
- Issue: Multiple orphaned variations of theme files and scripts exist in root (`old_iiot_theme.py`, `old2_iiot_theme.py`, `old3_iiot_theme.py`, `iiot_theme-2.py`, `enhanced_iiot_themed_main.py`, `old_main.py`).
- Why: Rapid prototyping without cleanup or package modularization.
- Impact: Confuses developers on which module is the authoritative implementation; updates to `iiot_theme.py` are not reflected in older scripts.
- Fix approach: Consolidate all palette, theme, and diagram logic into a formal Python package (`src/iiot_diagrams/`).

**Missing Local Image Assets:**
- Issue: Code references PNG files (`./icons/iiot-edge.png`, `./icons/iiot-broker.png`, `./iiot_logo.png`, `./icons/default.png`) that do not exist on disk.
- Why: The assets were either gitignored or not checked in during initial project export.
- Impact: Diagrams rendered via `diagrams.custom.Custom` will show broken image placeholders or error out depending on the Graphviz output target.
- Fix approach: Implement pure-Python vector shape primitives and SVG icon embedding rather than relying on external local image files.

**Fundamental Placement Limitations of Graphviz DOT:**
- Issue: Existing scripts rely on `diagrams` (which invokes Graphviz `dot`), which prevents directed or constraint-based placement.
- Why: Graphviz `dot` uses hierarchical Sugiyama ranking and ignores absolute `(x, y)` coordinates or shape-to-shape relative margins.
- Impact: Complex multi-column layouts like `mock-up.txt` or precise slide layouts (`diagram-architecture-slide.py`) cannot be rendered reliably.
- Fix approach: Implement a native constraint solver and SVG renderer supporting directed coordinate systems and flow placement.

## Known Bugs

**Missing `print_bom()` Method in `IIoTPalette`:**
- Symptoms: Running `python test_bom.py` crashes with `AttributeError: 'IIoTPalette' object has no attribute 'print_bom'`.
- Trigger: Executing `test_bom.py`.
- Root cause: `print_bom()` was present in an earlier draft or different version of the script but was omitted from `iiot_theme.py`.
- Fix approach: Add `print_bom()` to `IIoTPalette` or transition to the new `BOMGenerator` class.

**Unpinned Requirements:**
- Symptoms: Inconsistent builds across environments.
- Trigger: Running `pip install -r requirements.txt`.
- Root cause: `requirements.txt` contains unpinned package names (`diagrams`, `pyyaml`, `gitpython`, `boto3`).
- Fix approach: Pin exact versions and use a lockfile or `pip-tools`.

## Security Considerations

**Automated Git Push:**
- Risk: `IIoTPalette.push_to_github()` runs `repo.git.add(all=True)` and pushes directly to `origin`.
- Impact: Risk of accidentally staging and committing secrets, environment files, or untracked temporary files to public repositories.
- Mitigation: Require explicit file staging and sanitize outputs before commit.

**AWS Credentials Exposure:**
- Risk: `docker_compose.yml` mounts AWS environment variables directly into the container.
- Impact: If container logs or environment dumps are captured, credentials could leak.
- Mitigation: Use AWS IAM roles or secrets manager when running in production pipelines.

## Fragile Areas

**Graphviz Cluster Inter-Edges:**
- In `diagram-architecture-slide.py` and `diagram-iiot-high-availability.py`, edges connecting nodes across different `Cluster` blocks cause Graphviz to warp the rank order of internal nodes, frequently resulting in inverted layouts and overlapping connectors.
