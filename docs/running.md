# Running & Installation Guide

## 1. Prerequisites

- **Python Version:** Python 3.10, 3.11, 3.12, or 3.13 (Python 3.13 recommended)
- **Package & Runtime Manager:** [`uv`](https://docs.astral.sh/uv/) (Required across all workflows)
- **Container Runtime (Optional):** Docker or Docker Compose

> [!IMPORTANT]
> Always use `uv` for environment management, dependency provisioning, and command execution. Never invoke bare `pip install` or direct un-sandboxed `python` commands.

---

## 2. Environment Setup

### 2.1 Clone and Synchronize Virtual Environment

```bash
git clone https://github.com/bsommers/diagrams-as-code.git
cd diagrams-as-code

# Synchronize dependencies and virtual environment with uv
uv sync
```

### 2.2 Adding as a Local or Git Dependency

To use `diagrams-as-code` in another project:

```bash
# Add as a local path dependency using uv
uv add --path /path/to/diagrams-as-code

# Or add directly from GitHub
uv add git+https://github.com/bsommers/diagrams-as-code.git
```

---

## 3. Running Scripts & Generating Diagrams

### 3.1 Run the Main Architecture Demonstration

```bash
uv run python main.py
```
This generates:
- `output/main_architecture.svg`
- `output/main_architecture.png`
- `output/main_architecture_README.md`

### 3.2 Run Any Domain Architecture Example

```bash
# Run a specific cloud architecture example
uv run python examples/cloud/01_simple_vpc_web.py

# Run an AI pipeline example
uv run python examples/ai/01_simple_rag_pipeline.py

# Run a cybersecurity Zero-Trust architecture example
uv run python examples/cybersecurity/09_iam_federation_saml_oidc.py
```

The three top-level examples recreate the original IIoT reference diagrams:

```bash
uv run python examples/01_mockup_slide.py
uv run python examples/02_high_availability.py
uv run python examples/03_sparkplug_pipeline.py
```

### 3.3 Batch Regenerate the Gallery

```bash
uv run diagrams-as-code render examples --out output --format svg,png,bom
```

This scans `examples/` for every script that defines `diagram()`, renders each
into its domain subdirectory under `output/`, and writes all three formats
(the default `--format` is `svg,bom`; `png` is added explicitly here since
PNG bytes are excluded from the batch's tracked comparison but useful to look
at locally).

### 3.4 The `diagrams-as-code` Command

Installed as a console script (`uv run diagrams-as-code ...`), and also
runnable as `uv run python -m diagrams_as_code ...`.

**`render PATH... [--out DIR] [--format FORMATS] [--theme THEME] [--layout MODE] [--direction DIR] [--layout-file FILE] [--debug]`**

Renders one or more scripts, or every `diagram()`-defining script found by
recursively scanning a directory. `--format` is a comma-separated subset of
`svg,png,bom`; it defaults to `svg,bom` because those two are the
byte-comparable, git-tracked artifacts — PNG bytes vary slightly by backend
(Cairo vs. the pure-Python fallback), so they're opt-in. `--theme`,
`--layout`, `--direction`, and `--layout-file` override the script's own
`Diagram(...)` settings for this render only. `--debug` prints full
tracebacks for scripts that fail to load or render.

**`layout export SCRIPT [-o FILE] [--layout MODE] [--direction DIR] [--layout-file FILE] [--debug]`**

Runs a script's `diagram()`, solves it, and writes every element's resolved
position to a JSON layout file (default: `SCRIPT.layout.json`). See
`docs/how-to.md` for the layout-file editing workflow.

**`themes`**

Lists every built-in theme name, one per line.

**`icons [--domain DOMAIN]`**

Lists every built-in icon as `name<TAB>domain<TAB>description`; `--domain`
filters to one domain.

**Exit codes:** `0` success; `1` one or more scripts failed to load, render,
or write (each failure is reported, and the command continues with the
rest); `2` a command-line usage error (unknown flag, missing subcommand).

---

## 4. Test Suite Execution

Execute the comprehensive 431-test automated suite using `uv run pytest`:

```bash
# Run all tests
uv run pytest

# Run tests with detailed verbosity
uv run pytest -v

# Run only domain example verification tests
uv run pytest tests/test_domain_examples.py

# Run only SVG renderer tests
uv run pytest tests/test_renderer_svg.py

# Run only theme system tests
uv run pytest tests/test_theme.py
```

---

## 5. Docker Build & Execution

For containerized environments, CI runners, or air-gapped deployments:

### 5.1 Using the Helper Script

```bash
./docker-build-n-run.sh
```

### 5.2 Using Docker Compose Directly

```bash
# Build the container image
docker compose build

# Run diagram generation in container
docker compose run --rm diagram-gen
```

---

## 6. Exit Codes

The `diagrams-as-code` CLI (§3.4) returns:

| Exit Code | Meaning |
|---|---|
| `0` | Success: every script loaded, solved, and wrote its requested formats. |
| `1` | One or more scripts failed to load, render, or write (a cycle in the layout constraints raises `RuntimeError` here); each failure is reported and the command continues with the rest. |
| `2` | Command-line usage error: unknown flag or missing subcommand. |

`uv run pytest` follows the ordinary pytest convention: `0` all tests passed, `1` at least one test failed.
