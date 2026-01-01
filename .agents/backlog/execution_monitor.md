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

- [ ] Add "Monitor" nav item to `unified-shell.component.ts`
  - Icon: `monitor_heart` or `assessment`
  - Route: `/app/monitor`
  - Position: After "Run" in sidebar
- [ ] Create `execution-monitor` feature module
- [ ] Create basic `ExecutionMonitorComponent` with placeholder content
- [ ] Add routes to `app.routes.ts`

### Phase 2: Active Runs Panel

**Goal**: Show currently running protocols with real-time updates

- [ ] Create `ActiveRunsPanelComponent`
  - Subscribe to `ExecutionService` for current run
  - Show status, progress, elapsed time
  - Click to view details
- [ ] Add visual indicators for run states:
  - RUNNING: Pulsing green indicator
  - QUEUED: Yellow/amber indicator
  - PREPARING: Blue spinner
- [ ] Show queue position for queued runs

### Phase 3: Run History Table

**Goal**: Paginated table of past runs

- [ ] Create `RunHistoryService` for API calls
- [ ] Create `RunHistoryTableComponent`
  - Columns: Protocol Name, Status, Started, Duration, Machine
  - Sortable columns
  - Pagination controls
- [ ] Add demo data support via `DemoInterceptor`
- [ ] Click row to navigate to run detail

### Phase 4: Filtering & Search

**Goal**: Filter runs by protocol, status, date

- [ ] Create `RunFiltersComponent`
  - Protocol dropdown (from available protocols)
  - Status multi-select (COMPLETED, FAILED, CANCELLED, RUNNING, QUEUED)
  - Date range picker
  - Search by run ID
- [ ] Implement query param synchronization
- [ ] Persist filter state in URL

### Phase 5: Run Detail View

**Goal**: Detailed view of a single run

- [ ] Create `RunDetailComponent`
  - Route: `/app/monitor/:runId`
  - Show full run info, parameters, machine used
  - Display deck configuration snapshot
  - Show execution timeline
  - Full log viewer with search
  - Output data visualization (if available)
- [ ] Add "Re-run with same parameters" action
- [ ] Add log download (JSON, TXT formats)

### Phase 6: Enhanced Visualization

**Goal**: Visual timeline and analytics

- [ ] Create `RunTimelineComponent`
  - Visual representation of run phases
  - Hover for phase details
- [ ] Add summary statistics to overview
  - Runs today/this week
  - Success rate
  - Average duration by protocol
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
