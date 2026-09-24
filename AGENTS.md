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
> 3. **Verify Clean Output Diffs:** Ensure `git diff --exit-code -- output/ icons/ README.md docs/` produces zero diff before pushing.
> 4. **No Speculative or Intermediate Remote Commits:** Never push intermediate, broken, or WIP commits to remote branches. Batch commits and push only fully verified, green changesets.
> 5. **Avoid Redundant CI Runs:** Planning files (`.planning/**`), documentation notes, and agent checkpoints must not trigger unnecessary remote builds.

