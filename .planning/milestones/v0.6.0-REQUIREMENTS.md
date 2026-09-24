# Requirements: Milestone v0.6.0 (CLI Interactive & Viewport Enhancements)

**Defined:** 2026-09-23  
**Target Release:** `v0.6.0`  
**Core Value:** Zero external binary dependencies producing deterministic, publication-grade architecture diagrams from clean Python code.

## Active Requirements

### Phase 4: CLI `--interactive` Option (`CAP-DIAG-CLI-INTERACTIVE`)

- [x] **CLI-INTER-01**: Add `--interactive` flag to `diagrams-as-code render` subcommand in `src/diagrams_as_code/cli.py`, forwarding `interactive=True` to `Diagram.configure()`.
- [x] **CLI-INTER-02**: Support batch directory rendering with `--interactive`, generating interactive SVG outputs for all discovered diagram scripts.
- [x] **CLI-INTER-03**: Verify default non-interactive behavior when `--interactive` is omitted (`interactive=False` retained).
- [x] **CLI-INTER-04**: Add unit and subprocess integration tests for CLI `--interactive` in `tests/test_cli.py`.

### Phase 5: Client-Side Search & Node Highlight (`CAP-DIAG-SEARCH`)

- [x] **SEARCH-01**: Inject lightweight search input field into the SVG interactive HUD controls.
- [x] **SEARCH-02**: Client-side filtering script: Typing in search input dynamically highlights matching node labels/IDs and dims non-matching nodes/edges.
- [x] **SEARCH-03**: Escape key or clearing input resets all node opacities.

### Phase 6: Viewport Minimap Navigator (`CAP-DIAG-NAVIGATOR`)

- [x] **MINIMAP-01**: Render a miniature overview thumbnail widget in the bottom corner of the interactive SVG canvas.
- [x] **MINIMAP-02**: Render a responsive viewport rectangle inside the minimap indicating the current visible diagram bounds.
- [x] **MINIMAP-03**: Support click and drag on the minimap viewport rectangle to smoothly navigate across large topologies.

## Traceability

| Requirement | Phase | Status |
|---|---|:---:|
| CLI-INTER-01 | Phase 4 (CLI Interactive) | Passed |
| CLI-INTER-02 | Phase 4 (CLI Interactive) | Passed |
| CLI-INTER-03 | Phase 4 (CLI Interactive) | Passed |
| CLI-INTER-04 | Phase 4 (CLI Interactive) | Passed |
| SEARCH-01 | Phase 5 (Search Highlight) | Passed |
| SEARCH-02 | Phase 5 (Search Highlight) | Passed |
| SEARCH-03 | Phase 5 (Search Highlight) | Passed |
| MINIMAP-01 | Phase 6 (Minimap) | Passed |
| MINIMAP-02 | Phase 6 (Minimap) | Passed |
| MINIMAP-03 | Phase 6 (Minimap) | Passed |
