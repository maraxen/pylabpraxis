# Agent Prompt: Fix Dashboard Axis Selector Reactivity

Examine `.agents/README.md` for development context.

**Status:** 🟢 Not Started
**Priority:** P2
**Difficulty:** Medium
**Batch:** [260109](./README.md)
**Backlog Reference:** [dataviz.md](../../backlog/dataviz.md#p2-dashboard-not-responding-to-selects)

---

## 1. The Task

The data visualization dashboard's X-axis and Y-axis selectors don't properly update the chart when changed. Users expect the visualization to reactively update when they select different axis configurations.

**Goal:** Fix the axis selector → chart data binding so the chart updates immediately when axis options are changed.

**User Value:** Users can dynamically explore their data by switching between different visualization perspectives.

---

## 2. Technical Implementation Strategy

**Root Cause Analysis:**

Looking at `DataVisualizationComponent`, the issue is likely in the `updateChart()` method which is called on `(ngModelChange)` but does nothing:

```typescript
updateChart() {
  // Triggers reactivity through signal updates
}
```

The `chartData` and `chartLayout` computed signals reference `this.xAxis` and `this.yAxis` directly, but these are plain properties, not signals. This breaks Angular's signal reactivity.

**Solution:**

Convert `xAxis` and `yAxis` to signals so the computed signals properly react to changes.

**Frontend Components:**

1. Convert `xAxis` and `yAxis` from plain properties to `signal<string>()`
2. Update template bindings to use signal values
3. Remove empty `updateChart()` method (no longer needed with proper reactivity)

**Data Flow:**

1. User selects new axis option
2. Signal updates trigger `chartData` and `chartLayout` recomputation
3. Plotly component receives new data and re-renders

---

## 3. Context & References

**Primary Files to Modify:**

| Path | Description |
|:-----|:------------|
| `praxis/web-client/src/app/features/data/data-visualization.component.ts` | Main component - convert axis properties to signals |

**Reference Files (Read-Only):**

| Path | Description |
|:-----|:------------|
| `praxis/web-client/src/app/shared/components/praxis-select/praxis-select.component.ts` | Select component API |

---

## 4. Constraints & Conventions

- **Commands**: Use `npm` for Angular tasks
- **Frontend Path**: `praxis/web-client`
- **State**: Use Angular Signals for reactive state
- **Testing**: Test axis selection behavior manually

**Implementation:**

```typescript
// Before
xAxis = 'timestamp';
yAxis = 'volumeTransferred';

// After
xAxis = signal('timestamp');
yAxis = signal('volumeTransferred');

// Update template bindings:
// [(ngModel)]="xAxis" → [ngModel]="xAxis()" (ngModelChange)="xAxis.set($event)"

// Update computed references:
chartData = computed(() => {
  // ...
  if (this.xAxis() === 'well') { ... }  // Note the () to read signal value
});
```

**Template Changes:**

```html
<!-- Before -->
<app-praxis-select
  [(ngModel)]="xAxis"
  (ngModelChange)="updateChart()">
</app-praxis-select>

<!-- After -->
<app-praxis-select
  [ngModel]="xAxis()"
  (ngModelChange)="xAxis.set($event)">
</app-praxis-select>
```

---

## 5. Verification Plan

**Definition of Done:**

1. Changing X-axis selector immediately updates the chart
2. Changing Y-axis selector immediately updates the chart
3. Chart title updates to reflect selected axes
4. No console errors during axis changes

**Verification Commands:**

```bash
cd praxis/web-client
npm run build
```

**Manual Verification:**
1. Navigate to Data Visualization page
2. Select different X-axis options (Time vs Well)
3. Verify chart type changes (line chart vs bar chart)
4. Select different Y-axis options (Volume, Cumulative, Temperature, Pressure)
5. Verify Y-axis values and title update correctly

---

## On Completion

- [ ] Commit changes with message: `fix(dataviz): fix axis selector reactivity with signals`
- [ ] Update backlog item status in `backlog/dataviz.md`
- [ ] Update `DEVELOPMENT_MATRIX.md` if applicable
- [ ] Mark this prompt complete in batch README and set status to 🟢 Completed

---

## References

- `.agents/README.md` - Development context and agent workflow
- `backlog/dataviz.md` - Full dataviz issue tracking
