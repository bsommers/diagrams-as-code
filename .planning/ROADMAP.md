# Roadmap: Diagrams as Code

## Overview

Following the successful release of `v0.4.0` (auto-layout, CLI, modularity), this roadmap executes three sequential milestones: resolving immediate review edge cases and polish (Phase 1), formalizing typed constraint models and decoupled group flow engines (Phase 2), and implementing client-side interactive SVG pan/zoom and collapsible group toggles (Phase 3).

## Phases

- [x] **Phase 1: SDD Review Polish & Edge Robustness** - CLI error targeting, descendant traversal memoization, stable edge keying, and import cleanliness.
- [ ] **Phase 2: Architectural Follow-ups** - Typed constraint dataclasses and group flow layout engine extraction.
- [ ] **Phase 3: Interactive SVG Pan-Zoom & Collapsible Groups** - Optional inline JavaScript injection for responsive SVG manipulation.

## Phase Details

### Phase 1: SDD Review Polish & Edge Robustness
**Goal**: Address non-blocking minor debt and edge cases logged during the auto-layout/CLI review.  
**Depends on**: Nothing (first active phase).  
**Requirements**: POLISH-01, POLISH-02, POLISH-03, POLISH-04  
**Success Criteria**:
1. When `--out` points to an existing file when rendering, the CLI reports an explicit error attributing the issue to `--out` rather than failing during discovery and blaming the diagram script.
2. `_has_absolute_descendant()` in `layout/graph.py` computes descendant pin status without redundant $O(n \cdot \text{depth})$ tree re-traversals.
3. Pre-computed edge waypoints in `layout/pipeline.py` do not rely on transient `id(edge)` keys.
4. `tests/test_dependency_catalog.py` has no unused imports, and `diagram.py` imports are alphabetized.
5. All 431 existing tests continue to pass with zero regressions.
**Plans**: 1 plan

Plans:
- [x] 01-01: Implement CLI path checks, graph traversal memoization, edge waypoint attachment, and import cleanup.

### Phase 2: Architectural Follow-ups
**Goal**: Elevate model type-safety and decouple layout logic from container elements.  
**Depends on**: Phase 1  
**Requirements**: ARCH-01, ARCH-02  
**Success Criteria**:
1. Shape constraints are represented by typed dataclasses (`RelativeConstraint`, `AbsoluteConstraint`, `AlignConstraint`) with backwards-compatible coercion.
2. `Group.flow()` delegates placement algorithms to a pluggable layout engine class in `diagrams_as_code/layout/`.
3. All 88 domain diagrams render with 100% byte-identical SVG outputs.
**Plans**: 1 plan

Plans:
- [ ] 02-01: Introduce typed constraint dataclasses and extract group flow layout engine.

### Phase 3: Interactive SVG Pan-Zoom & Collapsible Groups (`CAP-DIAG-INTERACTIVE`)
**Goal**: Implement client-side interactive pan/zoom and collapsible groups via pure, zero-dependency inline JavaScript.  
**Depends on**: Phase 2  
**Requirements**: INTER-01, INTER-02, INTER-03  
**Success Criteria**:
1. `Diagram(interactive=True)` injects lightweight, zero-dependency SVG `<script>` and `<style>` blocks into rendered SVGs.
2. Users can pan via click-drag and zoom via scroll wheel within browser SVG viewports.
3. Clicking group headers toggles group collapse/expand state with reactive visibility changes.
4. Default rendering (`interactive=False`) remains 100% byte-identical and zero-script.
**Plans**: 1 plan

Plans:
- [ ] 03-01: Implement interactive SVG script generator, pan/zoom handlers, and collapsible group toggles.
