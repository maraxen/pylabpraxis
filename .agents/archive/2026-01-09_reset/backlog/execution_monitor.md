# Execution Monitor Enhancement

**Priority**: High
**Owner**: Frontend
**Created**: 2025-12-31
**Status**: Planning

---

## Overview

Enhance the execution monitor to provide comprehensive visibility into protocol runs - both active and historical. The monitor should be easily accessible from the sidebar and support filtering by protocol, status, and time range.

### Current State

```
┌─────────────────────────────────────────────────────────────┐
│ Sidebar                                                      │
│ ┌─────┐                                                      │
│ │ Run │ → /app/run (wizard) → /app/run/live (single run)    │
│ └─────┘                                                      │
│                                                              │
│ • Live dashboard only shows CURRENT run                      │
│ • No run history view                                        │
│ • No way to see past executions                              │
│ • Must navigate through wizard to reach monitor              │
└─────────────────────────────────────────────────────────────┘
```

### Target State

```
┌─────────────────────────────────────────────────────────────┐
│ Sidebar                                                      │
│ ┌─────────┐                                                  │
│ │ Run     │ → /app/run (wizard to start new run)            │
│ └─────────┘                                                  │
│ ┌─────────┐                                                  │
│ │ Monitor │ → /app/monitor (execution dashboard)            │
│ └─────────┘                                                  │
│                                                              │
│ Monitor Features:                                            │
│ • Active runs panel (real-time updates)                      │
│ • Run history table with pagination                          │
│ • Filter by: protocol, status, date range                    │
│ • Click-through to run details                               │
│ • Export logs and data                                       │
└─────────────────────────────────────────────────────────────┘
```

---

## Architecture

### Routes

```
/app/monitor                    → ExecutionMonitorComponent (overview)
/app/monitor/:runId             → RunDetailComponent (single run detail)
/app/monitor?protocol=:id       → Filtered by protocol
/app/monitor?status=:status     → Filtered by status
```

### Components

```
execution-monitor/
├── execution-monitor.component.ts      # Main dashboard
├── components/
│   ├── active-runs-panel.component.ts  # Real-time active runs
│   ├── run-history-table.component.ts  # Paginated history
│   ├── run-detail.component.ts         # Single run detail view
│   ├── run-filters.component.ts        # Filter controls
│   └── run-timeline.component.ts       # Visual timeline
├── models/
│   └── monitor.models.ts               # Monitor-specific models
├── services/
│   └── run-history.service.ts          # API calls for run history
└── execution-monitor.routes.ts         # Route definitions
```

### Data Flow

```
Backend API                     Frontend
─────────────────────────────────────────────────────────
GET /api/v1/protocols/runs      →  RunHistoryService
  ?status=RUNNING,COMPLETED       (paginated list)
  ?protocol_id=xxx
  ?limit=50&offset=0

GET /api/v1/protocols/runs/:id  →  Run detail with logs

WebSocket /ws/execution/:runId  →  Real-time updates
                                   (existing ExecutionService)
```

---

## Implementation Phases

### Phase 1: Sidebar & Basic Structure

**Goal**: Add Monitor to sidebar, create basic overview page

- [x] Add "Monitor" nav item to `unified-shell.component.ts` ✅ FIXED
  - Icon: `monitor_heart` or `assessment`
  - Route: `/app/monitor`
  - Position: After "Run" in sidebar
- [x] Create `execution-monitor` feature module ✅ FIXED
- [x] Create basic `ExecutionMonitorComponent` with placeholder content ✅ FIXED
- [x] Add routes to `app.routes.ts` ✅ FIXED

### Phase 2: Active Runs Panel

**Goal**: Show currently running protocols with real-time updates

- [x] Create `ActiveRunsPanelComponent` ✅ FIXED
  - Subscribe to `ExecutionService` for current run
  - Show status, progress, elapsed time
  - Click to view details
- [x] Add visual indicators for run states: ✅ FIXED
  - RUNNING: Pulsing green indicator
  - QUEUED: Yellow/amber indicator
  - PREPARING: Blue spinner
- [x] Show queue position for queued runs ✅ FIXED

### Phase 3: Run History Table

**Goal**: Paginated table of past runs

- [x] Create `RunHistoryService` for API calls ✅ FIXED
- [x] Create `RunHistoryTableComponent` ✅ FIXED
  - Columns: Protocol Name, Status, Started, Duration, Machine
  - Sortable columns
  - Pagination controls
- [x] Add demo data support via `DemoInterceptor` ✅ FIXED
- [x] Click row to navigate to run detail ✅ FIXED

### Phase 4: Filtering & Search

**Goal**: Filter runs by protocol, status, date

- [x] Create `RunFiltersComponent`
  - [x] Protocol dropdown (from available protocols) - **Multi-select added 2026-01-02**
  - [x] Status multi-select (COMPLETED, FAILED, CANCELLED, RUNNING, QUEUED)
  - [x] Horizontal scroll container for filters (Single-line flex, no wrapping) - **Implemented 2026-01-02**
  - Date range picker
  - Search by run ID
