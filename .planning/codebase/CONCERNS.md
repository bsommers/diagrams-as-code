---
last_mapped_commit: 24c06772a5a54fc91d84877ee767ee933a39e761
---

# Technical Concerns & Architecture Backlog

**Analysis Date:** 2026-09-22 (v0.4.0)

## Architectural Debt & Refactoring Opportunities

1. **Untyped Constraint Dictionaries (`elements.py`, `constraints.py`):**
   - Current state: Constraints are stored as untyped Python dictionaries (`{"type": "right_of", "target": other, "margin": 40}`).
   - Improvement: Replace with typed dataclasses (`RelativeConstraint`, `AbsoluteConstraint`, `AlignConstraint`) to ensure static analysis and type safety.

2. **Group Flow Engine Extraction (`groups.py`, `layout/`):**
   - Current state: `Group.flow()` embeds flow algorithms directly inside the group model.
   - Improvement: Extract flow placement algorithms into pluggable layout engines under `diagrams_as_code/layout/`.

3. **Subtree Descendant Walk Performance (`layout/graph.py`):**
   - Current state: `_has_absolute_descendant()` re-walks descendant subtrees per group, resulting in $O(n \cdot \text{depth})$ traversal.
   - Improvement: Memoize or precompute descendant pin states during bottom-up scope traversal.

4. **Edge Routing Map Identity Keying (`layout/pipeline.py`):**
   - Current state: Pre-computed edge waypoints are mapped via `id(edge)`.
   - Improvement: Use stable edge keys or assign waypoints directly to the `Edge` dataclass.

## CLI & Error Handling Polish

1. **CLI `--out` Blame Target (`cli.py`):**
   - Current state: If `--out` points to an existing file when rendering, the error message blames the diagram script rather than `--out`.
   - Improvement: Validate `--out` path type before running diagram discovery.

2. **Import Cleanliness (`diagram.py`, `tests/test_dependency_catalog.py`):**
   - Unused `Diagram` import in `tests/test_dependency_catalog.py`.
   - Non-alphabetized `context` import in `diagram.py`.

## Planned Future Capabilities

1. **`CAP-DIAG-INTERACTIVE` (Interactive SVG Pan/Zoom & Collapsible Groups):**
   - Client-side lightweight JavaScript injection into SVG output for interactive pan, zoom, and collapsible group toggling.
