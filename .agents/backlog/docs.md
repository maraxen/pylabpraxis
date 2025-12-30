# Documentation Backlog

**Area Owner**: All
**Last Updated**: 2025-12-29

---

## High Priority

### Docs Building

- [ ] Configure Sphinx/MkDocs for auto-generation
- [ ] API documentation from docstrings
- [ ] Component documentation
- [ ] Build pipeline (CI/CD integration)

### Demo Documentation

- [ ] `DEMO_SCRIPT.md` - Step-by-step demo walkthrough
- [ ] Talking points for each feature
- [ ] Screenshots / GIFs of key flows
- [ ] Troubleshooting guide for demo

### Architecture Updates

- [ ] Update `docs/architecture.md` with current state
- [ ] Add frontend architecture section
- [ ] Document WebSocket protocol
- [ ] Document state management patterns

---

## Medium Priority

### User Guides

- [ ] Getting started guide
- [ ] Protocol authoring guide
- [ ] Resource management guide
- [ ] Deck configuration guide

### Developer Guides

- [ ] Contributing guide
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

- [ ] "Hello World" protocol tutorial
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
| `docs/architecture.md` | Outdated | Update with current components |
| `docs/state_management.md` | Current | Review for accuracy |
| `docs/testing.md` | Current | Consolidate with tests/*.md |
| `docs/installation.md` | Minimal | Expand with full setup |
| `docs/quickstart.md` | Stub | Write proper quickstart |

---

## Documentation Standards

- Use "Praxis" (not "PyLabPraxis") in all new docs
- Use "machines" (not "instruments")
- Include code examples where applicable
- Keep docs close to code (inline comments, docstrings)
- Update docs as part of feature PRs
