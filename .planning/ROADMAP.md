# Roadmap: Milestone v0.7.0 (Smart Routing & Layout Optimization)

## Milestone History

- **[v0.6.0 Milestone](milestones/v0.6.0-ROADMAP.md)** — Shipped 2026-09-23: Phase 4 (CLI `--interactive` flag), Phase 5 (Client-side Search & Highlight), Phase 6 (Viewport Minimap Navigator).
- **[v0.5.0 Milestone](milestones/v0.5.0-ROADMAP.md)** — Shipped 2026-09-23: Phase 1 (Polish & Edge Robustness), Phase 2 (Typed Constraints & Group Flow Decoupling), Phase 3 (Interactive SVG Pan-Zoom & Collapsible Groups).
- **[v0.4.0 Milestone](milestones/v0.5.0-ROADMAP.md)** — Shipped 2026-09-22: Auto-layout, JSON layout files, CLI, modularity refactoring, unconditional canvas growth.

## Overview

Milestone `v0.7.0` focuses on intelligent routing and layout optimization:
1. Phase 7 implements obstacle-aware orthogonal edge routing in `router.py` and multi-rank crossing minimization in `layout/layered.py`.

## Phases

- [x] **Phase 7: Edge Routing & Orthogonal Waypoint Enhancements (`CAP-DIAG-ROUTER-AVOIDANCE`)** - Obstacle-aware orthogonal Manhattan routing, collision detection, and multi-rank crossing reduction.

## Phase Details

### Phase 7: Edge Routing & Orthogonal Waypoint Enhancements (`CAP-DIAG-ROUTER-AVOIDANCE`)
**Goal**: Prevent edges from crossing over intermediate node obstacles and minimize multi-rank edge crossings.  
**Depends on**: Milestone v0.6.0  
**Requirements**: ROUTE-01, ROUTE-02, ROUTE-03, ROUTE-04, ROUTE-05  
**Success Criteria**:
1. `OrthogonalRouter.route()` routes around intermediate obstacles using clean orthogonal detours when obstacles are present.
2. Fast-path collision check preserves 100% byte-invariance and zero regression when paths are clear.
3. `LayeredLayout` barycenter sweep accounts for multi-rank edges spanning $\ge 2$ ranks.
4. Comprehensive test coverage for collision detection, detour routing, and multi-rank crossings.
5. All 453 tests pass.
**Plans**: 1 plan
- [x] 07-01: Implement obstacle avoidance in `router.py`, multi-rank sweeps in `layered.py`, wire pipeline, and verify.
