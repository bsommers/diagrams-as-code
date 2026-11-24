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
- `examples/main_architecture.svg`
- `examples/main_architecture.png`
- `examples/main_architecture_README.md`

### 3.2 Run Any Domain Architecture Example

```bash
# Run a specific cloud architecture example
uv run python examples/cloud/01_simple_vpc_web.py

# Run an AI pipeline example
uv run python examples/ai/01_simple_rag_pipeline.py

# Run a cybersecurity Zero-Trust architecture example
uv run python examples/cybersecurity/09_iam_federation_saml_oidc.py
```

The four top-level `examples/0*.py` scripts are the original IIoT reference diagrams and the curves-and-fillets demo:

```bash
uv run python examples/01_mockup_slide.py
uv run python examples/02_high_availability.py
uv run python examples/03_sparkplug_pipeline.py
uv run python examples/04_curves_and_fillets.py
```

Every example writes its SVG, PNG and BOM next to the script (for instance `examples/cloud/01_simple_vpc_web.svg`); there is no separate `output/` directory.

### 3.3 Batch Regenerate the Gallery

```bash
uv run diagrams-as-code render examples --format svg,png,bom
```

This scans `examples/` for every script that defines `diagram()`, renders each
into its domain subdirectory under `examples/`, and writes all three formats
(the default `--format` is `svg,bom`; `png` is added explicitly here since
PNG bytes are excluded from the batch's tracked comparison but useful to look
at locally).

### 3.4 The `diagrams-as-code` Command

Installed as a console script (`uv run diagrams-as-code ...`), and also
runnable as `uv run python -m diagrams_as_code ...`.

**`render PATH... [--json] [--out DIR] [--format FORMATS] [--theme THEME] [--interactive | --no-interactive] [--layout MODE] [--direction DIR] [--layout-file FILE] [--debug]`**

Renders one or more scripts into `--out` (default: beside each script), or every `diagram()`-defining script found by
recursively scanning a directory. `--format` is a comma-separated subset of
`svg,png,pdf,bom`; it defaults to `svg,bom` because those two are the
byte-comparable, git-tracked artifacts — PNG bytes vary slightly by backend
(Cairo vs. the pure-Python fallback), so they're opt-in. `pdf` writes a
vector PDF beside the SVG; it needs no extra software and is also opt-in. `--theme`,
`--layout`, `--direction`, and `--layout-file` override the script's own
`Diagram(...)` settings for this render only. `--debug` prints full
tracebacks for scripts that fail to load or render.

**`lint PATH... [--json] [--ignore KIND[,KIND]] [--quiet] [--layout MODE] [--direction DIR] [--layout-file FILE] [--debug]`**

Lays out each diagram and reports visual defects (a line through a node, overlapping labels, text that does not fit), one per line as `script: kind: detail`. Exits `1` if anything is found. With `--json`: `{"checked": N, "findings": [{"file", "kind", "detail", "ids"}], "failed": [{"file", "code", "message", "line"?}]}`, where `ids` are the ids of the elements involved. Example: `uv run diagrams-as-code lint examples`.

**`layout export SCRIPT [-o FILE] [--layout MODE] [--direction DIR] [--layout-file FILE] [--debug]`**

Runs a script's `diagram()`, solves it, and writes every element's resolved
position to a JSON layout file (default: `SCRIPT.layout.json`). See
`docs/how-to.md` for the layout-file editing workflow.

**`themes [--json]`**

Lists every built-in theme name, one per line (`{"themes": [...]}` with `--json`).

**`icons [--domain DOMAIN] [--json]`**

Lists every built-in icon as `name<TAB>domain<TAB>description`; `--domain`
filters to one domain (`{"icons": [{"name", "domain", "description"}]}` with `--json`).

**`api [NAME] [--json]`**

The public Python API as a reference: every name in `diagrams_as_code.__all__` plus the `plot`, `draft`, `sequence` and `gantt` kits, each with kind, signature and a one-line summary. `NAME` is a class, function, kit module (`gantt`) or substring; a class also lists its methods. Exits `1` if nothing matches. The JSON is the same document the MCP `describe_api` tool returns.

**`examples [--domain DOMAIN] [--dir DIR] [--json]`**

Without `--domain`, lists the gallery's domains and counts; with it, lists `DOMAIN/NAME<TAB>title`. Reads `./examples`, else the checkout's.

**`source EXAMPLE [--dir DIR]`**

Prints an example's script (`DOMAIN/NAME`, e.g. `finance/candlestick_chart`; the numeric prefix is optional). Exit `1` if there is no such example.

