# DOC-02: Fix Docker Service Names in Documentation

## Context

**Files to modify**: 5 documentation files
**Issue**: References to Docker service `db` should be `praxis-db`
**Related**: `docker-compose.yml` uses `praxis-db` as service name

## Requirements

Update the following files to use `praxis-db` instead of `db`:

1. **docs/getting-started/installation-production.md** (around line 27)
2. **docs/reference/troubleshooting.md** (around line 19)
3. **docs/reference/cli-commands.md** (around line 7)
4. **docs/development/contributing.md** (around line 23)
5. **docs/development/testing.md** (around line 13)

Search for all variations:

- `docker compose exec db`
- `docker-compose exec db`
- References to the `db` service in examples

Do NOT modify:

- Any other service names
- Any code files
- Database connection strings (those may use different naming)

## Acceptance Criteria

- [ ] All 5 files updated with correct service name
- [ ] No other unintended changes
- [ ] Grep for "exec db" returns no results in docs/
