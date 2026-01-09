# Agent Prompt: Add Sample Data Seeding for Data Visualization

Examine `.agents/README.md` for development context.

**Status:** 🟢 Not Started
**Priority:** P2
**Difficulty:** Medium
**Batch:** [260109](./README.md)
**Backlog Reference:** [dataviz.md](../../backlog/dataviz.md#p2-sample-data-seeding)

---

## 1. The Task

New users see empty visualizations in the Data Visualization page because there's no protocol run history. The app should ship with sample/demo data from simulated runs.

**Goal:** Seed the browser database with sample protocol run data that demonstrates the visualization capabilities.

**User Value:** New users immediately see meaningful visualizations and understand the data analysis capabilities.

---

## 2. Technical Implementation Strategy

**Current State:**

The `DataVisualizationComponent` already generates mock data dynamically based on loaded protocols (see `generateMockRuns` and `generateSeededTransferData`). The issue is that this data is ephemeral and may not persist.

**Options:**

1. **Browser DB Seeding**: Add sample runs to SQLite on first load
2. **Enhanced Mock Data**: Improve the existing mock data generation
3. **Demo Mode Flag**: Show demo data when no real data exists

**Recommended Approach:**

Since mock data generation already exists, ensure it:
1. Creates meaningful, representative data
2. Covers various scenarios (complete runs, failed runs, running experiments)
3. Includes diverse well configurations
4. Persists in browser DB for return visits

**Implementation Steps:**

1. Create seed data service for browser mode
2. Generate representative protocol runs on first app load
3. Store in browser SQLite via existing services
4. Show seed data in Data Visualization

---

## 3. Context & References

**Primary Files to Modify:**

| Path | Description |
|:-----|:------------|
| `praxis/web-client/src/app/features/data/data-visualization.component.ts` | Enhance mock data or integrate with seed service |
| `praxis/web-client/src/app/core/services/sqlite.service.ts` | Add seed data loading |

**Reference Files (Read-Only):**

| Path | Description |
|:-----|:------------|
| `praxis/web-client/src/app/features/protocols/services/protocol.service.ts` | Protocol data access |
| `praxis/web-client/src/app/core/services/app-init.service.ts` | Initialization hooks |

---

## 4. Constraints & Conventions

- **Commands**: Use `npm` for Angular tasks
- **Frontend Path**: `praxis/web-client`
- **State**: Use Angular Signals
- **Storage**: Use existing SQLite service for browser mode

**Sample Data Requirements:**

```typescript
interface SampleRun {
  id: string;
  protocolName: string;
  protocolId: string;
  status: 'completed' | 'running' | 'failed';
  startTime: Date;
  endTime?: Date;
  wellData: WellDataPoint[];
}

interface WellDataPoint {
  well: string;  // A1, A2, etc.
  timestamp: Date;
  volume: number;
  temperature?: number;
  // Additional metrics
}
```

**Seed Data Should Include:**

1. **Simple Transfer Protocol** - 12 wells, completed successfully
2. **Serial Dilution Protocol** - 96 wells, completed successfully
3. **Plate Replication** - 96 wells, failed mid-run (demonstrates error state)
4. **Active Experiment** - Status "running" (demonstrates live updates)

**Implementation Sketch:**

```typescript
// In a new seed-data.service.ts or integrated into sqlite.service.ts

async seedDemoData(): Promise<void> {
  const hasData = await this.checkExistingRuns();
  if (hasData) return;

  const sampleRuns = this.generateSampleRuns();
  for (const run of sampleRuns) {
    await this.saveProtocolRun(run);
    await this.saveWellData(run.id, run.wellData);
  }
}

private generateSampleRuns(): SampleRun[] {
  return [
    {
      id: 'demo-run-001',
      protocolName: 'Simple Transfer',
      protocolId: 'demo-protocol-001',
      status: 'completed',
      startTime: new Date(Date.now() - 2 * 60 * 60 * 1000), // 2 hours ago
      endTime: new Date(Date.now() - 1.5 * 60 * 60 * 1000),
      wellData: this.generateWellData(12)
    },
    // ... more sample runs
  ];
}
```

---

## 5. Verification Plan

**Definition of Done:**

1. Data Visualization shows sample data on first load
2. Sample data includes various run statuses
3. Charts render with meaningful data
4. Sample data persists across browser sessions
5. Real data takes precedence when available

**Verification Commands:**

```bash
cd praxis/web-client
npm run build
```

**Manual Verification:**
1. Clear browser storage (new user scenario)
2. Navigate to Data Visualization
3. Verify sample runs appear in run history
4. Verify charts show data
5. Refresh page - verify data persists
6. Run a real protocol - verify it appears alongside demo data

---

## On Completion

- [ ] Commit changes with message: `feat(dataviz): add sample data seeding for new users`
- [ ] Update backlog item status in `backlog/dataviz.md`
- [ ] Update `DEVELOPMENT_MATRIX.md` if applicable
- [ ] Mark this prompt complete in batch README and set status to 🟢 Completed

---

## References

- `.agents/README.md` - Development context and agent workflow
- `backlog/dataviz.md` - Full dataviz issue tracking
