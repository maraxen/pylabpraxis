# DOC-03: Create CHANGELOG.md

## Context

**Create**: `CHANGELOG.md` at repository root
**Format**: Keep a Changelog (<https://keepachangelog.com/>)
**Current State**: No changelog exists

## Requirements

Create `CHANGELOG.md` with the following structure:

```markdown
# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- (placeholder for upcoming changes)

### Changed
- (placeholder for upcoming changes)

### Fixed
- (placeholder for upcoming changes)

## [v0.1-alpha] - 2026-01-XX

### Added
- Initial PyLabRobot integration for liquid handling automation
- Browser-mode SQLite database with OPFS persistence
- Asset management (machines and resources)
- Protocol execution and monitoring
- JupyterLite REPL integration
- WebSocket-based real-time updates

### Infrastructure
- Angular 19 frontend with Material Design
- FastAPI backend with PostgreSQL
- Playwright E2E test suite
```

Do NOT:

- Make up specific dates (use XX placeholder)
- Add changes not yet released
- Modify any other files

## Acceptance Criteria

- [ ] CHANGELOG.md exists at repository root
- [ ] Follows Keep a Changelog format
- [ ] Includes Unreleased section
- [ ] Documents v0.1-alpha initial features