- [x] Implement query param synchronization (Handled by Filters Component)
- [ ] Persist filter state in URL

### Phase 5: Run Detail View

**Goal**: Detailed view of a single run

- [ ] Create `RunDetailComponent`
  - Route: `/app/monitor/:runId`
  - Show full run info, parameters, machine used
  - Display deck configuration snapshot
  - [x] Show execution timeline - **Implemented 2026-01-02**
  - Full log viewer with search
  - Output data visualization (if available)
- [ ] Add "Re-run with same parameters" action
- [ ] Add log download (JSON, TXT formats)

### Phase 6: Enhanced Visualization

**Goal**: Visual timeline and analytics

- [ ] Create `RunTimelineComponent` (Implemented inline in `RunDetailComponent` 2026-01-02)
  - [x] Visual representation of run phases
  - [ ] Hover for phase details
- [x] Add summary statistics to overview - **✅ Resolved 2026-01-01**
  - [x] Runs today/this week - `RunStatsPanelComponent` shows runs today + total
  - [x] Success rate - Shows percentage with completed/failed breakdown
  - [x] Average duration by protocol - Shows avg duration from run history
- [ ] Add mini-charts for trends

---

## API Requirements

### Existing Endpoints (verify/extend)

```
GET  /api/v1/protocols/runs
     Query params: status, protocol_id, limit, offset, sort_by, sort_order

GET  /api/v1/protocols/runs/:id
     Returns: Full run detail with logs

POST /api/v1/protocols/runs/:id/cancel
     Cancel a running/queued protocol
```

### Demo Mode Support

Add to `demo.interceptor.ts`:

- Mock run history data with various statuses
- Support filtering by status and protocol
- Pagination simulation

---

## UI/UX Considerations

### Layout Options

**Option A: Tab-based**

```
┌─────────────────────────────────────────────────────────┐
│ [Active Runs] [History] [Analytics]                      │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  Tab content here                                        │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

**Option B: Split view (Recommended)**

```
┌─────────────────────────────────────────────────────────┐
│ Active Runs (2)                             [Filters ▾] │
├─────────────────────────────────────────────────────────┤
│ ▶ Serial Dilution - RUNNING - 45%          [View]       │
│ ◷ Plate Prep - QUEUED - Position #2        [View]       │
├─────────────────────────────────────────────────────────┤
│ Run History                                              │
├─────────────────────────────────────────────────────────┤
│ Protocol        │ Status    │ Started      │ Duration   │
│ Serial Dilution │ COMPLETED │ 10:30 AM     │ 12m 34s    │
│ Plate Prep      │ FAILED    │ 09:15 AM     │ 5m 12s     │
│ ...             │           │              │            │
└─────────────────────────────────────────────────────────┘
```

### Status Colors

| Status | Color | Icon |
|--------|-------|------|
| RUNNING | Green | `play_circle` |
| QUEUED | Amber | `schedule` |
| PREPARING | Blue | `hourglass_empty` |
| COMPLETED | Gray/Green | `check_circle` |
| FAILED | Red | `error` |
| CANCELLED | Gray | `cancel` |
| PAUSED | Yellow | `pause_circle` |

### Responsive Behavior

- Desktop: Full table with all columns
- Tablet: Condensed table, collapsible filters
- Mobile: Card-based layout, stacked filters

---

## Files to Create/Modify

### Create

| File | Description |
|------|-------------|
| `src/app/features/execution-monitor/` | New feature module |
| `src/app/features/execution-monitor/execution-monitor.component.ts` | Main dashboard |
| `src/app/features/execution-monitor/components/active-runs-panel.component.ts` | Active runs |
| `src/app/features/execution-monitor/components/run-history-table.component.ts` | History table |
| `src/app/features/execution-monitor/components/run-detail.component.ts` | Run detail view |
| `src/app/features/execution-monitor/services/run-history.service.ts` | API service |
| `src/assets/demo-data/run-history.ts` | Extended mock data |

### Modify

| File | Description |
|------|-------------|
| `src/app/layout/unified-shell.component.ts` | Add Monitor nav item |
| `src/app/app.routes.ts` | Add monitor routes |
| `src/app/core/interceptors/demo.interceptor.ts` | Add run history mocks |

---

## Success Metrics

1. **Accessibility**: Monitor reachable in 1 click from sidebar
2. **Visibility**: Can see all runs (active + historical) in one view
3. **Filtering**: Can filter to specific protocol's runs
4. **Performance**: Table loads in <500ms for 100+ runs
5. **Real-time**: Active runs update without refresh

---

## Related Backlogs

- [ui-ux.md](./ui-ux.md) - General UI patterns
- [backend.md](./backend.md) - Protocol run API endpoints

---

## Notes

- Consider moving `LiveDashboardComponent` logic into new `RunDetailComponent`
- `ExecutionService` WebSocket handling can be reused
- Ensure demo mode fully supports monitor features
