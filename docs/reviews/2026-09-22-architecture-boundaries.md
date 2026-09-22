# Architecture Review — Component Boundaries (2026-09-22)

**Scope:** boundaries between the input API, model, layout, routing, renderer, and I/O, reviewed while planning auto-layout and the CLI (`docs/superpowers/plans/2026-09-22-auto-layout-cli.md`).
**Verdict:** partly clean. `ConstraintSolver`, `OrthogonalRouter` and `Theme` are well isolated; `Diagram` is a god object, the renderer does layout work, and an import cycle hides behind a function-level import.

There is no text parser: diagrams are authored in Python through the fluent `Diagram` / `>>` API, which is the input layer.

| Component | Current state | Boundary problem | Recommendation | Status |
|---|---|---|---|---|
| Input API (`Diagram`, `_EdgeBuilder`, `_GroupContext`, `Element.__rshift__`) | Readable fluent DSL | `Element.>>` finds the active diagram via a function-level import of `diagram.py`: a hidden cycle | Active-diagram stack in a bottom-layer `context.py` | Plan Task 1 |
| `Diagram` (587 lines) | Central object | Registry + DSL + solve + framing + render + 4 PNG backends | Solve → `layout/pipeline.py`, PNG → `rasterize.py`, files → `output.py` | Plan Tasks 2, 5, 8 |
| Model (`Element`, `Shape`, `Group`) | Geometry plus constraints | Constraints are untyped dicts; `Group` holds flow layout algorithms | Typed constraint dataclasses; group flows as layout engines | **Deferred** (follow-up) |
| Layout (`ConstraintSolver`) | Clean imports | Layout logic spread across the solver, `Diagram.solve()` and `groups._apply_layout` | One ordered pipeline (`run_layout`) | Plan Task 8 |
| Routing (`OrthogonalRouter`) | Pure, small | Called by the renderer during drawing (`renderer_svg.py:165`) | Route in the layout stage; the renderer receives paths | Plan Task 9 (added) |
| Renderer (`SVGRenderer`) | Takes a theme and element lists, not `Diagram` | Owns label-below metrics (14px, `renderer_svg.py:296,315`) that layout must duplicate | Shared `metrics.py` read by both | Plan Task 7 (added) |
| Shapes / icons (1,009 lines) | Catalog is the single source of truth | 486-line glyph `if/elif` | `icon_glyphs.GLYPHS` table | Plan Task 3 |
| BOM (`BOMGenerator`) | Reads the model; imports `Diagram` for types only | — | — | OK |
| Theme | Frozen dataclass + registry | `Diagram.__init__` copies fields by hand for overrides | `dataclasses.replace` | Plan Task 4 |
| Output / I/O | 84 scripts write their own files | Building and writing are mixed | `diagram()` builds; `render_all` writes | Plan Task 5 |
| Enforcement | None | Layering can drift | Import-direction test (`tests/test_module_boundaries.py`) | Plan Task 1 |

## Decisions
- 2026-09-22: user approved adding route-in-layout and shared label metrics to the plan; typed constraints deferred to a follow-up.
