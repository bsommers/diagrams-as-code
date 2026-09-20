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

### 3.3 Batch Regenerate All 80 Domain Examples

```bash
uv run python -c "
import importlib.util
from pathlib import Path

for py_file in sorted(Path('examples').glob('*/*.py')):
    spec = importlib.util.spec_from_file_location('module', py_file)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    domain = py_file.parent.name
    out_dir = Path('output') / domain
    if hasattr(mod, 'build_diagram'):
        mod.build_diagram(out_dir)
"
```

---

## 4. Test Suite Execution

Execute the comprehensive 227+ automated test suite using `uv run pytest`:

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

| Exit Code | Meaning |
|---|---|
| `0` | Success: diagram generation completed, layout solved, and files written. |
| `1` | Test failure or script execution error. |
| `2` | Cycle detected in layout constraints (`RuntimeError`). |
