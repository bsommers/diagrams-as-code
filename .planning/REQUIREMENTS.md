# Requirements: Diagrams as Code

**Defined:** 2026-09-22  
**Core Value:** Zero external binary dependencies producing deterministic, publication-grade architecture diagrams from clean Python code.

## Active Requirements

### Phase 1: SDD Review Polish & Edge Robustness

- [x] **POLISH-01**: CLI `--out` validation: When `--out` path is an existing regular file when generating multiple outputs, report a clear error blaming `--out` rather than blaming the diagram script.
- [x] **POLISH-02**: Graph builder optimization: Memoize descendant pin state in `layout/graph.py` (`_has_absolute_descendant()`) during bottom-up traversal to eliminate repeated $O(n \cdot \text{depth})$ subtree walks.
- [x] **POLISH-03**: Edge identity keying: Replace `id(edge)` dictionary keying in `layout/pipeline.py` with stable edge identifiers or direct waypoint storage on `Edge` instances.
- [x] **POLISH-04**: Import cleanliness & ordering: Clean up unused `Diagram` import in `tests/test_dependency_catalog.py` and alphabetize imports in `diagram.py`.

### Phase 2: Architectural Follow-ups

- [x] **ARCH-01**: Typed constraint dataclasses: Replace untyped constraint dictionaries (`shape.constraints = [{"type": ...}]`) with typed dataclasses (`RelativeConstraint`, `AbsoluteConstraint`, `AlignConstraint`) with backward-compatible dict coercion.
- [x] **ARCH-02**: Group flow layout engine extraction: Decouple flow layout algorithms from `Group.flow()` into dedicated layout engine classes under `diagrams_as_code/layout/`.

### Phase 3: Interactive SVG Pan-Zoom & Collapsible Groups (`CAP-DIAG-INTERACTIVE`)

- [x] **INTER-01**: Interactive SVG enablement: Support `Diagram(interactive=True)` emitting zero-dependency inline SVG `<script>` and `<style>` blocks.
- [x] **INTER-02**: Pan & Zoom viewport controls: Mouse drag, scroll wheel zoom, and reset button integrated within SVG `viewBox`.
- [x] **INTER-03**: Collapsible groups: Interactive click toggles on hierarchical group headers to collapse/expand child nodes.

## Traceability

| Requirement | Phase | Status |
|---|---|:---:|
| POLISH-01 | Phase 1 (Polish) | Completed |
| POLISH-02 | Phase 1 (Polish) | Completed |
| POLISH-03 | Phase 1 (Polish) | Completed |
| POLISH-04 | Phase 1 (Polish) | Completed |
| ARCH-01 | Phase 2 (Architecture) | Completed |
| ARCH-02 | Phase 2 (Architecture) | Completed |
| INTER-01 | Phase 3 (Interactive) | Completed |
| INTER-02 | Phase 3 (Interactive) | Completed |
| INTER-03 | Phase 3 (Interactive) | Completed |
