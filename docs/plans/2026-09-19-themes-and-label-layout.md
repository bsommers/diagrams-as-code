# Themes, Label Layout Optimization, and Full Documentation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Expand the theme engine with 5+ new light/dark/accessibility palettes, eliminate label text spilling via multi-line wrapping and "text-below-graphic" positioning, showcase 3-5 theme varieties per domain across all 80 examples, and deliver a comprehensive documentation suite (`docs/` and `docs/diagrams/`).

**Architecture:** Extend `Theme` registry in `src/diagrams_as_code/theme.py` with palette discovery and dynamic override capabilities. Upgrade `Shape` and `RendererSVG` in `src/diagrams_as_code/renderer_svg.py` to support `label_position="bottom"` (text below graphic), `<tspan>` multi-line wrapping, dynamic font scaling, and `kind="icon"`. Update all 80 domain examples and regenerate outputs. Synthesize complete documentation following the repository standard.

**Tech Stack:** Python 3.13, `uv`, `pytest`, `resvg-py` (PNG rendering), SVG, Mermaid, Draw.io XML, ASCII.

## Global Constraints
- Pure Python standard library for core layout and SVG generation (zero C-dependencies).
- Always use `uv` for package management, script running, and testing (`uv run pytest`).
- Backward compatibility: all public APIs in `src/diagrams_as_code/` remain re-exported through `src/iiot_diagrams/`.
- Strict execution constraints: zero conversational filler, bullet points under 5 words per line.

---

### Task 1: Theme Engine Expansion & Palette Customization

**Files:**
- Modify: `src/diagrams_as_code/theme.py`
- Modify: `src/diagrams_as_code/diagram.py`
- Modify: `src/iiot_diagrams/theme.py`
- Modify: `src/iiot_diagrams/diagram.py`
- Test: `tests/test_theme.py`

**Interfaces:**
- Consumes: `Theme` dataclass
- Produces:
  - `list_themes() -> list[str]`
  - `get_light_themes() -> list[str]`
  - `get_dark_themes() -> list[str]`
  - `create_theme(name: str, base: str = "iiot_dark_gold", **overrides) -> Theme`
  - `get_theme(name_or_theme: Union[Theme, str]) -> Theme`
  - 5 new built-in themes: `solarized_light`, `pastel_light`, `dracula`, `synthwave`, `high_contrast`

- [ ] **Step 1: Write failing unit tests for new themes and theme customization in `tests/test_theme.py`**
- [ ] **Step 2: Run `uv run pytest tests/test_theme.py` to confirm failure**
- [ ] **Step 3: Implement new themes and helper functions in `src/diagrams_as_code/theme.py` and `diagram.py`**
- [ ] **Step 4: Update backward-compatibility facades in `src/iiot_diagrams/`**
- [ ] **Step 5: Run `uv run pytest tests/test_theme.py` to confirm all tests pass**

---

### Task 2: Label Spilling Resolution & Text Below Graphic Engine

**Files:**
- Modify: `src/diagrams_as_code/elements.py`
- Modify: `src/diagrams_as_code/shapes.py`
- Modify: `src/diagrams_as_code/renderer_svg.py`
- Modify: `src/diagrams_as_code/diagram.py`
- Modify: `src/iiot_diagrams/` facades
- Test: `tests/test_renderer_svg.py`

**Interfaces:**
- Consumes: `Element`, `Shape`, `RendererSVG`, `Theme`
- Produces:
  - `label_position` support on `Shape` and `Diagram` (`"inside"`, `"bottom"`, `"below"`, `"auto"`)
  - `wrap_text(text: str, max_chars: int) -> list[str]` in `RendererSVG`
  - Dynamic `<tspan>` multi-line rendering with baseline adjustment
  - Dynamic font scaling (10px - 12px) for long single-word labels
  - Auto-calculated width adaptation in `Shape.__init__`
  - `kind="icon"` pure vector icon rendering with label below graphic

- [ ] **Step 1: Write unit tests verifying text wrapping, `label_position="bottom"`, and `kind="icon"` in `tests/test_renderer_svg.py`**
- [ ] **Step 2: Run `uv run pytest tests/test_renderer_svg.py` to confirm test failure**
- [ ] **Step 3: Implement text wrapping and label positioning in `src/diagrams_as_code/renderer_svg.py` and `elements.py`**
- [ ] **Step 4: Verify with target examples (`cybersecurity/09` and `datacenter/03`) to prove zero spilling**
- [ ] **Step 5: Run `uv run pytest tests/test_renderer_svg.py` and full suite `uv run pytest` to ensure zero regressions**

---

### Task 3: Domain Examples Theming & Output Regeneration

**Files:**
- Modify: `examples/cloud/*.py`
- Modify: `examples/ai/*.py`
- Modify: `examples/computer/*.py`
- Modify: `examples/datacenter/*.py`
- Modify: `examples/business_process/*.py`
- Modify: `examples/cybersecurity/*.py`
- Modify: `examples/network_engineering/*.py`
- Modify: `examples/iiot/*.py`
- Modify: `output/` (regenerate all 80 diagrams: `.svg`, `.png`, `_README.md`)
- Modify: `examples/README.md`
- Test: `tests/test_domain_examples.py`

**Interfaces:**
- Consumes: `Diagram(theme=...)`, `Shape(..., label_position=...)`
- Produces:
  - 80 updated example scripts showcasing 3-5 theme varieties per domain
  - 240+ regenerated output artifacts under `output/`
  - Passing anti-stacking and anti-spilling test assertions

- [ ] **Step 1: Update domain example generator / scripts with 3-5 theme varieties and optimized margins/label positioning**
- [ ] **Step 2: Execute all 80 example scripts to regenerate `.svg`, `.png`, and `_README.md`**
- [ ] **Step 3: Visually verify `output/cybersecurity/09_iam_federation_saml_oidc.png` and `output/datacenter/03_leaf_spine_clos_network.png`**
- [ ] **Step 4: Update `tests/test_domain_examples.py` with theme variety checks and run `uv run pytest`**

---

### Task 4: Complete Documentation Suite & Multi-Format Diagrams

**Files:**
- Modify: `README.md`
- Create: `docs/README.md`
- Create: `docs/purpose.md`
- Modify: `docs/architecture.md`
- Create: `docs/running.md`
- Create: `docs/how-to.md`
- Create: `docs/diagrams/README.md`
- Create: `docs/diagrams/ascii_architecture.txt`
- Create: `docs/diagrams/architecture.mmd`
- Create: `docs/diagrams/execution_lifecycle.mmd`
- Create: `docs/diagrams/architecture.drawio`

**Interfaces:**
- Consumes: Codebase architecture, CLI, theme gallery, domain examples
- Produces:
  - Full `/documentation` compliant docs hub and multi-format diagrams (ASCII, Mermaid, draw.io XML)

- [ ] **Step 1: Author `docs/purpose.md`, `docs/running.md`, `docs/how-to.md`, and update `docs/architecture.md`**
- [ ] **Step 2: Generate multi-format diagrams in `docs/diagrams/` (`ascii_architecture.txt`, `.mmd`, `.drawio`)**
- [ ] **Step 3: Update `docs/README.md` and root `README.md`**
- [ ] **Step 4: Validate all markdown links and XML/Mermaid syntax**
