# Agent Prompt: Autoselect Buttons for Machine & Asset Steps

Examine `.agents/README.md` for development context.

**Status:** 🟢 Not Started
**Priority:** P1
**Batch:** [260109](README.md)
**Backlog Reference:** [protocol_workflow.md](../../backlog/protocol_workflow.md)
**Estimated Complexity:** Easy-Medium

---

## 1. The Task

Add "Auto-Select" buttons to both the **Machine Selection** step (Step 3) and **Asset Selection** step (Step 4) in the protocol workflow. These buttons allow users to re-trigger automatic selection after making manual changes or when new inventory is available.

**User Value:** Quick recovery from manual selection mistakes and discovery of newly added compatible resources.

---

## 2. Technical Implementation Strategy

### Part A: Asset Selection Step (GuidedSetupComponent)

The `autoSelect()` method already exists in `GuidedSetupComponent`. Just need to:

1. **Expose it in the UI** with a button
2. **Add the button to the header or summary area**

**Location in template (~line 50-65):**

```html
<!-- Add Auto-Select button after the description or in the summary -->
<div class="flex justify-between items-center mb-4">
  <p class="description" *ngIf="!isInline">
    Please assign inventory items to the required assets for this protocol.
    We've auto-selected matches where possible.
  </p>
  <button 
    mat-stroked-button 
    (click)="autoSelect()"
    [disabled]="isLoading()"
    matTooltip="Re-run automatic selection based on best matches">
    <mat-icon>auto_awesome</mat-icon>
    Auto-Select
  </button>
</div>
```

### Part B: Machine Selection Step (RunProtocolComponent)

The machine selection is in the parent `RunProtocolComponent`. Need to:

1. **Add autoselect logic** that picks the first compatible machine
2. **Add a button** in the machine selection step header

**Add method to RunProtocolComponent:**

```typescript
autoSelectMachine() {
  const compatible = this.compatibilityData().filter(item => {
    // Filter to only compatible machines
    if (!item.compatibility.is_compatible) return false;
    
    // If physical mode, exclude simulated machines
    if (!this.store.simulationMode()) {
      const connectionInfo = item.machine.connection_info || {};
      const backend = (connectionInfo['backend'] || '').toString();
      const isSimulated = item.machine.is_simulation_override === true ||
        (item.machine as any).is_simulated === true ||
        backend.includes('Simulator');
      if (isSimulated) return false;
    }
    
    return true;
  });

  if (compatible.length > 0) {
    this.onMachineSelect(compatible[0]);
  }
}
```

**Add button to machine selection step header (~line 287):**

```html
<h3 class="text-xl font-bold text-sys-text-primary mb-6 flex items-center gap-3">
   <div class="w-8 h-8 rounded-lg bg-primary/20 flex items-center justify-center text-primary">
     <mat-icon>precision_manufacturing</mat-icon>
   </div>
   Select Execution Machine
   <span class="flex-1"></span>
   
   <!-- NEW: Auto-Select Button -->
   <button 
     mat-stroked-button 
     (click)="autoSelectMachine()"
     [disabled]="isLoadingCompatibility()"
     matTooltip="Automatically select first compatible machine">
     <mat-icon>auto_awesome</mat-icon>
     Auto-Select
   </button>
   
   <app-hardware-discovery-button></app-hardware-discovery-button>
</h3>
```

### Part C: Add button to Asset Selection step wrapper in RunProtocolComponent

Since `GuidedSetupComponent` is used inline, also add a parent-level auto-select trigger:

**In RunProtocolComponent template (~line 323-345):**

```html
<!-- Step 4: Asset Selection -->
<mat-step [stepControl]="assetsFormGroup">
   <ng-template matStepLabel><span data-tour-id="run-step-label-assets">Select Assets</span></ng-template>
   <div class="h-full flex flex-col p-6" data-tour-id="run-step-assets">
     <div class="flex-1 overflow-y-auto">
       <h3 class="text-xl font-bold text-sys-text-primary mb-6 flex items-center gap-3">
          <div class="w-8 h-8 rounded-lg bg-primary/20 flex items-center justify-center text-primary">
            <mat-icon>inventory_2</mat-icon>
          </div>
          Asset Selection
          <span class="flex-1"></span>
          
          <!-- NEW: Auto-Select Button -->
          <button 
            mat-stroked-button 
            (click)="guidedSetup?.autoSelect()"
            matTooltip="Re-run automatic asset matching">
            <mat-icon>auto_awesome</mat-icon>
            Auto-Select
          </button>
       </h3>

       @if (selectedProtocol()) {
          <app-guided-setup 
            #guidedSetup
            [protocol]="selectedProtocol()" 
            [isInline]="true"
            (selectionChange)="onAssetSelectionChange($event)">
          </app-guided-setup>
       }
     </div>
     <!-- ... rest of step -->
   </div>
</mat-step>
```

**Add ViewChild reference:**

```typescript
@ViewChild('guidedSetup') guidedSetup?: GuidedSetupComponent;
```

---

## 3. Context & References

**Primary Files to Modify:**

| Path | Description |
|:-----|:------------|
| `praxis/web-client/src/app/features/run-protocol/run-protocol.component.ts` | Add auto-select button to machine step header, add `autoSelectMachine()` method, add ViewChild for guidedSetup |
| `praxis/web-client/src/app/features/run-protocol/components/guided-setup/guided-setup.component.ts` | Make `autoSelect()` public (already is), optionally add button in inline mode |

**Reference Files (Read-Only):**

| Path | Description |
|:-----|:------------|
| `praxis/web-client/src/app/features/run-protocol/components/machine-selection/machine-selection.component.ts` | Machine compatibility model and selection logic |

---

## 4. Constraints & Conventions

- **Commands**: Use `npm` for Angular CLI commands
- **Frontend Path**: `praxis/web-client`
- **Styling**: Use existing button patterns (mat-stroked-button with icon)
- **State**: Leverage existing signals and methods
- **Linting**: Run `npm run lint` before committing

---

## 5. Verification Plan

**Definition of Done:**

1. The code compiles without errors:

   ```bash
   cd praxis/web-client && npm run build
   ```

2. Auto-Select button appears in Machine Selection step header
3. Auto-Select button appears in Asset Selection step header
4. Clicking Auto-Select in machine step selects first compatible machine
5. Clicking Auto-Select in asset step re-runs autoSelect matching

**Manual Testing:**

1. Open a protocol for execution
2. On Machine Selection step:
   - Click Auto-Select
   - Verify a compatible machine is selected
   - Manually change selection, click Auto-Select again
   - Verify it re-selects optimally
3. On Asset Selection step:
   - Click Auto-Select
   - Verify assets are auto-matched
   - Manually clear a selection, click Auto-Select
   - Verify it re-fills the cleared slot

---

## On Completion

- [ ] Commit changes with message: "feat(protocol): add auto-select buttons to machine and asset steps"
- [ ] Update backlog item status
- [ ] Mark this prompt complete in batch README

---

## References

- `.agents/README.md` - Environment overview
- Angular Material Button documentation
