# Contributing

Thanks for helping improve this project!

## Development setup (recommended: uv)

- Install uv
- Create/sync the environment:
  - `uv sync`
- Run the CLI locally (example):
  - `uv run python -m <your_package>.cli --help`

## Quality checks

- Lint/format:
  - `uv run ruff check .`
  - `uv run ruff format .`
- Tests:
  - `uv run pytest -q`

## Submitting changes

- Create a branch from `main`
- Keep PRs focused and small
- Add/adjust tests when behavior changes
- Make sure CI passes before requesting review
