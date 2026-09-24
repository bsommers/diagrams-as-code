# Requirements: Milestone v0.7.0 (Smart Routing & Layout Optimization)

**Defined:** 2026-09-23  
**Target Release:** `v0.7.0`  
**Core Value:** Zero external binary dependencies producing deterministic, publication-grade architecture diagrams from clean Python code.

## Active Requirements

### Phase 7: Edge Routing & Orthogonal Waypoint Enhancements (`CAP-DIAG-ROUTER-AVOIDANCE`)

- [x] **ROUTE-01**: Segment-box collision test function in `router.py` detecting overlap between orthogonal line segments and expanded obstacle rectangles.
- [x] **ROUTE-02**: Obstacle-avoidance routing algorithm in `OrthogonalRouter.route()` that computes non-intersecting Manhattan paths around intermediate nodes.
- [x] **ROUTE-03**: Backward compatibility guarantee: default routing without obstacles produces exact identical waypoints for existing tests.
- [x] **ROUTE-04**: Multi-rank crossing minimization in `LayeredLayout` barycenter ordering.
- [x] **ROUTE-05**: Full verification across all tests, zero diff in `output/`, and 100% downward architecture boundary compliance.

## Traceability

| Requirement | Phase | Status |
|---|---|:---:|
| ROUTE-01 | Phase 7 (Routing & Layout) | Passed |
| ROUTE-02 | Phase 7 (Routing & Layout) | Passed |
| ROUTE-03 | Phase 7 (Routing & Layout) | Passed |
| ROUTE-04 | Phase 7 (Routing & Layout) | Passed |
| ROUTE-05 | Phase 7 (Routing & Layout) | Passed |

## Archived Milestones

- [v0.6.0 Requirements Archive](milestones/v0.6.0-REQUIREMENTS.md)
- [v0.5.0 Requirements Archive](milestones/v0.5.0-REQUIREMENTS.md)
