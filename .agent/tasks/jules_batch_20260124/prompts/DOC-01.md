# DOC-01: Update CONTRIBUTING.md with uv Commands

## Context

**File**: `CONTRIBUTING.md` (repository root)
**Related**: `README.md` uses `uv run` commands
**Current State**: CONTRIBUTING.md uses deprecated `make` commands

## Requirements

1. Replace all `make` commands with their `uv` equivalents:
   - `make test` → `uv run pytest`
   - `make lint` → `uv run ruff check .`
   - `make typecheck` → `uv run mypy .`
   - `make docs` → `uv run mkdocs build` (if applicable)
   - `make format` → `uv run ruff format .`

2. Ensure consistency with README.md command patterns

3. Preserve all other content and formatting

4. Do NOT modify any other files

## Acceptance Criteria

- [ ] All `make` commands replaced with `uv run` equivalents
- [ ] Commands are syntactically correct
- [ ] Document formatting is preserved
- [ ] No unintended content changes
