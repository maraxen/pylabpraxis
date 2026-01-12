# Agent Prompt: Data Visualization Axis Selects Fix

Examine `.agents/README.md` for development context.

**Status:** 🟢 Not Started
**Priority:** P2
**Batch:** [260112](./README.md)
**Backlog Reference:** [dataviz.md](../../backlog/dataviz.md)

---

## 1. The Task

Fix the data visualization dashboard so that the X-axis and Y-axis dropdown selects actually update the chart when changed. Currently, changing the axis selectors does not update the visualization.

**User Value:** Users can customize their data visualization by selecting different axes to analyze experiment data from multiple perspectives.

---

## 2. Technical Implementation Strategy

### Problem Analysis

In `DataVisualizationComponent` (lines 558-559, 588-598, 801-838, 840-868):
- `xAxis` and `yAxis` are signals
- `chartData` and `chartLayout` are computed signals that depend on these
- The selects use `[(ngModel)]` binding with `(ngModelChange)` to set the signal

Potential issues:
1. `PraxisSelectComponent` may not properly emit `ngModelChange`
2. The `[ngModel]` binding reads the signal but `(ngModelChange)` may not update it correctly
3. Plotly component may need explicit refresh after data change

### Frontend Components

1. **Debug `DataVisualizationComponent`**
   - Verify `xAxis.set()` and `yAxis.set()` are being called on selection change
   - Check if `chartData()` computed is recalculating
   - Verify Plotly component receives new data

2. **Fix binding pattern**
   - Current pattern (line 200-202): `[ngModel]="xAxis()" (ngModelChange)="xAxis.set($event)"`
   - This should work - verify `PraxisSelectComponent` emits correctly
   - Consider using `formControl` pattern if ngModel has issues

3. **Plotly refresh**
   - If computed updates but chart doesn't, may need to force Plotly redraw
   - Check `angular-plotly.js` documentation for reactive updates

### Data Flow

1. User selects new axis option
2. `PraxisSelectComponent` emits `ngModelChange`
3. `xAxis.set()` or `yAxis.set()` updates signal
4. `chartData()` and `chartLayout()` recompute
5. Plotly component receives new `[data]` and `[layout]` props
6. Chart re-renders

---

## 3. Context & References

**Primary Files to Modify:**

| Path | Description |
|:-----|:------------|
| `praxis/web-client/src/app/features/data/data-visualization.component.ts` | Main component (lines 195-212, 558-598, 801-868) |

**Reference Files (Read-Only):**

| Path | Description |
|:-----|:------------|
| `praxis/web-client/src/app/shared/components/praxis-select/praxis-select.component.ts` | Custom select component |
| `praxis/web-client/node_modules/angular-plotly.js/` | Plotly Angular wrapper |

---

## 4. Constraints & Conventions

- **Commands**: Use `npm` for Angular.
- **Frontend Path**: `praxis/web-client`
- **State**: Prefer Signals for Angular components.
- **Charting**: Using Plotly via `angular-plotly.js`

---

## 5. Verification Plan

**Definition of Done:**

1. The code compiles without errors:
   ```bash
   cd praxis/web-client && npm run build
   ```

2. Manual testing:
   - Navigate to Data Visualization page
   - Select a protocol run with data
   - Change X-axis from "Time" to "Well" → chart should switch to bar chart
   - Change Y-axis from "Volume Transferred" to "Cumulative Volume" → Y values should update
   - Change Y-axis to "Temperature" → chart should show temperature data

3. Chart updates are smooth without full page reload

---

## On Completion

- [ ] Commit changes with descriptive message
- [ ] Update backlog item status in `dataviz.md`
- [ ] Update DEVELOPMENT_MATRIX.md if applicable
- [ ] Mark this prompt complete in batch README

---

## References

- `.agents/README.md` - Environment overview
- [angular-plotly.js docs](https://github.com/plotly/angular-plotly.js)
