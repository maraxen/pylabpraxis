# Task: Make Execution Monitor Filters Horizontally Scrollable

**Dispatch Mode**: ⚡ **Fast Mode** (CSS layout fix)

## Context

Read these files first:

- `.agents/DEVELOPMENT_MATRIX.md` - See P2 item "Execution Filters Container"
- `.agents/backlog/execution_monitor.md` - Phase 4 Filtering section

## Problem

Execution monitor filters overflow on narrow viewports. They need to be in a horizontally scrollable flex container.

## Implementation

1. Find filters component: `praxis/web-client/src/app/features/execution-monitor/components/run-filters.component.*`
2. Wrap all filter elements in a flex container
3. Add CSS:

   ```scss
   .filters-container {
     display: flex;
     flex-wrap: nowrap;
     gap: 1rem;
     overflow-x: auto;
     padding-bottom: 0.5rem; // Space for scrollbar
     
     // Hide scrollbar but keep functionality
     scrollbar-width: thin;
     &::-webkit-scrollbar {
       height: 4px;
     }
   }
   ```

4. Ensure filters don't wrap to new lines

## Testing

1. Run: `cd praxis/web-client && npm test -- --testPathPattern=execution-monitor`
2. Manual test: Resize browser to narrow width, verify horizontal scroll appears

## Definition of Done

- [ ] Filters are in horizontal flex row
- [ ] Horizontal scroll appears on narrow viewports
- [ ] Filters remain visually accessible
- [ ] Tests pass
- [ ] Update `.agents/backlog/execution_monitor.md` - Add "Horizontal scroll container ✅ Complete" to Phase 4
- [ ] Update `.agents/DEVELOPMENT_MATRIX.md` - Mark "Execution Filters Container" as complete

## Files to Modify

- `praxis/web-client/src/app/features/execution-monitor/components/run-filters.component.html`
- `praxis/web-client/src/app/features/execution-monitor/components/run-filters.component.scss`
