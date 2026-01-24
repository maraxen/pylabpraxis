# SPLIT-03: Decompose data-visualization.component.ts

## Context

**File**: `src/app/features/data/data-visualization.component.ts`
**Current Size**: 932 lines
**Goal**: Extract chart components and data processing services

## Architecture Analysis

Likely contains:

1. **Chart Components**: Various visualization types
2. **Data Processing**: Transformations, aggregations
3. **Controls**: Filters, chart type selectors
4. **Export Functions**: Download, share

## Requirements

### Phase 1: Extract Services

1. **DataTransformService**: Data processing, aggregations
2. **ChartConfigService**: Chart configuration builders

### Phase 2: Extract Components

1. Chart-type specific components if multiple chart types inline
2. `data-viz-controls.component.ts` - Filters, selectors
3. `data-viz-legend.component.ts` - Legend if complex

### Phase 3: Verification

1. `npm run build` passes
2. `npm test` passes
3. Charts render correctly with sample data

## Acceptance Criteria

- [ ] Main component under 400 lines
- [ ] Data processing logic in services
- [ ] `npm run build` passes
- [ ] Commit: `refactor(data): split data-visualization into modules`

## Anti-Requirements

- Do NOT change chart rendering behavior
- Do NOT modify data formats
