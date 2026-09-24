# Roadmap: Milestone v0.6.0 (CLI Interactive & Rich Viewport Controls)

## Milestone History

- **[v0.5.0 Milestone](milestones/v0.5.0-ROADMAP.md)** — Shipped 2026-09-23: Phase 1 (Polish & Edge Robustness), Phase 2 (Typed Constraints & Group Flow Decoupling), Phase 3 (Interactive SVG Pan-Zoom & Collapsible Groups).
- **[v0.4.0 Milestone](milestones/v0.5.0-ROADMAP.md)** — Shipped 2026-09-22: Auto-layout, JSON layout files, CLI, modularity refactoring, unconditional canvas growth.

## Overview

Milestone `v0.6.0` extends the standalone CLI and client-side interactive SVG rendering capabilities with three sequential phases:
1. Phase 4 exposes `--interactive` on the CLI to allow batch generation of interactive diagrams without code edits.
2. Phase 5 adds inline HUD search filtering to quickly highlight nodes and inspect complex architectures.
3. Phase 6 introduces an interactive minimap overview thumbnail for navigating large topologies.

## Phases

- [x] **Phase 4: CLI `--interactive` Option (`CAP-DIAG-CLI-INTERACTIVE`)** - Add `--interactive` flag to `diagrams-as-code render` for single-script and batch exports.
- [x] **Phase 5: Client-Side Search & Node Highlight (`CAP-DIAG-SEARCH`)** - Add HUD search filter with dynamic node matching and opacity dimming.
- [x] **Phase 6: Viewport Minimap Navigator (`CAP-DIAG-NAVIGATOR`)** - Add interactive overview thumbnail widget for large diagrams.

## Phase Details

### Phase 4: CLI `--interactive` Option (`CAP-DIAG-CLI-INTERACTIVE`)
**Goal**: Allow users to batch-generate interactive SVG diagrams directly from the CLI.  
**Depends on**: Milestone v0.5.0  
**Requirements**: CLI-INTER-01, CLI-INTER-02, CLI-INTER-03, CLI-INTER-04  
**Success Criteria**:
1. `diagrams-as-code render <path> --interactive` outputs SVG files with interactive pan/zoom and collapsible groups enabled.
2. Batch rendering whole directories (e.g. `diagrams-as-code render examples/ --interactive --out output/`) applies interactive mode across all discovered scripts.
3. Default rendering without `--interactive` produces 100% byte-identical, script-free outputs.
4. Comprehensive test coverage in `tests/test_cli.py`.
**Plans**: 1 plan
- [x] 04-01: Add `--interactive` flag to `cli.py`, pass through `_configure()`, and add CLI integration tests.

### Phase 5: Client-Side Search & Node Highlight (`CAP-DIAG-SEARCH`)
**Goal**: Enable fast visual search and filtering inside interactive SVGs.  
**Depends on**: Phase 4  
**Requirements**: SEARCH-01, SEARCH-02, SEARCH-03  
**Success Criteria**:
1. Search input in HUD controls accepts query strings.
2. Matching elements are highlighted while non-matching elements and edges are dimmed.
3. Clearing the input or pressing Escape restores normal visibility.
**Plans**: 1 plan
- [x] 05-01: Implement search input widget in HUD and client-side filtering script in `renderer_svg.py`.

### Phase 6: Viewport Minimap Navigator (`CAP-DIAG-NAVIGATOR`)
**Goal**: Provide bird's-eye navigation for large diagrams.  
**Depends on**: Phase 5  
**Requirements**: MINIMAP-01, MINIMAP-02, MINIMAP-03  
**Success Criteria**:
1. Pinned minimap thumbnail renders scaled overview of all elements.
2. Viewport indicator rect reflects visible bounds and updates during pan/zoom.
3. Clicking/dragging on minimap navigates the main diagram viewport.
**Plans**: 1 plan
- [x] 06-01: Implement minimap thumbnail and interactive drag navigation.
