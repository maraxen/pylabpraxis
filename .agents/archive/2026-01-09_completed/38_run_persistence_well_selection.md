# Agent Prompt: 38_run_persistence_well_selection

Examine `.agents/README.md` for development context.

**Status:** 🟢 Not Started
**Batch:** [260109](./README.md)
**Backlog:** [run_protocol_workflow.md](../../backlog/run_protocol_workflow.md)
**Priority:** P2 - High (Core workflow completion)

---

## Task

Complete the run protocol workflow with three interconnected features:

1. **Run Persistence (IndexedDB)** - Save browser-mode runs so they appear in Execution Monitor
2. **Name & Notes Pass-Through** - Use user-entered run name/notes instead of auto-generated
3. **Well Selection Step** - Add conditional stepper step for protocols requiring well selection

---

## Context Files

| File | Purpose |
|:-----|:--------|
| [run-protocol.component.ts](../../../praxis/web-client/src/app/features/run-protocol/run-protocol.component.ts) | Main wizard with stepper steps |
| [execution.service.ts](../../../praxis/web-client/src/app/features/run-protocol/services/execution.service.ts) | Run execution and state management |
| [sqlite.service.ts](../../../praxis/web-client/src/app/core/services/sqlite.service.ts) | IndexedDB persistence layer |
| [run-history.service.ts](../../../praxis/web-client/src/app/features/execution-monitor/services/run-history.service.ts) | Execution Monitor data source |
| [well-selector-dialog.component.ts](../../../praxis/web-client/src/app/shared/components/well-selector-dialog/well-selector-dialog.component.ts) | Well selection UI |
| [schema.sql](../../../praxis/web-client/src/assets/db/schema.sql) | Database schema reference |

---

## Part 1: Run Persistence & Name/Notes

### Problem

1. Browser-mode runs are not saved to IndexedDB - they don't appear in Execution Monitor
2. User-entered run name and notes are ignored - auto-generated name is used instead

### Current Flow (Broken)

```
User enters name/notes → startRun() ignores them → generates "Protocol - Date"
startBrowserRun() → creates in-memory state only → no IndexedDB record
Execution Monitor → queries IndexedDB → no runs found
```

### Target Flow

```
User enters name/notes → startRun() uses them → passes to service
startBrowserRun() → creates IndexedDB record → updates status on complete/fail
Execution Monitor → queries IndexedDB → shows run history
```

### Implementation

#### 1.1 Update `run-protocol.component.ts` - `startRun()`

**Current** (line ~956):


```typescript
const runName = `${protocol.name} - ${new Date().toLocaleString()}`;
```


**Change to**:

```typescript
const runName = this.runNameControl.value?.trim() || `${protocol.name} - ${new Date().toLocaleString()}`;
const runNotes = this.runNotesControl.value?.trim() || '';

this.executionService.startRun(
  protocol.accession_id,
  runName,
  params,
  this.store.simulationMode(),
  runNotes  // Add notes parameter
)
```

#### 1.2 Update `execution.service.ts` - `startRun()` signature


**Current**:

```typescript
startRun(
  protocolId: string,
  runName: string,
  parameters?: Record<string, any>,
  simulationMode: boolean = true
): Observable<{ run_id: string }>

```

**Change to**:

```typescript
startRun(
  protocolId: string,
  runName: string,
  parameters?: Record<string, any>,
  simulationMode: boolean = true,
  notes?: string
): Observable<{ run_id: string }>
```


#### 1.3 Update `startBrowserRun()` - Save to IndexedDB

**Add** after creating `runId`:

```typescript
// Persist run to IndexedDB
const runRecord = {
  accession_id: runId,
  protocol_definition_accession_id: protocolId,
  name: runName,
  status: 'QUEUED',
  created_at: new Date().toISOString(),
  input_parameters_json: JSON.stringify(parameters || {}),
  properties_json: JSON.stringify({ notes, simulation_mode: true })
};

this.sqliteService.createProtocolRun(runRecord).subscribe({
  error: (err) => console.warn('[ExecutionService] Failed to persist run:', err)
});

```

#### 1.4 Update `executeBrowserProtocol()` - Update status on complete/fail

**On success** (after `this.addLog('[Browser Mode] Execution completed successfully.')`):


```typescript
// Update run status in IndexedDB
this.sqliteService.updateProtocolRunStatus(runId, 'COMPLETED').subscribe();
```

**On error** (in catch block):

```typescript
// Update run status in IndexedDB  
this.sqliteService.updateProtocolRunStatus(runId, 'FAILED').subscribe();

```

#### 1.5 Fix `SqliteService.createProtocolRun()` to match schema

The `protocol_runs` table schema requires `top_level_protocol_definition_accession_id` NOT NULL.

**Update** `createProtocolRun()`:

