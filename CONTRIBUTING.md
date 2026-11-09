# Contributing

Full guidelines: [docs/development.md](docs/development.md). Agent rules: [AGENTS.md](AGENTS.md).

1. Use `uv` for everything (`uv sync`, `uv run pytest`); never bare `pip` or `python`.
2. Keep the core engine pure standard library; add no runtime dependencies.
3. Before pushing, run `uv run pytest`, `uv run python main.py`, `uv run python tools/generate_icons.py --check`, and confirm `git diff --exit-code -- output/ icons/ README.md docs/` is clean (after committing your changes).
4. Update docs and `docs/CHANGELOG.md` in the same change.
