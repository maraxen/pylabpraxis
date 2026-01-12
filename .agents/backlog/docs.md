# Documentation Issues

**Created**: 2026-01-09
**Priority**: P2

---

## P2: API Docs Not Working

**Status**: Open
**Difficulty**: Medium

### Problem

API documentation pages are not working/rendering.

### Tasks

- [ ] Investigate API docs generation
- [ ] Fix rendering issues
- [ ] Verify all endpoints documented
- [ ] Test interactive examples if present

---

## P2: Keyboard Shortcut Column Formatting

**Status**: COMPLETE
**Difficulty**: Easy

### Problem

Keyboard shortcut column formatting is not working properly.

### Tasks

- [x] Identify affected docs page
- [x] Fix column/table formatting
- [x] Verify responsiveness

---

## P2: System Architecture Views

**Status**: Open
**Difficulty**: Medium

### Problem

Trying to expand the system architecture views does not work and instead yields just the text, not the actual visual view.

### Tasks

- [ ] Debug diagram rendering in docs
- [ ] Check if Mermaid/diagram library loading
- [ ] Fix expand/collapse functionality
- [ ] Test in different browsers

---

## P2: Dead Links

**Status**: COMPLETE
**Difficulty**: Easy

### Problem

Dead links exist in the documentation.

### Tasks

- [x] Run link checker across docs
- [x] Fix or remove dead links
- [x] Update any moved pages

---

## P2: Mode Separation in Architecture Docs

**Status**: Open
**Difficulty**: Medium

### Problem

We should have separate tabs for browser-lite and production mode in the backend/architecture section of the docs.

### Tasks

- [ ] Add tabbed view for mode-specific architecture
- [ ] Document browser-lite limitations
- [ ] Document production mode requirements
- [ ] Show diagram differences between modes

---

## P2: State Management Diagram

**Status**: COMPLETE
**Difficulty**: Easy

### Problem

State management overview diagram is improperly formatted for theming.

### Tasks

- [x] Fix diagram CSS for dark/light mode
- [x] Verify colors are theme-aware
- [x] Test in both themes

---

## P2: Execution Flow Diagram

**Status**: COMPLETE
**Difficulty**: Easy

### Problem

Execution flow diagram has formatting issues.

### Tasks

- [x] Identify specific formatting problems
- [x] Fix diagram layout/styling
- [x] Test rendering

---

## P2: Tutorial Updates

**Status**: Open
**Difficulty**: Medium

### Problem

The tutorial needs to be brought up to date.

### Tasks

- [ ] Review current tutorial steps
- [ ] Update screenshots if UI changed
- [ ] Verify all described features still work
- [ ] Test tutorial flow end-to-end

---

## P2: Documentation Accuracy Audit

**Status**: Open
**Difficulty**: Medium

### Problem

Need to verify all docs are up to date.

### Tasks

- [ ] Create checklist of all doc pages
- [ ] Review each page for accuracy
- [ ] Flag outdated content
- [ ] Update or remove stale information

---

## Note: Production Mode

Production mode still requires a lot of validation work. This should be documented clearly in the production setup guide, listing what has been tested vs what still needs validation.