```typescript
public createProtocolRun(run: any): Observable<any> {
    return this.db$.pipe(
        map(db => {
            const stmt = db.prepare(`
                INSERT INTO protocol_runs 
                (accession_id, top_level_protocol_definition_accession_id, name, status, 
                 created_at, updated_at, input_parameters_json, properties_json)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            `);
            const now = new Date().toISOString();
            stmt.run([
                run.accession_id,
                run.protocol_definition_accession_id,
                run.name,
                run.status || 'QUEUED',
                run.created_at || now,
                now,
                run.input_parameters_json || null,
                run.properties_json || null
            ]);
            stmt.free();
            this.saveToStore(db);  // Persist to IndexedDB
            return run;
        })
    );
}
```

---

## Part 2: Well Selection Step (Conditional)

### Problem

Protocols requiring well selection (e.g., `selective_transfer`) have no UI for users to specify which wells to use.

### Design Decisions

1. **Separate Stepper Step** - Add new step after Asset Selection, before Deck Setup
2. **Conditional Visibility** - Only show if protocol has well-selection parameters

3. **Auto-detect Plate Type** - Derive 96/384 from selected plate assets
4. **Auto-refresh Execution Monitor** - Refresh after run completes

### Implementation

#### 2.1 Add `wellsFormGroup` and state

**In** `run-protocol.component.ts`:

```typescript
wellsFormGroup = this._formBuilder.group({ 
  valid: [true]  // Optional by default, validated when wells required
});

// Well selection state
wellSelectionRequired = computed(() => {
  const protocol = this.selectedProtocol();
  return protocol?.parameters?.some(p => this.isWellSelectionParameter(p)) ?? false;
});

wellSelections = signal<Record<string, string[]>>({});
```

#### 2.2 Add `isWellSelectionParameter()` heuristic

```typescript
private isWellSelectionParameter(param: ParameterDefinition): boolean {
  const name = (param.name || '').toLowerCase();
  const typeHint = (param.type_hint || '').toLowerCase();
  
  // Check name patterns
  const wellNamePatterns = ['well', 'wells', 'source_wells', 'target_wells', 'well_ids'];
  if (wellNamePatterns.some(p => name.includes(p))) {
    return true;
  }
  
  // Check ui_hint if available
  if (param.ui_hint?.type === 'well_selector') {
    return true;

  }
  
  return false;
}
```

#### 2.3 Add Well Selection Step to Template

**Insert after Asset Selection step** (after line ~352):

```html
<!-- Step 5: Well Selection (Conditional) -->
<mat-step [stepControl]="wellsFormGroup" *ngIf="wellSelectionRequired()">
  <ng-template matStepLabel>
    <span data-tour-id="run-step-label-wells">Select Wells</span>
  </ng-template>
  <div class="h-full flex flex-col p-6" data-tour-id="run-step-wells">
    <div class="flex-1 overflow-y-auto">
      <h3 class="text-xl font-bold text-sys-text-primary mb-6 flex items-center gap-3">
        <div class="w-8 h-8 rounded-lg bg-primary/20 flex items-center justify-center text-primary">
          <mat-icon>grid_on</mat-icon>
        </div>
        Well Selection
      </h3>
      
      <p class="text-sys-text-secondary mb-6">
        This protocol requires you to specify which wells to use. Click each parameter below to select wells.
      </p>
      
      @for (param of getWellParameters(); track param.name) {
        <div class="mb-6 p-4 bg-surface-variant rounded-xl">
          <div class="flex items-center justify-between mb-2">
            <span class="font-medium">{{ param.name }}</span>
            <span class="text-sm text-sys-text-tertiary">{{ param.description }}</span>
          </div>
          <button mat-stroked-button (click)="openWellSelector(param)" class="w-full !justify-start">
            <mat-icon class="mr-2">grid_on</mat-icon>
            {{ getWellSelectionLabel(param.name) }}
          </button>
        </div>
      }
    </div>
    
    <div class="mt-6 flex justify-between border-t border-[var(--theme-border)] pt-6">
      <button mat-button matStepperPrevious class="!text-sys-text-secondary">Back</button>
      <button mat-flat-button color="primary" matStepperNext 
              [disabled]="!areWellSelectionsValid()" 
              class="!rounded-xl !px-8 !py-6">
        Continue
      </button>
    </div>
  </div>
</mat-step>
```

#### 2.4 Add Well Selector Methods

