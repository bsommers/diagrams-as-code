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
- The core engine (`src/iiot_diagrams/`) is pure Python standard library: zero external C-dependencies (no Graphviz `dot`, Cairo, or ImageMagick required for SVG rendering).
- Do not add runtime dependencies to `dependencies = []` in `pyproject.toml` unless explicitly requested.
