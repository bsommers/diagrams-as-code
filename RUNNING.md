# Diagrams as Code - How to Run

## Prerequisites & Installation

This project uses [`uv`](https://docs.astral.sh/uv/) for Python environment management, dependency resolution, and script execution.

### Install `uv` (if not already installed)
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Sync Environment
```bash
uv sync
```
This automatically provisions the virtual environment (`.venv/`) and installs `iiot-diagrams` in editable mode with development dependencies.

## Running Diagrams and Examples

Generate the primary reference architecture and living documentation:
```bash
uv run python main.py
```

Run specific example architectures:
```bash
uv run python examples/01_mockup_slide.py
uv run python examples/02_high_availability.py
uv run python examples/03_sparkplug_pipeline.py
```

## Running the Test Suite
```bash
uv run pytest
```

## Running with Docker
Build and run containerized diagram generation using the official Astral `uv` Docker image:
```bash
./docker-build-n-run.sh
```

Or via Docker Compose:
```bash
docker compose run --rm diagram-gen
```
