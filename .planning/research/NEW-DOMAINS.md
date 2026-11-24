# New domain galleries: research (2026-11-23)

Method: four parallel Sonnet researchers, each with web search and a read of this repo's existing galleries. Evidence is mostly indirect (docs, tutorials, vendor pages); none found usage counts. Scores are judgments, 1-5. Source reports follow the synthesis.

## Answers to your questions
- **Physics:** exists (10 examples: free body, projectile, RLC, lenses, Snell, waves, beats, Carnot, dipole, hydrogen levels). Mechanics and thermo are covered thinly; no quantum/relativity/E&M beyond dipole.
- **AI:** exists (11 infra/MLOps examples, only 7 icons). Missing: model internals, agent design patterns, MCP, evals, AI-assisted SDLC, governance.
- **Chemistry:** none. **Semiconductors:** none (manufacturing has a wafer fab loop, litho cell, yield, backend assembly).

## Ranked shortlist
| # | Gallery | Demand | Fit | Differentiation | Effort | Prereq |
|---|---|---|---|---|---|---|
| 1 | agentic_dev (AI software design) | 5 | 4 | 5 | M | check/add sequence-diagram primitive |
| 2 | semiconductor | 4 | 3 | 5 | M-L | cross-section helper (layers, taper, hatch) |
| 3 | chemical_engineering (PFD) | 3 | 5 | 5 | M | dedupe icons vs iiot/engineering |
| 4 | data_engineering | 4 | 4 | 4 | M | small partition/time-axis helper |
| 5 | ml_models (AI architecture) | 4 | 3 | 4 | M-L | tensor-grid helper, xN brackets |
| 6 | chemistry | 4 | 3 | 4 | M | `\rightleftharpoons`, `\ce` helper (S) |
| 7 | devops | 5 | 4 | 3 | M | commit-graph helper |
| 8 | biology | 4 | 4 | 3 | M | T-bar edge ending |
| 9 | project_management | 5 | 2 now, 4 after | 4 | L | Gantt/time-axis primitive |
| 10 | electronics | 4 | 3 | 2-3 | M | symbol helper; don't clone schemdraw |
| 11 | org | 3 | 3 | 2 | M | fold into project_management |

## Cross-cutting engine work (unlocks several galleries)
1. Time-axis/Gantt primitive: project_management, devops incident timelines, data backfills.
2. Sequence diagram with lifelines: agentic_dev (MCP, tool calls), devops. Unverified whether it exists.
3. Cross-section layer helper: semiconductor, also chemistry apparatus.
4. Math: `\rightleftharpoons`, `\ce{}`: chemistry, biology.
5. Loop/back-edge routing, T-bar edge endings.

## Suggested sequencing
Wave 1: sequence primitive + agentic_dev; semiconductor. Wave 2: chemical_engineering, data_engineering. Wave 3: chemistry (with math pre-work), ml_models. Later: devops, biology, project_management (after Gantt).

## Overlaps to avoid
medical already has SIR, cell cycle, Michaelis-Menten, action potential; cloud/database already cover medallion and service mesh; mind_map has OKR and risk register; business_process has release gate and incident escalation.

---
# Source report: semi
# Semiconductor + Electronics gallery research

Caveat: ~7 web searches, no page fetches. Demand evidence is indirect (tool docs, tutorials, Commons files); no usage/star counts found. Engine knowledge is from CAPABILITIES.md and physics/03_series_rlc_circuit.py only; I did not read plot/draft/math source.

