# Plan: medical, engineering and CAD textbook figures (v0.16.0)

Follows the plot kit (v0.15.0). Goal: textbook-quality medical, engineering-drawing and CAD figures.

## Engine: `src/diagrams_as_code/draft.py` (layer 5.5, beside `plot`)
`Draft(diagram)` in canvas pixels: `outline`, `smooth_closed/open` (Catmull-Rom organic outlines),
`centerline`, `hidden_line`, `hatch` (even-odd section lining, holes), `dimension` (extension lines,
arrows, text; arrows flip outside when short), `radius_dim` (R / diameter), `section_arrows`,
`gdt_frame`, `leader`, `wave` plus `ecg_beat`. Tests: `tests/test_draft.py`.

## Galleries (10 figures each, `paper` theme, `**Figure N:**` caption)
- `examples/medical/`: anatomy outlines, cardiac cycle and ECG, Wiggers-style pressure traces,
  pharmacokinetics (`Plot`, log axis), dose-response, nephron/neuron, epidemic curve, SIR, cell cycle, Bohr-style gas exchange.
- `examples/engineering/`: dimensioned part with section and hatching, GD&T, beam shear/moment,
  truss, stress-strain, Mohr circle, gear train, P-V/T-S cycles, control block, bode.
- `examples/cad/`: orthographic third-angle views, isometric solids, exploded assembly,
  fits and tolerances, thread detail, sketch constraints, fillet/chamfer, revolve/extrude/sweep, BOM balloons.

## Process
Sonnet agents author one gallery each (own `examples/<domain>/` and `output/<domain>/` only, no commits,
no shared files). Orchestrator adds `tests/test_clinical_engineering_examples.py`, docs, runs the gate.
No push, PR or release without the user's OK.
