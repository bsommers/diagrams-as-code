# Domain expansion wave: review log (2026-11-23)

All 12 PRs below are open (4 new kits/features, 8 galleries). **Nothing is merged or tagged.** Merging, the version bump, and the docs/counts PR are waiting on your OK.
Live tracker: http://192.168.1.251:8790/ (`.planning/tracker/`, uncommitted). Research basis: `.planning/research/NEW-DOMAINS.md`.

## PRs
| PR | Branch | What | Base |
|---|---|---|---|
| #33 | feat/mcp-sandbox | MCP scripts run in a resource-limited child process | master |
| #34 | feat/math-binom-accents | `\binom`, accents, `\sqrt[n]` | #33 (stacked) |
| #39 | feat/gallery-chemistry | chemistry gallery + `\rightleftharpoons`, `\ce{}` | #34 (stacked) |
| #35 | feat/gallery-agentic-dev | 10 diagrams | master |
| #36 | feat/gallery-semiconductor | 10 diagrams | master |
| #37 | feat/sequence-diagram | SequenceDiagram kit + 3 examples | master |
| #38 | feat/gallery-data-engineering | 10 diagrams | master |
| #40 | feat/gallery-ml-models | 10 diagrams | master |
| #41 | feat/gallery-devops | 10 diagrams | master |
| #42 | feat/gallery-biology | 10 diagrams | master |
| #43 | feat/gallery-chemical-engineering | 10 diagrams | master |
| #44 | feat/gantt-timeline | Gantt/timeline primitive + 3 examples | master |

Merge order matters only for the stack: #33 -> #34 -> #39 (retarget each to master after its parent merges).

## What each piece did
- **MCP sandbox (#33):** `sandbox.py` runs each script in a child process: wall-clock kill of the process group, CPU/address-space rlimits (POSIX; memory only reliably enforced on Linux, untested here), stdin closed, stdout discarded, stderr capped, scrubbed env. Flags `--timeout`, `--memory-mb`. Not file/network isolation.
- **Math (#34):** `\binom`, `\hat \widehat \tilde \widetilde \dot \ddot \vec \grave`, `\sqrt[n]{}`. `\acute \check \breve` unsupported (no outlines).
- **Chemistry (#39):** `\rightleftharpoons`/`\rightleftarrows` (two stacked arrow glyphs, not harpoons), `\ce{}` helper; 10 figures with computed numbers (IAPWS phase diagram, titration curves, Maxwell-Boltzmann...).
- **agentic_dev (#35):** 5 Anthropic agent patterns + supervisor/swarm, planner-executor, agentic RAG, spec-driven loop, coding-agent harness. Skipped: eval/judge harness, OTel tracing, MCP sequence (now possible with #37).
- **semiconductor (#36):** RTL-to-GDSII, litho steps, CMOS/FinFET/GAA cross-sections, BEOL, damascene, wafer map (synthetic yield), CoWoS, chiplets, clock tree. Engine limits: no clipping to circle, hatch z-order, no taper primitive.
- **Sequence kit (#37):** layer 5.5 `sequence.py`; participants, messages, activations, notes, loop/alt/opt/par/critical/break; 32 tests; examples in `examples/sequence/`. Limits: horizontal messages only, no lost/found, no create/destroy, no `ref`.
- **data_engineering (#38):** dbt lineage, Airflow states, Kafka, stream windows, Lambda/Kappa, column lineage, data contract, backfill, exactly-once, ingestion-to-BI. Cut: data mesh, SCD2.
- **ml_models (#40):** decoder block, MHA, MoE, diffusion U-Net, PPO, RLHF/DPO, CNN FPN, VAE, LoRA, KV cache/speculative. Limits: no tensor helper; no `\mathcal`.
- **devops (#41):** GitOps, CI gates, commit graphs, canary/blue-green, K8s, ingress, OTel, SLO burn, incident timeline, Terraform. Cut: image supply chain.
- **biology (#42):** central dogma, ribosome, glycolysis/TCA, MAPK (bar-head inhibition), cells, phylogeny, food web, Punnett, PCR, population dynamics.
- **chemical_engineering (#43):** PFD, distillation, CSTR, HEN, mass balance, Haber loop, PID, pump curve, McCabe-Thiele, RTD. Symbols hand-drawn (no pump/valve icons exist).
- **Gantt (#44):** layer 5.5 `gantt.py`: `GanttChart` (deps with lag, phases, milestones, % done, today line, computed critical path, orthogonal arrows) and `Timeline` (non-colliding label stacking); 3 examples in `examples/project_management/`. Limits: calendar days, finish-to-start only, ~0.5% of arrows on dense random charts unroutable (warned). #37 and #44 both edit docs/architecture.md and LAYERS: expect a trivial conflict on the second merge.

## Not done / decisions for you
1. **Docs + counts PR** (README, docs/CAPABILITIES.md, capabilities.json, examples/README.md, CHANGELOG, user-guide mentions, test_domain_examples EXPECTED_DOMAINS): deliberately deferred. Every gallery PR adds files only, so the PRs merge without conflicts; a single docs PR after merging avoids count conflicts. The sequence agent already edited docs/architecture.md (247 -> 250), so the docs PR must reconcile the final total (about 307 scripts).
2. **Merge and release:** which PRs to merge, and whether to cut v0.19.0. Not authorized yet.
3. **Icons:** none of the proposed icon sets were built (galleries use existing icons or drawn primitives). Say if you want per-domain icon sets.
4. **electronics** and **org** galleries not started (research ranked them lowest; org folds into project_management).
5. **project_management gallery** (10 diagrams: roadmap, kanban, risk matrix, RACI, value-stream, PERT, org...) can now start; Gantt primitive is in PR #44 with 3 of its examples.
6. Test coverage: several new domains are not in `EXPECTED_DOMAINS` / DOMAINS lists, so pytest does not enforce "committed SVG matches script" for them (chemistry was added).
7. Not on GitHub's CI: all gates were run locally per CLAUDE.md.
8. Tracker exposed on the LAN (192.168.x.x only) and can read repo files; stop with `kill $(lsof -ti :8790)`.
