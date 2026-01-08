# Agent Prompt: 03_unique_name_parsing

Examine `.agents/README.md` for development context.

**Status:** ✅ Complete  
**Batch:** [260108](./README.md)  
**Backlog:** [chip_filter_standardization.md](../../backlog/chip_filter_standardization.md)  
**Priority:** P2

---

## Task

Implement logic to extract and display distinguishing parts of asset names in filter chip labels.

**Problem:** When many assets have similar names (e.g., "Hamilton Core96 Tip Rack", "Hamilton Core96 Deep Well Plate"), the filter chips truncate and show indistinguishable labels.

---

## Implementation Steps

### 1. Create Name Parsing Utility

Create `praxis/web-client/src/app/shared/utils/name-parser.ts`:

```typescript
/**
 * Extracts the unique/distinguishing part of asset names.
 * 
 * Examples:
 * - ["Hamilton Core96 Tip Rack", "Hamilton Core96 Plate"] -> ["Tip Rack", "Plate"]
 * - ["Corning 384 Well", "Corning 96 Well"] -> ["384 Well", "96 Well"]
 */
export function extractUniqueNameParts(names: string[]): Map<string, string> {
  // 1. Find common prefix across all names
  // 2. Find common suffix across all names
  // 3. Return the middle/unique portion for each name
  // 4. Handle edge cases (single name, no common parts)
}
```

### 2. Integrate with Filter Chips

Update `FilterChipComponent` or `ResourceFiltersComponent`:

```typescript
// In component that builds filter options
const uniqueLabels = extractUniqueNameParts(allAssetNames);
this.filterOptions = assets.map(a => ({
  value: a.accession_id,
  label: uniqueLabels.get(a.name) || a.name,
  fullName: a.name  // Keep full name for tooltips
}));
```

### 3. Add Tooltip for Full Name

Ensure chips show full name on hover:

```html
<app-filter-chip 
  [label]="option.label"
  [matTooltip]="option.fullName"
  ...
/>
```

### 4. Unit Tests

Create `praxis/web-client/src/app/shared/utils/name-parser.spec.ts`:

```typescript
describe('extractUniqueNameParts', () => {
  it('should extract unique suffix', () => {
    const names = ['Hamilton Core96 Tip Rack', 'Hamilton Core96 Plate'];
    const result = extractUniqueNameParts(names);
    expect(result.get('Hamilton Core96 Tip Rack')).toBe('Tip Rack');
    expect(result.get('Hamilton Core96 Plate')).toBe('Plate');
  });
  
  it('should handle names with no common parts', () => { /* ... */ });
  it('should handle single name', () => { /* ... */ });
});
```

---

## Context Files

| File | Purpose |
|:-----|:--------|
| [chip_filter_standardization.md](../../backlog/chip_filter_standardization.md) | Backlog tracking |
| [filter-chip.component.ts](file:///Users/mar/Projects/pylabpraxis/praxis/web-client/src/app/shared/components/filter-chip/filter-chip.component.ts) | Filter chip component |
| [resource-filters.component.ts](file:///Users/mar/Projects/pylabpraxis/praxis/web-client/src/app/features/assets/components/resource-filters/resource-filters.component.ts) | Resource filters |

---

## Project Conventions

- **Frontend Tests**: `cd praxis/web-client && npm test`

See [codestyles/typescript.md](../../codestyles/typescript.md) for conventions.

---

## On Completion

- [x] Update [chip_filter_standardization.md](../../backlog/chip_filter_standardization.md) - mark Unique Name Parsing complete
- [x] Update [DEVELOPMENT_MATRIX.md](../../DEVELOPMENT_MATRIX.md)
- [x] Mark this prompt complete in batch README

---

## References

- [.agents/README.md](../../README.md) - Environment overview
