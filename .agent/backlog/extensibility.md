# Extensibility & Plugin Architecture Backlog

**Priority**: Long-term (v1.0+)
**Status**: Research Required

---

## Overview

This tracks the research and eventual implementation of an extensibility layer for Praxis. The scope covers multiple pillars with different risk/complexity profiles.

---

## Pillars

### 1. Labware Libraries (Community Submissions)

- **Format**: JSON/YAML-based definitions only (no code execution)
- **Risk**: Low — no code execution, purely declarative
- **UX**: Open submission, minimal approval needed
- **Browser/Desktop**: Both supported
- **Research Questions**:
  - [ ] Define schema for labware submissions
  - [ ] Community contribution workflow (GitHub PRs? Web form?)
  - [ ] Versioning and conflict resolution

### 2. Vendor Instrument Extensions

- **Format**: Python backends (drivers)
- **Risk**: Medium — code execution, but controlled
- **UX**: Manually approved by maintainers
- **Browser/Desktop**: Desktop/production only (requires backend)
- **Research Questions**:
  - [ ] API contract for backend adapters
  - [ ] Sandboxing/isolation approach
  - [ ] Certification/approval workflow

### 3. Theming

- **Format**: CSS/JSON theme files
- **Risk**: Low — styling only
- **UX**: User-installable
- **Browser/Desktop**: Both supported
- **Research Questions**:
  - [ ] Theme manifest format
  - [ ] Integration with Angular Material theming
  - [ ] Default theme variants (dark, high-contrast, etc.)

### 4. Application Mods (Advanced Extensions)

- **Format**: Sandboxed modules running in separate threads
- **Risk**: High — significant isolation work required
- **UX**: Power users / institutional deployments
- **Browser/Desktop**: Desktop/production only (likely); browser support TBD
- **Research Questions**:
  - [ ] Can Web Workers provide sufficient isolation?
  - [ ] What APIs would be exposed to mods?
  - [ ] Desktop-only vs browser-compatible?
  - [ ] Security model and permissions

---

## Next Steps

1. [ ] Research feasibility of each pillar
2. [ ] Prioritize based on user demand
3. [ ] Create task directories when ready to implement

---

## Related

- [ROADMAP.md](../ROADMAP.md) — Long-Term Vision section
- [protocol_reliability.md](./protocol_reliability.md) — Flight Checklists (related UX pattern)
