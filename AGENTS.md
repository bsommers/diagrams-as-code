# Agent Guidelines & Execution Constraints

## Universal Tooling Rule: Always Use `uv`

In this repository, **ALWAYS** use [`uv`](https://docs.astral.sh/uv/) for all Python package management, virtual environment provisioning, and script/test execution.
**NEVER** invoke bare `pip install`, `pip`, or un-sandboxed `python`/`pytest` commands directly outside of `uv`.

### Standard Commands
- **Environment Setup / Sync:** `uv sync`
- **Add / Remove Dependencies:** `uv add <package>` / `uv add --dev <package>` / `uv remove <package>`
- **Run Scripts:** `uv run python <script.py>` (e.g., `uv run python main.py`)
- **Run Tests:** `uv run pytest`
- **Container Build & Run:** `./docker-build-n-run.sh` or `docker compose run --rm diagram-gen`

### Architecture Constraints
- The core engine (`src/diagrams_as_code/`) is pure Python standard library: zero external C-dependencies (no Graphviz `dot`, Cairo, or ImageMagick required for SVG rendering). `src/iiot_diagrams/` is a backward-compatibility facade that re-exports it.
- Do not add runtime dependencies to `dependencies = []` in `pyproject.toml` unless explicitly requested.

## GitHub CI Quota Conservation & Local-First Verification

> [!IMPORTANT]
> Remote GitHub Actions CI minutes are constrained. Execute all verification steps locally before pushing or opening pull requests:
> 1. **Run Full Test Suite Locally:** Always run `uv run pytest` and verify 100% pass rate locally.
> 2. **Run Artifact Verification Locally:** Execute `uv run python main.py` and `uv run python tools/generate_icons.py --check`.
> 3. **Run the Visual Defect Audit:** Execute `uv run python tools/audit_gallery.py --check`. Counts may only go down; after fixing defects run `--update`. Passing tests are not evidence that a diagram looks right: rasterize changed diagrams and look at them.
> 4. **Verify Clean Output Diffs:** Ensure `git diff --exit-code -- examples/ icons/ README.md docs/` produces zero diff before pushing.
> 5. **No Speculative or Intermediate Remote Commits:** Never push intermediate, broken, or WIP commits to remote branches. Batch commits and push only fully verified, green changesets.
> 6. **Avoid Redundant CI Runs:** Planning files (`.planning/**`), documentation notes, and agent checkpoints must not trigger unnecessary remote builds.

## Using this library as an agent

If you are *using* diagrams-as-code (not changing it), read [`docs/for-agents.md`](docs/for-agents.md) first: which interface to pick (Python API, CLI, MCP), a verified quickstart, the 15 calls you need, the render and lint feedback loop, and the pitfalls. The API is `d = Diagram(title)`, `d.shape(label)` or `d.add(Shape(id, label))`, and `a >> d.edge(label) >> b`; there is no `add_node` or `add_edge`.

- [`docs/llms.txt`](docs/llms.txt) (index) and [`docs/llms-full.txt`](docs/llms-full.txt) (everything in one file) are served at <https://bsommers.github.io/diagrams-as-code/llms.txt>.
- [`docs/api-reference.md`](docs/api-reference.md): every public name with signature and docstring.
- [`examples/index.json`](examples/index.json): one record per example script (domain, title, theme, kits used).
- Those four files are generated: `uv run python tools/build_agent_docs.py` rewrites them and `--check` verifies them. Do not edit them by hand; edit a docstring or `docs/for-agents.md` instead. Every code block in `docs/for-agents.md` is executed by `tests/test_for_agents_doc.py`.