**`--json` contract:** `render`, `lint`, `themes`, `icons`, `api` and `examples` print exactly one JSON document on stdout and nothing else; the human text is unchanged without the flag. Errors and anything a script prints go to stderr. `render --json` prints `{"written": [{"script", "format", "file"}], "failed": [...]}`.

**`mcp [--root DIR] [--timeout SECONDS] [--memory-mb MB]`**

Serves render, lint and listing tools over stdio for MCP clients (see [§7](#7-driving-it-from-an-mcp-client)). `--timeout` (default 60) and `--memory-mb` (default 2048) limit each script run.

**Exit codes:** `0` success; `1` findings or failures (a script failed to load, render or write, `lint` found a defect, a named example or API name does not exist; each failure is reported and the command continues with the rest); `2` a command-line usage error (unknown flag, missing subcommand).

---

## 4. Test Suite Execution

Execute the automated test suite using `uv run pytest`:

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

## 7. Driving it from an MCP client

`diagrams-as-code mcp [--root DIR]` serves these tools over stdio (JSON-RPC, MCP 2025-06-18). Each declares an `inputSchema` (descriptions, enums) and, for object results, an `outputSchema`; `tools/list` returns them.

| Tool | Arguments | Returns |
|---|---|---|
| `render_source` | `source`; optional `formats` (`svg`,`png`,`pdf`,`bom`), `theme`, `inline`, `out`, `name` | `{stem, written[], svg?, svg_truncated?, svg_chars?, bom?}`. SVG is inline by default when `out` is omitted (cut at 100,000 characters); `png`/`pdf` need `out`. |
| `lint_source` | `source`; optional `ignore` | `{checked, count, findings:[{kind, detail, ids}]}` |
| `get_example` | `domain`, `name` | `{domain, name, title, script, source, svg?}` |
| `list_domains` | none | `{total, domains:[{domain, count, titles}]}` |
| `describe_api` | optional `name` | `{total, returned, truncated, entries:[{name, module, kind, signature, summary, members?}]}` |
| `capabilities` | optional `category` | `{version, total, capabilities:[{id, title, category, status, verification}]}` |
| `render` | `path`; optional `out`, `formats`, `theme` | `{written[], failed[]}` (files under the root) |
| `lint` | `path`; optional `ignore` | `{checked, findings[], failed[]}` (files under the root) |
| `list_examples`, `list_themes`, `list_icons` | optional `path`/`domain` | lists |

An agent with no file-write tool starts with `describe_api` and `get_example`, then calls `render_source` with script text it wrote. `source` is arbitrary Python: it runs in the sandbox below, not in the server process. Minimal exchange (one JSON message per line):

```json
{"jsonrpc":"2.0","id":1,"method":"initialize","params":{}}
{"jsonrpc":"2.0","method":"notifications/initialized"}
{"jsonrpc":"2.0","id":2,"method":"tools/call","params":{"name":"render_source","arguments":{"source":"from diagrams_as_code import Diagram\ndef diagram():\n    d = Diagram('Hello')\n    d.shape('A', id='a')\n    return d\n"}}}
```

The reply's `structuredContent.svg` holds the SVG. **Errors** come back with `isError: true` and `{"error": {"code", "message", "line"?}}` as both text and `structuredContent`. `line` is the line of the submitted script that raised. Codes: `invalid_argument` (bad or missing argument, unknown key, value outside an enum), `path_outside_root`, `not_found`, `no_scripts`, `script_error` (the script raised, exited, or defined no `diagram()`), `timeout`, `resource_limit` (killed for CPU or memory), `sandbox_failure`, `output_error` (unsafe or unwritable output) and `internal_error`. A missing required argument is a JSON-RPC `-32602` error instead.

The path-based tools map onto the CLI (`render`, `lint`, `themes`, `icons`) and the Python API (`render_all`, `audit_findings`); `render` writes beside the script unless `out` is given. Because rendering imports the script, which is arbitrary Python, all script and output paths are confined to `--root` (default: the current directory). Each script runs in a resource-limited child process (`diagrams_as_code.sandbox`): a wall-clock `--timeout` kills the whole process group, CPU and memory caps apply on POSIX (`--memory-mb`; address space is only enforced on Linux), stdin is closed, stdout is discarded, stderr is capped and the environment is scrubbed. That limits resources and protects the protocol stream; it is not file or network isolation, so run it only over scripts you trust, or in a container.

```json
{"mcpServers": {"diagrams-as-code": {"command": "uv", "args": ["run", "diagrams-as-code", "mcp"]}}}
```
