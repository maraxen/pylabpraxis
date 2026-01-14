# Agent Prompt: Workcell View Models

Examine `.agents/README.md` for development context.

**Status:** 🟢 Completed
**Priority:** P1
**Batch:** [260115](README.md)
**Difficulty:** Low
**Dependencies:** None
**Backlog Reference:** WCX-001-IMPL (P0.1)

---

## 1. The Task

Create TypeScript interfaces for the new workcell view as defined in Phase 0.1 of the [Workcell Implementation Plan](../artifacts/workcell_implementation_plan.md). This foundation phase is critical for ensuring type safety across the new feature.

## 2. Technical Implementation Strategy

**(From workcell_implementation_plan.md)**

**Frontend Components:**

- Create `src/app/features/workcell/models/workcell-view.models.ts` with the following interfaces:

```typescript
export interface WorkcellGroup {
  workcell: Workcell | null;
  machines: MachineWithRuntime[];
  isExpanded: boolean;
}

export interface MachineWithRuntime extends Machine {
  connectionState: 'connected' | 'disconnected' | 'connecting';
  lastStateUpdate?: Date;
  stateSource: 'live' | 'simulated' | 'cached' | 'definition';
  currentRun?: ProtocolRunSummary;
  alerts: MachineAlert[];
}

export interface MachineAlert {
  severity: 'info' | 'warning' | 'error';
  message: string;
  resourceId?: string;
}

export interface ProtocolRunSummary {
  id: string;
  protocolName: string;
  currentStep: number;
  totalSteps: number;
  progress: number;
  estimatedRemaining?: number;
}
```

**Backend/Services:**

- No backend changes required for this task.

**Data Flow:**

- These models will be used by `WorkcellViewService` to transform raw backend data into view-optimized structures.

## 3. Context & References

**Primary Files to Modify:**

| Path | Description |
|:-----|:------------|
| `src/app/features/workcell/models/workcell-view.models.ts` | New file for workcell-specific models |
| `src/app/features/assets/models/asset.models.ts` | Update if necessary to export specific base types |

**Reference Files (Read-Only):**

| Path | Description |
|:-----|:------------|
| `.agents/artifacts/workcell_implementation_plan.md` | Implementation plan source |
| `src/app/features/assets/models/machine.models.ts` | Existing Machine model reference |

## 4. Constraints & Conventions

- **Commands**: Use `npm` for Angular.
- **Frontend Path**: `praxis/web-client`
- **Typing**: Ensure strict typing; avoid `any`.
- **Linting**: Run `eslint` or equivalent before committing.

## 5. Verification Plan

**Definition of Done:**

1. The code compiles without errors.
2. The following tests pass:

   ```bash
   npm run build
   ```

3. Models are exported and accessible for other components.

---

## On Completion

- [x] Commit changes with descriptive message referencing the backlog item
- [x] Update backlog item status
- [x] Update DEVELOPMENT_MATRIX.md if applicable
- [x] Mark this prompt complete in batch README and set the status in this prompt document to 🟢 Completed

---

## References

- `.agents/README.md` - Environment overview
- `TECHNICAL_DEBT.md` - Known issues
