# E2E-VIZ-02: Visual Audit - Run Protocol Pages

## Context

**Routes**: `/app/run/*`
**Goal**: Visual quality audit for protocol execution UI

## Skill Integration

- `playwright-skill` - Screenshot capture
- `ui-ux-pro-max` - Visual criteria
- `designer.md` - Design evaluation

## Requirements

### Phase 1: Screenshot Capture

Capture at 1920x1080, 768x1024, 375x667:

1. `/app/run` - Protocol selection
2. Run setup wizard (each step)
3. Execution in progress view
4. Completed run summary
5. Error/stopped state

### Phase 2: Analysis

Focus areas for run protocol:

- **Progress indicators**: Clear, accessible
- **Status colors**: Semantic and consistent
- **Deck visualization**: Readable at all sizes
- **Control buttons**: Visible, accessible
- **Log display**: Readable, scrollable

### Phase 3: Report

Create `visual-audit-run-protocol.md` with:

- Screenshot inventory
- Critical/Important/Polish findings
- Specific recommendations

## Acceptance Criteria

- [ ] Full screenshot coverage
- [ ] Analysis documented
- [ ] Findings prioritized
