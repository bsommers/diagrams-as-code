---
description: Always use uv for python environment, package management, and command execution
globs: ["**/*.py", "pyproject.toml", "Dockerfile"]
---

# Always Use `uv`

In this project, always use `uv` instead of standard `pip` or bare `python`:

- **Install/Sync:** `uv sync`
- **Add Dependency:** `uv add <package>` or `uv add --dev <package>`
- **Run Python Scripts:** `uv run python <script.py>`
- **Run Tests:** `uv run pytest`
- **Docker:** Use the multi-stage `uv` Dockerfile (`ghcr.io/astral-sh/uv:python3.12-bookworm-slim`)

## Conserve GitHub CI Minutes
Always run tests (`uv run pytest`) and artifact checks (`uv run python main.py`) locally before pushing or opening pull requests. Do not push intermediate or broken commits to remote.

