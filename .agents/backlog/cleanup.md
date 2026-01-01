# Cleanup & Standards Backlog

**Area Owner**: All
**Last Updated**: 2025-12-29

---

## Pre-Merge Critical

### Naming Consistency

- [ ] Rename "PyLabPraxis" to "Praxis" globally - **⚠️ 32 refs in docs/**
  - [ ] Documentation files (.md)
  - [ ] Code comments
  - [ ] UI strings / branding
  - [ ] Package metadata
- [x] Unite wording: "machines" not "instruments" - **✅ Complete (0 occurrences found)**
  - [x] Frontend labels and text
  - [x] Backend variable names
  - [x] Documentation

### Codebase Standards Review

- [ ] Remove unused imports
- [ ] Consistent code formatting (ruff)
- [ ] Type annotations cleanup (ty check)
- [ ] Remove dead code / commented blocks
- [ ] **Frontend Linting**: Ensure ESLint/Prettier are running and passing (Angular).
- [ ] **DRY Enforcement**: Identify and refactor duplicated logic (Separation of Concerns).
- [ ] Consolidate duplicate utilities

### Pre-Merge Cleanup

- [ ] Remove development artifacts
- [ ] Clean up console.log / print statements - **⚠️ ~40 console.logs in app/**
- [ ] Verify all TODO comments are tracked or resolved
- [ ] Update .gitignore if needed
- [ ] Verify no secrets in codebase
- [ ] Remove legacy Sphinx files - **⚠️ 17 .rst files in docs/**

---

## Medium Priority

### UX/UI Review

- [ ] Consistency audit across all views
- [ ] Accessibility review (ARIA labels, keyboard nav)
- [ ] Error message clarity
- [ ] Empty state designs
- [ ] Loading state consistency

### Test Cleanup

- [ ] Remove or fix skipped tests
- [ ] Consolidate test utilities
- [ ] Update test documentation
- [ ] Remove obsolete test fixtures

### Dependencies

- [ ] Audit and update outdated packages
- [ ] Remove unused dependencies
- [ ] Security vulnerability scan

---

## Low Priority

### Performance

- [ ] Bundle size optimization (currently ~9.3MB uncompressed dist)
- [x] Lazy loading audit - **✅ `loadChildren` used on all feature routes**
- [ ] API response time audit

### Code Organization

- [ ] Review module boundaries
- [ ] Consolidate shared utilities
- [ ] Service layer consistency

---

## Files to Update for Rename

### High-Impact (User-Facing)

- `praxis/web-client/src/index.html` - Title
- `praxis/web-client/src/app/` - UI strings
- `README.md` - Project description
- `docs/` - All documentation

### Medium-Impact (Internal)

- `.agents/` - All markdown files
- `praxis/backend/` - Logging, comments
- `tests/` - Test documentation

### Low-Impact (Metadata)

- `pyproject.toml` - Package name (careful!)
- `package.json` - App name