```typescript
import { MatDialog } from '@angular/material/dialog';
import { WellSelectorDialogComponent, WellSelectorDialogData, WellSelectorDialogResult } 
  from '@shared/components/well-selector-dialog/well-selector-dialog.component';

private dialog = inject(MatDialog);

getWellParameters(): ParameterDefinition[] {
  return this.selectedProtocol()?.parameters?.filter(p => this.isWellSelectionParameter(p)) || [];
}

openWellSelector(param: ParameterDefinition) {
  const currentSelection = this.wellSelections()[param.name] || [];
  
  // Auto-detect plate type from selected assets
  const plateType = this.detectPlateType();
  
  const dialogData: WellSelectorDialogData = {
    plateType,
    initialSelection: currentSelection,
    mode: 'multi',
    title: `Select Wells: ${param.name}`,
    plateLabel: param.description || param.name
  };
  
  this.dialog.open(WellSelectorDialogComponent, { 
    data: dialogData,
    width: plateType === '384' ? '900px' : '700px'
  }).afterClosed().subscribe((result: WellSelectorDialogResult) => {
    if (result?.confirmed) {
      this.wellSelections.update(s => ({ ...s, [param.name]: result.wells }));
      this.validateWellSelections();
    }
  });
}

private detectPlateType(): '96' | '384' {
  // Check configured assets for plate with well count
  const assets = this.configuredAssets();
  if (assets) {
    for (const [, asset] of Object.entries(assets)) {
      const res = asset as any;
      // Check resource definition for well count
      if (res?.fqn?.toLowerCase().includes('384') || res?.name?.includes('384')) {
        return '384';
      }
    }
  }
  return '96';  // Default
}

getWellSelectionLabel(paramName: string): string {
  const wells = this.wellSelections()[paramName] || [];
  if (wells.length === 0) return 'Click to select wells...';
  if (wells.length <= 5) return wells.join(', ');
  return `${wells.length} wells selected`;
}

areWellSelectionsValid(): boolean {
  const wellParams = this.getWellParameters();
  const selections = this.wellSelections();
  
  // All required well parameters must have at least one selection
  return wellParams.every(p => {
    if (p.optional) return true;
    return (selections[p.name]?.length || 0) > 0;
  });

}

private validateWellSelections() {
  this.wellsFormGroup.get('valid')?.setValue(this.areWellSelectionsValid());
}
```

#### 2.5 Include Well Selections in Run Parameters

**Update** `startRun()`:

```typescript
const params = {
  ...this.parametersFormGroup.value,
  ...this.configuredAssets(),
  ...this.wellSelections()  // Add well selections
};
```

---

## Part 3: Execution Monitor Auto-Refresh

### Implementation

**In** `run-history-table.component.ts`, add interval refresh:

```typescript
private refreshInterval?: ReturnType<typeof setInterval>;

ngOnInit() {
  this.loadRuns();
  
  // Auto-refresh every 10 seconds
  this.refreshInterval = setInterval(() => {
    this.loadRuns();
  }, 10000);
}

ngOnDestroy() {
  if (this.refreshInterval) {
    clearInterval(this.refreshInterval);
  }
}
```

---

## Technical Debt (Future Work)

### Improved Well Parameter Detection

The current heuristic (`isWellSelectionParameter`) is basic. Future improvement:

1. **Tracer Integration**: During protocol simulation, trace which parameters are used as indices to plate resources
2. **Parameter Metadata**: Add explicit `ui_hint: { type: 'well_selector' }` to parameter definitions
3. **Protocol Analysis**: Backend protocol analyzer should flag parameters that receive well indices

**Track in**: [TECHNICAL_DEBT.md](../../TECHNICAL_DEBT.md)

---

## Files to Modify

| File | Changes |
|------|---------|
| `run-protocol.component.ts` | Use name/notes controls, add well selection step & methods |
| `execution.service.ts` | Add notes param, save/update run in IndexedDB |
| `sqlite.service.ts` | Fix `createProtocolRun()` to match schema |
| `run-history-table.component.ts` | Add auto-refresh interval |

---

## Testing

### Manual Testing

1. **Run Persistence**:
   - Start a run in browser mode
   - Navigate to Execution Monitor
   - Verify run appears in history table
   - Verify status updates (QUEUED → RUNNING → COMPLETED)

2. **Name & Notes**:
   - Enter custom run name
   - Enter notes
   - Start run
   - Verify name appears in Execution Monitor

3. **Well Selection**:
   - Select `selective_transfer` protocol (or add well params to test protocol)
   - Verify Well Selection step appears
   - Open well selector dialog
   - Select wells
   - Verify selections persist through workflow
   - Start run and verify wells passed to execution

### Unit Tests

- `ExecutionService`: Mock `sqliteService.createProtocolRun()`, verify data shape
- `RunProtocolComponent`: Test `isWellSelectionParameter()` with various inputs

---

## Success Criteria

- [ ] Browser-mode runs appear in Execution Monitor
- [ ] Run status updates correctly (QUEUED → RUNNING → COMPLETED/FAILED)
- [ ] User-entered run name and notes are persisted
- [ ] Well Selection step appears only when protocol requires it
- [ ] Plate type auto-detected from selected assets
- [ ] Well selections passed to execution
- [ ] Execution Monitor auto-refreshes

---

## On Completion

- [ ] All implementation complete
- [ ] Tests passing
- [ ] Manual QA verified
- [ ] Update [DEVELOPMENT_MATRIX.md](../../DEVELOPMENT_MATRIX.md)
- [ ] Update [run_protocol_workflow.md](../../backlog/run_protocol_workflow.md)
- [ ] Add improved well detection to [TECHNICAL_DEBT.md](../../TECHNICAL_DEBT.md)
- [ ] Mark this prompt complete in batch README

---

## References

- [run_protocol_workflow.md](../../backlog/run_protocol_workflow.md) - Parent backlog
- [well-selector-dialog.component.ts](../../../praxis/web-client/src/app/shared/components/well-selector-dialog/well-selector-dialog.component.ts) - Well UI
- [schema.sql](../../../praxis/web-client/src/assets/db/schema.sql) - Database schema