## 1. Demand evidence
- RTL-to-GDSII is a standard teaching/open-source flow. The OpenROAD-flow-scripts tutorial lists Yosys synthesis, floorplan, placement, CTS, global/detail route, fill, signoff, KLayout GDS, DRC/LVS: https://openroad-flow-scripts.readthedocs.io/en/latest/tutorials/FlowTutorial.html (also a MICRO 2022 tutorial deck on the-openroad-project.github.io). Every such course redraws this flow.
- Timing diagrams are an established niche: WaveDrom (Hackaday coverage https://hackaday.com/2015/05/25/need-timing-diagrams-try-wavedrom, ASCII-art follow-up https://hackaday.com/2022/04/04/turn-timing-diagrams-into-ascii-art-for-friendlier-pasting), schemdraw's TimingDiagram (https://schemdraw.readthedocs.io/en/latest/elements/timing.html), tikz-timing and a Typst package on CTAN/Typst Universe.
- Schematics: CircuiTikZ (CTAN recommendations https://ctan.org/recommendations/circuitikz), schemdraw (https://pypi.org/project/schemdraw), plus a comparison page https://dmccreary.github.io/signal-processing/circuits/schemadraw-vs-circuiTekz and a Julia forum thread asking for pure-Julia schematic drawing (https://discourse.julialang.org/t/draw-circuit-schematic-in-pure-julia/126592.md). Shows an ongoing "I want schematics from code in my language" demand.
- Packaging is hot: CoWoS-S/L/R, 2.5D vs 3D, interposer/TSV/HBM explainers (https://semiwiki.com/wikis/industry-wikis/cowos-chip-on-wafer-on-substrate-wiki, https://3dfabric.tsmc.com/english/dedicatedFoundry/technology/cowos.htm, TrendForce/TweakTown coverage). Most such figures are vendor art or screenshots, not reusable.
- Cross-sections: Wikimedia has hand-drawn Inkscape files (CMOS chip structure with FEOL/BEOL, CMOS inverter layout; translatable). USPTO patents are full of GAA/FinFET process-step figure series (patents 9224812, 10868127 etc.). So these are drawn by hand in Inkscape/PowerPoint with no code workflow.
- Communities (inferred, not measured): EE/VLSI students and instructors, open-silicon/Tiny Tapeout/OpenROAD users, hardware engineers writing design docs and papers (LaTeX), analysts/journalists on packaging, makers/KiCad users.

## 2. Competitors and gaps
- schemdraw (Python, matplotlib): circuit symbols, logic gates, K-maps, WaveJSON timing. Strong; no semiconductor/process content. We should not out-schemdraw it on general circuit symbols.
- CircuiTikZ: publication quality, LaTeX-only, steep curve. WaveDrom: JS, timing/bitfield/register, sync-grid-only. tikz-timing. draw.io/Inkscape/PowerPoint: manual, dominant for fab/packaging.
- Gap (my read): nothing code-driven covers process cross-sections, fab flow, packaging stacks, and clocks/timing in one consistent style. EDA tools (KLayout, Magic) draw layouts, not explanatory figures.
- Where we're distinctive: pure stdlib, SVG+PNG+PDF, math markup for labels (t_pd, V_DD, \frac), auto-layout flow charts, grouped hierarchies, MCP access for LLM-driven generation, repo-tested golden images.

## 3. Proposed galleries
Engine primitives (from CAPABILITIES): Polygon/Polyline/Path, Band, Solid/cuboid/oblique/isometric, Bracket, leader, Text math markup, plot kit, auto layout, groups, orthogonal routing, align/distribute.

### A. `semiconductor` (recommended first)
Examples:
1. RTL-to-GDSII flow (auto layout, feedback loops, tool names)
2. Front-end/back-end fab flow (FEOL, BEOL, test, assembly) with loop-back
3. Photolithography step: coat/expose/develop/etch/strip cross-section strip
4. Planar NMOS/PMOS CMOS inverter cross-section (n-well, STI, poly, spacer)
5. FinFET vs GAA nanosheet cross-sections side by side
6. BEOL metal stack with vias, low-k, bump (Wikimedia-style)
7. Damascene vs subtractive metal process (multi-panel)
8. Die/wafer map with reticle shots, yield-by-die coloring
9. Advanced packaging stack: CoWoS-S, HBM, TSV, interposer, C4 bumps, substrate
10. Chiplet SoC floorplan (UCIe links, compute/IO/HBM tiles)
Icons (12): wafer, die, reticle_mask, euv_scanner, etch_chamber, cvd_chamber, ion_implanter, cmp_pad, tsv, solder_bump, hbm_stack, probe_card.
Needs: layered rect/polygon cross-sections with hatch/fill patterns (check Path/Polygon pattern fill support), taper/trapezoid shapes, wafer circle with die grid (plot kit or computed), optional isometric solids for 3D FinFET. Likely hard: realistic 3D FinFET/GAA, true-scale geometry, and photo-realistic fab tools; use schematic icons only. Overlaps manufacturing/01, 02, 06, 05 (wafer fab loop, litho cell, assembly, yield): avoid duplicating; link instead.
Effort: M-L (cross-section helpers are new reusable code). Demand 4, Fit 3, Differentiation 5.

### B. `electronics` (circuits and digital timing)
Examples:
1. RC low-pass filter schematic + Bode plot
2. Op-amp inverting/non-inverting amp with gain math
3. BJT/MOSFET common-source amplifier with bias network
4. Buck converter schematic + inductor current waveform
5. Full-wave rectifier with ripple waveform
6. 555 timer astable circuit + output waveform
7. SPI/I2C timing diagram (clock, MOSI, bit fields)
8. Synchronous clock tree / clock domain crossing with setup/hold timing
9. PCB floorplan/stackup (4-layer stackup, via types, placement outline)
10. Power delivery network: VRM, bulk/decoupling caps, impedance vs frequency
Icons (14): resistor, capacitor, inductor, diode, led, npn, nmos, pmos, opamp, ground, battery, crystal, ic_dip, connector.
Needs: parametric symbol path functions (as in physics/03, would need a shared `circuit` helper to avoid copy-paste), wire junctions (Junction exists), plot kit for waveforms/Bode, WaveJSON-like timing helper (new). Likely hard: dense schematics with auto-routing around symbol pins (orthogonal router targets boxes, not pin-level nets), net labels, true PCB layout. Overlaps physics RLC, logic gates/flip-flop. Fully competes with schemdraw/CircuiTikZ on the schematic half; timing + plot + math labels are the distinctive half.
Effort: M (symbols and timing helper) to L (if a netlist-like schematic layout is added). Demand 4, Fit 3 (symbols easy, routing awkward), Differentiation 2-3.

### Recommendation
Do `semiconductor` first (less competition, uses cross-section and auto-layout strengths, SEO-friendly AI/HBM topic). Make `electronics` second, scoped to waveforms/timing/PCB/power with a small symbol helper rather than a schemdraw clone. Possible split: move clock tree/timing to a `digital_design` gallery with logic if it feels crowded.

## 4. Scores
| Gallery | Effort | Demand | Engine fit | Differentiation |
|---|---|---|---|---|
| semiconductor | M-L | 4 | 3 | 5 |
| electronics | M (L with netlist routing) | 4 | 3 | 2-3 |

## Uncertainty
No quantitative demand data (stars/downloads/search volume). Did not verify engine pattern fills, hatch, or Path arc support. Did not browse Reddit/StackExchange/IEEE sources. Wikimedia/patent items show people draw these; they don't show people would adopt a code tool.

# Source report: chembio
# Research: chemistry / biology / ChemE-PFD galleries

## Engine baseline (from repo)
Primitives: shapes/groups, auto-layout (layered, LR/TB), orthogonal + Bezier edges, plot kit (axes, log, curves, bands, ODE/RK4, bars), draft kit (dimension lines, hatching, leaders, organic outlines, ECG traces), math markup (sub/superscripts, `\to \rightleftharpoons`? NOT listed: only `\to \leftrightarrow \Rightarrow \longrightarrow \rightsquigarrow`, `\frac`, `\mathrm`). Existing overlap: medical/ already has SIR, cell cycle, Michaelis-Menten, dose-response, action potential, O2 dissociation; physics/10 has hydrogen levels. So biology must avoid repeating those.
Gap in math markup: no equilibrium arrow (`\rightleftharpoons`/`\leftrightharpoons`), no `\ce{}` auto-subscripts, no charge/state notation helpers. Small addition, high value.

## 1. Demand evidence (honest: mostly circumstantial; no ranking of "most drawn diagrams" found)
- LaTeX chemistry community is large and tool-rich: chemfig (curved arrows, reaction schemes, PGF/TikZ-based) [manual](https://ctan.csail.mit.edu/macros/generic/chemfig/chemfig-en.pdf), [Wikipedia](https://en.wikipedia.org/wiki/Chemfig), mychemistry for reaction schemes [doc](https://ctan.csail.mit.edu/obsolete/macros/latex/contrib/mychemistry/mychemistry_en.pdf), mhchem for formulas [Moodle docs](https://docs.moodle.org/37/en/Chemistry_notation_using_mhchem). Shows people want text-coded reaction schemes.
- Researcher figure tooling market: BioRender (free tier 3 figures/month, paid from $35/mo per its own page) with many alternatives (Inkscape+Bioicons, draw.io+Bioicons, SciDraw, Mind the Graph) [BioRender comparison](https://www.biorender.com/vs/alternatives), [AlternativeTo](https://alternativeto.net/software/biorender), [Addgene toolbox](https://blog.addgene.org/early-career-researcher-toolbox-free-tools-for-making-scientific-graphics), [LabCritics](https://labcritics.com/open-source-alternatives-to-biorender/). Pain: manual assembly, licensing, price. Note: vendor-written pages, treat as soft evidence.
- Bioinformatics: tree drawing via ETE [paper](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC2820433/) and Biopython Bio.Phylo [paper](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3468381/); pathway standards SBGN [tips paper](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC5813898/) and Escher metabolic maps [paper](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC4552468/). Shows demand for scripted, reproducible figures.
- ChemE: ISO 10628 defines PFD/P&ID content and symbols (Part 1 diagrams, Part 2 symbols) [Wikipedia](https://en.wikipedia.org/wiki/ISO_10628); commercial symbol libraries (Vista Projects 181 symbols [page](https://www.vistaprojects.com/pfd-symbols/), [Creately](https://creately.com/guides/pfd-symbols/)). Search found NO diagram-as-code PFD tool (absence of evidence only; not exhaustively searched).
- Education: College Board AP Chem/Bio free-response booklets contain space for graphs/diagrams [AP Central](https://apcentral.collegeboard.org/help-center/will-free-response-booklets-contain-graphs-or-diagrams-students); a study guide lists reaction coordinate diagrams and titration/calorimetry apparatus sketches [Fiveable](https://fiveable.me/ap-bio/science-practices/science-practice-2-visual-representations/study-guide/NcMKVi6oFNNIuzMdBcd2) (AP Bio link; chem claim came via search summary, weakly verified). NOT confirmed: Punnett/central dogma as frequent exam drawings.
- Not verified (no source found): RDKit depiction details (from my own knowledge, RDKit's `Draw` module renders SVG from SMILES).

## 2. Competing tools and gaps
| Tool | Strength | Gap vs us |
|---|---|---|
| RDKit / ChemDraw / Marvin | real molecule depiction, SMILES | not schematic/teaching diagrams; heavy dependency (RDKit C++); ChemDraw proprietary |
| chemfig/mhchem/TikZ | reaction schemes in LaTeX | needs LaTeX toolchain, steep syntax, no auto-layout |
| BioRender | polished icons, GUI | paid, manual, not scriptable/diffable |
| Inkscape/draw.io + Bioicons | free | manual, not reproducible |
| Graphviz | graph layout | no domain shapes, needs binary |
| ete3/Bio.Phylo | trees | matplotlib/Qt dependencies; trees only |
| SBGN tools (CellDesigner, Newt, yEd), Escher | formal pathway maps | GUI/web, specialized notation |
Our niche: zero-dependency, scripted, deterministic, diffable SVG for schematic teaching/report figures with plots + math + icons in one engine. Reproducible-by-code is the differentiator.

## 3. Proposed galleries

### Scope line (honest)
IN: schematic/block figures: reaction equations, energy profiles, curves (plot kit), apparatus built from simple geometry, pathway/flow boxes, trees, grids. OUT: automatic molecule layout from SMILES, ring perception, stereochemistry wedges, bond-angle-correct skeletal structures, 3D, protein structures. Skeletal structures: only hand-placed hexagon/benzene template and a few chain zig-zags via polyline; no valence checking. Say so in docs.

### A. chemistry (11)
Examples: 1 Reaction energy profile (exo/endo, Ea, catalyst dashed path); 2 Strong acid-strong base titration curve (equivalence, pH 7); 3 Weak acid titration with buffer region and pKa; 4 Maxwell-Boltzmann distribution with Ea shading; 5 Water phase diagram (P-T, triple/critical points, log axes); 6 SN2 mechanism with curved arrows and transition state (hand-placed atoms); 7 Fractional distillation / simple distillation apparatus; 8 Titration setup (burette, flask, stir bar) with draft dimension leaders; 9 Molecular orbital diagram H2/O2 (levels + electron arrows, like physics hydrogen levels); 10 Periodic-table block/trend map (grid, group colors, electronegativity arrow); 11 Le Chatelier / rate-law concentration-vs-time (zero/1st/2nd order, ln[A] plot).
Icons (12): flask, beaker, burette, condenser, bunsen, test_tube, funnel, hotplate, thermometer, fume_hood, electron_pair, catalyst.
Primitives: plot, draft leaders/hatching, curved edges, math markup with sub/superscripts and arrows. Needs: equilibrium arrow glyph, `\ce`-style helper (S).
Weak: benzene/ring drawings, bond angles, stereo wedges.

### B. biology (11; avoid medical duplicates)
Examples: 1 Central dogma (DNA->RNA->protein, with replication loop); 2 Transcription/translation detail (ribosome, codons, tRNA); 3 Glycolysis-TCA metabolic pathway boxes with ATP/NADH tallies; 4 MAPK/receptor signalling cascade (phosphorylation, inhibition T-bars); 5 Cell structure (animal vs plant, organic outlines from draft kit); 6 Phylogenetic tree (cladogram + scale bar, from Newick-like nested tuples); 7 Food web/trophic pyramid with energy transfer 10%; 8 Punnett square (monohybrid + dihybrid 4x4) with ratio table; 9 PCR cycle workflow + thermocycler temperature trace; 10 NGS pipeline (reads -> QC -> align -> variant call); 11 Logistic vs exponential growth / predator-prey Lotka-Volterra (RK4 already available).
Icons (13): dna, ribosome, cell, mitochondrion, chromosome, enzyme, receptor, membrane, petri_dish, pipette, plasmid, virus, microscope.
Primitives: plot + ODE, draft organic outlines, auto layout, grid shapes, inhibition end-caps (check: T-bar edge ending may need adding).
Weak: realistic organelle art, protein structure, helix drawing (could do parametric sine ladder via plot/polyline, moderate).

### C. chemical_engineering (PFD, 10), recommend as third gallery or fold into existing `engineering/`
Examples: 1 Simple process flow (feed, heat exchanger, reactor, separator); 2 Distillation column with condenser/reboiler/reflux; 3 CSTR with jacket and control loop; 4 Heat exchanger network (shell and tube) with duty/temps; 5 Mass balance block with stream table (shapes + table); 6 Ammonia/Haber loop with recycle and purge; 7 Closed-loop PID level control; 8 Pump curve vs system curve operating point (plot); 9 McCabe-Thiele diagram (equilibrium curve, stairsteps); 10 Residence time distribution E(t) CSTR vs PFR.
Icons (12): pump, compressor, heat_exchanger, reactor_cstr, column, tank, valve, separator, filter, furnace, control_valve, flow_transmitter.
Primitives: orthogonal routing with ports (strong), groups, plot kit, auto-layout LR. Strong fit; ISO 10628 symbols are simple glyphs. Check overlap with existing iiot/manufacturing/engineering icons (valve, tank, pump may already exist; run `icons` to dedupe).

## 4. Effort and scores
| Gallery | Effort | Demand | Engine fit | Differentiation |
|---|---|---|---|---|
| chemistry | M (L if skeletal structures) | 4 | 3 (4 without structures) | 4 (chemfig is the only code alternative, LaTeX-only) |
| biology | M | 4 | 4 | 3 (BioRender/Inkscape strong on art, weak on code; medical overlaps) |
| chemical_engineering PFD | M | 3 | 5 | 5 (no diagram-as-code PFD tool found) |

Recommended order: PFD (best fit, least overlap) -> chemistry (add equilibrium arrow first) -> biology. Pre-work (S): `\rightleftharpoons` and `\ce`-like helper in math markup; T-bar edge ending. Caveat: demand scores are judgment from tooling-market evidence, not measured usage data.

# Source report: ai
# Research: AI architecture and AI software development galleries

## 0. Existing coverage
The `ai` gallery has 11 scripts: simple RAG, multimodal vision, agentic tool orchestration, distributed training, feature store/MLOps, LoRA fine-tuning, GraphRAG/KG, guardrails/safety eval, robotics SLAM, vLLM cluster, and an auto-laid-out training pipeline.
Its 7 icons are agent, brain, chip, model, vector_db, vision and workflow.
All 11 scripts are system or infrastructure block diagrams.
Not covered: model internals (transformer, attention, MoE, diffusion), agent design patterns, MCP, eval harnesses, coding-agent and SDLC loops, LLMOps tracing, and governance.

## 1. Demand evidence
- **Agent patterns are widely published.**
  - Anthropic "Building effective agents" names prompt chaining, routing, parallelization, orchestrator-workers and evaluator-optimizer, each with a diagram: https://www.anthropic.com/research/building-effective-agents
  - LangChain documents supervisor and handoff (swarm) multi-agent architectures: https://docs.langchain.com/oss/python/multi-agent
  - LangChain benchmarked multi-agent architectures: https://www.langchain.com/blog/benchmarking-multi-agent-architectures
  - Planner-executor and re-planner are covered in the practitioner guides at https://seanlewis08.github.io/posts/multi-agent-patterns/index.html and https://dev.to/focused_dot_io/multi-agent-orchestration-in-langgraph-supervisor-vs-swarm-tradeoffs-and-architecture-1b7e
  - Survey paper: https://arxiv.org/pdf/2606.24937
- **MCP has a canonical host / client / server architecture diagram.** The official spec carries it (host with several clients, each paired 1:1 with a server): https://modelcontextprotocol.io/specification/2025-11-25/architecture. The 2026-07-28 revision is stateless: https://modelcontextprotocol.io/specification/2026-07-28/architecture.md. A Hugging Face course unit teaches the same model: https://huggingface.co/learn/mcp-course/en/unit1/architectural-components
- **Spec-driven development is a diagram-heavy topic.**
  - GitHub Spec Kit runs constitution, specify, plan, tasks: https://github.blog/ai-and-ml/generative-ai/spec-driven-development-with-ai-get-started-with-a-new-open-source-toolkit
  - Kiro runs requirements, design, tasks: https://kiro.dev/blog/from-chat-to-specs-deep-dive/
  - Fowler's comparison of Kiro, Spec Kit and Tessl: https://www.martinfowler.com/articles/exploring-gen-ai/sdd-3-tools.html
  - Paper: https://arxiv.org/html/2602.00180v1
- **LLMOps, observability and evals** are a vendor-driven topic.
  - Tracing spans across prompt, retrieval, tool and eval, plus OTel GenAI conventions: https://mlflow.org/articles/setting-up-llm-observability-pipelines-in-2026
  - `gen_ai.evaluation.result` event (Development stability): https://www.dash0.com/knowledge/what-is-llm-evaluation
  - Study of 57 evaluation harnesses: https://arxiv.org/pdf/2605.24213
- **Model-internals figures are standard in papers and teaching.** NN-SVG (LeNail 2019, JOSS 4(33), 747): https://github.com/aivilmo/NN-SVG. The PlotNeuralNet forks, such as https://github.com/Chi20/PlotNeuralNet, show demand for code-defined network figures. A KDnuggets write-up: https://www.kdnuggets.com/2020/12/generating-beautiful-neural-network-visualizations.html
- **People want LLM-drawn diagrams but find them unreliable.**
  - Coordinate guessing leads to overlapping boxes and tangled arrows, so the project hands layout to a graph algorithm: https://cdn.jsdelivr.net/gh/bv-venky/excalidraw-architect-mcp@main/README.md
  - Excalidraw and draw.io formats are verbose and diff badly in Git, and Mermaid layout is hard to steer: https://dev.to/akari_iku/analyzing-the-best-diagramming-tools-for-the-llm-age-based-on-token-efficiency-5891
  - Mermaid reliability rose from about 70% to near 100% only after validate-and-repair loops: https://llm-enabled-development-41d6d8.pages.cms.hu-berlin.de/en/experiments/diagram/diagram-long
  - Mermaid's layout runs in a headless browser, which is heavy inside an agent loop: https://dev.to/msteja/why-ai-agents-cant-draw-svg-and-what-to-do-instead-1ci
  - A request for native draw.io output with sane layout and routing: https://community.openai.com/t/feature-request-native-enterprise-architecture-diagram-generation-xml-beyond-mermaid-etc/1374510

Caveat: these are search-result summaries, not full page reads. Several sources are vendor blogs. I did not find direct download or usage numbers for any diagram tool.

## 2. Competing tools and gaps
| Tool | Strength | Gap versus us |
|---|---|---|
| draw.io, Excalidraw | Manual, ubiquitous | Verbose XML/JSON, poor diffs, LLMs guess coordinates |
| Mermaid | Text-based, renders in GitHub and docs | Auto-layout is hard to steer, no model-architecture shapes, needs a browser to render, no lint |
| NN-SVG | Interactive MLP/CNN figures | Only FCNN, LeNet and AlexNet styles, no transformers or agents, GUI-only |
| PlotNeuralNet | Code-defined CNN figures in TikZ | Needs a LaTeX toolchain, no agent or system diagrams |
| LangGraph / framework viz | Auto-generated graph from code | Shows framework wiring only, little styling control, no icon vocabulary |

**Differentiator.** Our engine is deterministic and pure stdlib, with no Graphviz, LaTeX or browser. It lints and audits diagrams, has an MCP server so agents can render and lint, and produces byte-stable SVG that diffs cleanly in Git. That is a direct answer to the "LLMs guess coordinates and diagrams diff badly" complaints above. One idea to test: the lint step could act as the validate-and-repair loop that the HU Berlin project had to build for Mermaid.

**Communities.**
- AI app developers (agent patterns, MCP, RAG, evals, observability) are the largest group and the one most likely to put diagrams in READMEs.
- ML engineers (serving, training, LLMOps).
- Researchers and educators (transformer, attention, MoE, diffusion, RL loops).
- Architects and governance staff (risk, compliance, data lineage).

## 3. Proposal
**Recommendation: extend `ai` only lightly, and add two new galleries.** Keep `ai` for infrastructure and MLOps. Its 7-icon namespace is small, but its content is coherent. Gallery size is 10-11 examples, and agent patterns alone would swamp it.

### Gallery A: `agentic_dev` (agent design, MCP, AI-assisted SDLC, evals, LLMOps). Highest priority.
1. Prompt chain with gate (Anthropic pattern)
2. Router and parallelization (sectioning and voting)
3. Orchestrator-workers
4. Evaluator-optimizer loop
5. Supervisor multi-agent versus handoff swarm (side by side)
6. Planner-executor with re-planner
7. MCP host / clients / servers (stdio and remote)
8. Agentic RAG, with query rewrite, retrieval-grade loop and web fallback
9. Spec-driven dev loop (constitution, spec, plan, tasks, implement, verify)
10. Coding-agent harness (context, tools, sandbox, hooks, permissions, subagents)
11. Eval harness and LLM-as-judge (dataset, runner, judge, regression gate)
12. LLM observability pipeline (OTel spans, trace store, online eval sampling)

That is 12 candidates, so cut 1-2 to fit the 10-11 convention.

### Gallery B: `ml_models` (model internals and training)
1. Transformer encoder-decoder block
2. Decoder-only LLM block (pre-norm, GQA, RoPE)
3. Multi-head attention data flow (Q/K/V, heads, concat)
4. Mixture of Experts layer (router, top-k, experts)
5. Diffusion model (forward noising, U-Net, reverse denoising)
6. RL loop (agent, environment, policy, reward; PPO/RLHF)
7. RLHF/DPO post-training pipeline
8. CNN (conv, pool, FC, with 3D layer slabs)
9. Autoencoder / VAE
10. LoRA adapter injection (the existing LoRA example is pipeline-level, so this one is weight-level)
11. KV cache and speculative decoding

Candidate 11 can move to `ai` if the gallery gets too big.

### Gallery C or extra `ai` scripts: governance
Model risk and governance, and data/feature lineage. Governance, EU AI Act style risk tiers and an AI system card could be 3-4 additional `ai` examples instead of a separate gallery.

### Icon set to add (17 names)
Add the agentic icons to a new `agentic_dev` set and the model-internals ones to `ml_models`.
- Agentic set: `tool`, `mcp_server`, `mcp_client`, `prompt`, `context_window`, `memory`, `planner`, `judge`, `guardrail`, `sandbox`, `trace`, `eval_dataset`, `spec_doc`, `code_agent`, `human_review`, `router`, `skill`
- ML set (also usable for the `ai` set): `attention`, `embedding`, `layernorm`, `expert`, `tokenizer`, `diffusion_unet`, `reward_model`, `checkpoint`
The mandated 12-18 range is met by the first list; trim `skill` if needed.

### Engine primitives required
Already present per `docs/CAPABILITIES.md`:
- boxes, nesting via `shape.inside()`, layer bands, fractional side anchors for edges
- shared-trunk fan-out, two-way arrows
- oblique and isometric solids, which fit CNN and tensor slabs
- ellipsis connectors, z-order, align and distribute

Likely gaps:
- **Loop and feedback edges.** Agent loops (evaluator-optimizer, RL) need clean back-edges that do not cross nodes. Check the router for loop routing.
- **Matrix and tensor glyphs.** Grid cells for attention matrices need a small helper. These can be built from rects, but a helper avoids boilerplate.
- **Stacked-repeat "xN" brackets** for transformer layers, probably doable with brackets and captions.
- **Math labels.** The in-progress `text/math.py` already supports `\frac`, which helps with softmax(QK^T/sqrt(d)) labels.
- **Sequence diagrams** (agent / tool / MCP message flow with lifelines). I did not check whether these exist. This is the biggest likely gap, since MCP and tool-call flows are often drawn as sequence diagrams.

### What the engine cannot do well
- Animated or interactive figures (NN-SVG-style 3D rotation). There is a `renderer_interactive.py`, but I did not assess it.
- Dense neuron-level graphs, such as a fully connected net with hundreds of nodes. That is better done parametrically in a separate helper.
- Photoreal or artistic diffusion illustrations.
- Auto-generating diagrams from live framework graphs (LangGraph, OTel), which is an integration job rather than a drawing task.

## 4. Effort and scores
| Item | Effort | Demand | Engine fit | Differentiation |
|---|---|---|---|---|
| `agentic_dev` gallery + icons | M | 5 | 4 | 5 |
| `ml_models` gallery + icons | M-L (tensor glyphs, loop routing, 3D slabs) | 4 | 3 | 4 |
| Governance / lineage as 3-4 `ai` additions | S | 3 | 5 | 3 |
| Sequence-diagram primitive (if missing) | M | 5 | 2 | 4 |

**Suggested order.**
1. `agentic_dev` first. It is mostly boxes and arrows, which suit the engine, and the demand is strongest.
2. `ml_models` second.
3. Governance additions to `ai` last.
4. Check for a sequence-diagram primitive before committing to the MCP and tool-call examples.

# Source report: devops_project
# Research: DevOps / Data Eng and Project / Org galleries

## 0. Already covered (do not duplicate)
- cloud: VPC, serverless pipeline, CDN, hybrid VPN, service mesh (05), multi-cloud DR, lakehouse ingest (07), zero-trust, IoT fleet, backbone, auto pipeline.
- database: ER, star schema, CDC pipeline (05), lakehouse medallion (06), query plan, PITR backup.
- datacenter: Kubernetes bare metal (06). business_process: incident escalation (03), software release gate (06), change mgmt (10).
- enterprise_architecture: C4 context + container, ArchiMate, value-stream capability map (07), transition roadmap (08).
- mind_map: product launch plan, OKRs (05), risk register (06), five-whys retro (08). technical: state machine, timing diagram.
- Engine: auto layered layout (LR/TB), groups, dashed bands, plot kit (axes, bars, custom ticks), arrows/routing. No evidence of native Gantt, swimlane, sequence/UML, kanban, org-chart or matrix primitives (CAPABILITIES grep found none). Plot kit gives time-axis bars via custom tick labels.

## 1. Demand evidence
- GitOps/CI-CD reference diagrams are published by every cloud vendor: Azure AKS GitHub Actions + GitOps https://learn.microsoft.com/en-gb/azure/architecture/guide/aks/aks-cicd-github-actions-and-gitops ; Flux v2 https://learn.microsoft.com/en-gb/azure/azure-arc/kubernetes/conceptual-gitops-ci-cd ; AWS Argo CD https://docs.aws.amazon.com/prescriptive-guidance/latest/eks-gitops-tools/argo-cd.html ; Oracle https://docs.oracle.com/en/solutions/deploy-gitops-argocd-oke . Common shape: CI build -> registry -> config repo -> in-cluster Argo/Flux pull -> dev/staging/prod clusters (push vs pull comparison).
- dbt/Airflow/medallion/lineage: dbt DAG docs https://docs.getdbt.com/terms/dag ; Cosmos-generated Airflow DAGs and OpenLineage described at https://ilum.cloud/docs/user-guides/orchestrate-dbt-with-airflow/ and https://www.bacancytechnology.com/insights/how-we-built-data-lineage-automation ; Bronze-Silver-Gold LR flow https://fgarofalo56.github.io/csa-inabox/best-practices/medallion-architecture/ . Vendor-heavy sources; no single canonical notation.
- Diagrams-as-code is an established community: Structurizr "as code" https://docs.structurizr.com/as-code ; tool comparison https://dev.to/icepanel/top-7-diagrams-as-code-tools-for-software-architecture-3h4a ; notation guide https://hidekazu-konishi.com/entry/diagramming_c4_plantuml_mermaid_selection_guide.html ; Mermaid's key advantage is native GitHub rendering.
- Gantt: Mermaid supports `after`/`until` and a manual `crit` flag only (critical path is not computed) https://deepwiki.com/mermaid-js/mermaid/3.3-gantt-diagrams ; GitHub Issues has no native Gantt (vendor claim, secondary). Rendering pitfalls (date-format mismatch, font settings not scaling): https://buttondown.com/weekly-project-news/archive/weekly-github-report-for-mermaid-march-09-2026 .
- Platform feature requests for Mermaid-style timelines/mindmaps: https://community.lucid.co/ideas/add-timelines-and-mindmaps-as-supported-mermaid-code-diagrams-9458 ; org charts requested in BI tools https://feedback.mongodb.com/forums/923524-charts/suggestions/46956811-support-for-org-charts .
- Not verified (searches returned nothing usable): Kafka, SLO/observability, value-stream, CFD, RACI popularity. I rate those from general practitioner knowledge, not cited evidence.

## 2. Competitors and gaps
| Tool | Strength | Gap vs us |
|---|---|---|
| Mermaid | GitHub native, huge reach, gantt/timeline/kanban/C4/sequence | Auto layout only, limited styling, no computed critical path, layout varies by version, no lint |
| PlantUML | UML/sequence/Gantt depth | Java + Graphviz, dated look |
| Structurizr | C4 model-as-code, multi-view | Auto-layout export only; C4 only |
| diagrams.py (mingrammer) | Cloud/K8s icons, Python | Needs Graphviz; no timelines/charts; uneven layout |
| draw.io / Excalidraw | Manual, ubiquitous | Not code-driven; diff-hostile |
| Gantt tools (MS Project, GanttProject, TeamGantt) | Scheduling | Not text/versionable, not embeddable as lintable SVG |
Differentiator: deterministic SVG (byte-stable, git-diffable), pure stdlib (no Java/Graphviz/Node), lint/audit gate, themes, BOM, MCP, hand-placed precision plus auto layout. Gap: no sequence, Gantt, swimlane, org tree primitives yet.

## 3. Proposed galleries
Primitive status: OK = expressible now; NEW = needs primitive.

### A. devops (S-M)
Titles: 1 GitOps pull vs push (Argo CD/Flux); 2 CI pipeline stages with quality gates; 3 Trunk-based vs GitFlow branching (commit graph); 4 Progressive delivery canary/blue-green; 5 Kubernetes control plane + node anatomy; 6 Kubernetes namespace/ingress/service topology; 7 Observability stack (metrics/logs/traces, OTel collector); 8 SLO / error-budget burn chart (plot); 9 Incident timeline (detect/mitigate/resolve); 10 Terraform plan/apply state flow; 11 auto-layout: build-to-prod dependency graph.
Icons (13): repo, commit, branch, pipeline, build, registry, container, pod, helm, argo-sync, canary, alert, dashboard.
Primitives: OK boxes/groups/arrows/plot. NEW: commit-graph helper (lanes, merge edges, tags), timeline-axis helper. Weak: live metric fidelity, big real clusters.
Overlap risk: service mesh (cloud 05), release gate (BPM 06), K8s bare metal.

### B. data_engineering (S-M)
Titles: 1 dbt model lineage DAG (staging/intermediate/marts); 2 Airflow DAG with task states and retries; 3 Kafka topic/partition/consumer-group; 4 Stream processing windows (tumbling/sliding/session, plot); 5 Lambda vs Kappa architecture; 6 Column-level lineage; 7 Data contract and schema registry flow; 8 Feature store online/offline; 9 Data mesh domains and data products; 10 Batch ETL idempotent backfill timeline; 11 auto-layout: ingestion-to-BI.
Icons (13): source, topic, partition, stream, dag-task, table, view, lake, warehouse, schema, contract, feature, dashboard.
Primitives: OK layered auto-layout, groups, plot for windows. NEW: partition-cell strip, event-time axis. Weak: huge lineage graphs (hundreds of nodes), column-level port-to-port edges.
Overlap: medallion (database 06), CDC (05), lakehouse ingest (cloud 07) - differentiate with dbt/Airflow/Kafka specifics; skip another medallion.

### C. project_management (M-L)
Titles: 1 Gantt with dependencies and critical path; 2 Quarterly roadmap (now/next/later); 3 Release train / PI timeline; 4 Kanban board with WIP limits; 5 Cumulative flow diagram (plot); 6 Burndown/burnup (plot); 7 Risk matrix 5x5 heatmap; 8 RACI matrix; 9 Value-stream map with lead/process time; 10 PERT/CPM network (earliest/latest start); 11 auto-layout: work breakdown structure.
Icons (13): milestone, task, sprint, epic, backlog, kanban-card, risk, dependency, deliverable, gate, baseline, resource, timebox.
Primitives: OK plot (CFD, burndown), boxes (RACI grid, risk matrix). NEW: time-axis Gantt (date scale, bars, milestones, today line, dependency arrows), swimlane/table grid, matrix/heatmap cell helper. Weak: automatic scheduling (stdlib date math is fine, but resource levelling is out of scope), >100 tasks.
Overlap: transition roadmap (EA 08), risk register mind map, value-stream capability map (EA 07, a capability view, not a lead-time VSM).

### D. org (M)
Titles: 1 Org chart (hierarchy, dotted-line reports); 2 Matrix organisation; 3 Team Topologies (stream-aligned/platform/enabling); 4 OKR tree (company->team->KR); 5 Decision-rights / RACI by role; 6 Spotify-style squads/tribes/guilds; 7 Span-of-control and headcount plan; 8 Stakeholder power/interest grid; 9 On-call rotation and escalation ladder; 10 Hiring funnel (plot); 11 auto-layout: reporting tree.
Icons (12): person, team, manager, role, department, board, guild, oncall, vacancy, stakeholder, okr, decision.
Primitives: OK auto layered TB tree. NEW: dedicated tree layout with sibling compaction and assistant/dotted edges; matrix grid. Weak: very wide orgs (>50 siblings), photos.
Overlap: OKR mind map, escalation BPM. Lowest differentiation; consider folding into project_management as 5 diagrams.

## 4. Scores (1-5; effort S/M/L)
| Gallery | Demand | Engine fit | Differentiation | Effort |
|---|---|---|---|---|
| devops | 5 | 4 | 3 (Mermaid/diagrams.py crowded; our edge is styling/determinism) | M |
| data_engineering | 4 | 4 | 4 (little competition for polished Kafka/windowing/lineage) | M |
| project_management | 5 | 2 now / 4 after Gantt primitive | 4 (Mermaid Gantt is weak; deterministic, lintable Gantt is a real gap) | L |
| org | 3 | 3 | 2 | M |

## 5. Recommendation
1. Build a time-axis Gantt/timeline primitive first; it unlocks project_management (roadmap, release train, incident timeline, ETL backfill, devops timelines).
2. Ship data_engineering next (highest differentiation per effort, no new primitive beyond a small axis helper).
3. Ship devops with a commit-graph helper; avoid repeating service mesh/medallion.
4. Defer org or merge into project_management. Add sequence diagrams as a separate UML cluster (not covered here; high demand per Mermaid/PlantUML ubiquity, unverified by search).

