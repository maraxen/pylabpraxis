# Documentation Backlog

**Area Owner**: All
**Last Updated**: 2026-01-01

---

## High Priority

### Build & Infrastructure

- [x] Configure MkDocs for documentation site
- [x] Enable Mermaid rendering in MkDocs - **✅ Configured in mkdocs.yml**
- [x] Enable Mermaid rendering in Angular App (ngx-markdown)
- [x] **Mermaid Theming**:
  - Debug diagram displays to be more consistent. - **✅ Complete**
  - Implement full light/dark mode toggling for diagrams. - **✅ Complete**
- [x] **2. API Documentation (mkdocstrings)**: ✅ Completed 2026-01-01 (Configured mkdocstrings plugin and migrated Service Layer reference)
- [x] **Sphinx Deprecation**: Removed all .rst files globally - **✅ Complete 2026-01-02**
- [ ] Build pipeline (CI/CD integration for MkDocs)

### Demo Documentation

- [ ] `DEMO_SCRIPT.md` - Step-by-step demo walkthrough
- [ ] Talking points for each feature
- [ ] Screenshots / GIFs of key flows
- [ ] Troubleshooting guide for demo

### Architecture Updates

- [x] Consolidate `docs/architecture.md` into `docs/architecture/*.md`
- [x] Document state management patterns (`docs/architecture/state-management.md`)
- [x] Document execution flow (`docs/architecture/execution-flow.md`)
- [x] Document Application Modes (Production, Browser, Demo)
- [ ] Document WebSocket protocol in detail
- [x] Add frontend component architecture diagrams - **✅ Added Mermaid diagrams to docs/architecture/**

---

## Medium Priority

### User Guides

- [x] Audit and rename legacy "PyLabPraxis" to "Praxis" in all documents - **✅ Complete 2026-01-02**
- [x] Getting started guide (Quickstart)
- [x] Protocol authoring guide - **✅ `docs/user-guide/protocols.md` (339 lines)**
- [ ] Resource management guide
- [ ] Deck configuration guide

### Developer Guides

- [x] Contributing guide - **✅ `CONTRIBUTING.md` (61 lines)**
- [ ] Local development setup
- [ ] Testing patterns (consolidate from tests/*.md)
- [ ] Code style guide

### API Documentation

- [ ] OpenAPI spec review and cleanup
- [ ] Example requests/responses
- [ ] Authentication documentation
- [ ] WebSocket events documentation

---

## Low Priority

### Tutorials

- [x] "Hello World" protocol tutorial - **✅ Created docs/tutorials/hello-world.md**
- [ ] Custom machine driver tutorial
- [ ] Data visualization tutorial

### Reference

- [ ] Glossary of terms
- [ ] FAQ
- [ ] Troubleshooting guide

---

## Existing Docs to Review/Update

| File | Status | Action |
|------|--------|--------|
| `docs/architecture/overview.md` | Current | Reviewed and updated with Modes |
| `docs/architecture.md` | Legacy | Consolidate and delete |
| `docs/state_management.md` | Legacy | Move to `architecture/` |
| `docs/testing.md` | Legacy | Move to `development/` |
| `docs/installation.md` | Current | Updated with Browser Mode |
| `docs/quickstart.md` | Current | Updated with Browser Mode |

---

## Documentation Standards

- Use "Praxis" (not "PyLabPraxis") in all new docs
- Use "machines" (not "instruments")
- Include code examples where applicable
- Keep docs close to code (inline comments, docstrings)
- Update docs as part of feature PRs
