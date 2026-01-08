# Cleanup & Standards Backlog

**Area Owner**: All
**Last Updated**: 2026-01-02

---

## Pre-Merge Critical

### Naming Consistency

- [x] Rename "PyLabPraxis" to "Praxis" globally - **✅ Complete 2026-01-02**
  - [x] Documentation files (.md)
  - [x] Code comments
  - [ ] UI strings / branding
  - [ ] Package metadata
- [x] Unite wording: "machines" not "instruments" - **✅ Complete (0 occurrences found)**
  - [x] Frontend labels and text
  - [x] Backend variable names
  - [x] Documentation

### Codebase Standards Review

- [x] Remove unused imports (Ruff autofix) - **✅ Complete 2026-01-02**
- [x] Consistent code formatting (ruff) - **✅ Complete 2026-01-02**
- [x] Type annotations cleanup (ty check) - **✅ Initial pass complete 2026-01-02**
- [x] Remove dead code / commented blocks - **✅ Marked with TODO: [DEAD CODE]**
- [ ] **Frontend Linting**: Ensure ESLint/Prettier are running and passing (Angular).
- [ ] **DRY Enforcement**: Identify and refactor duplicated logic (Separation of Concerns).
- [ ] Consolidate duplicate utilities

### Pre-Merge Cleanup

- [ ] Remove development artifacts
- [x] Clean up console.log / print statements - **✅ Resolved 2026-01-01 (reduced to ~36)**
- [ ] Verify all TODO comments are tracked or resolved
- [ ] Update .gitignore if needed
- [x] Verify no secrets in codebase - **✅ Resolved 2026-01-01 (no hardcoded secrets)**
- [x] Remove legacy Sphinx files - **✅ All .rst files removed 2026-01-02**

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
