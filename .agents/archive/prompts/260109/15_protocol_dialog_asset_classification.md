# Agent Prompt: Protocol Dialog Asset Classification

Examine `.agents/README.md` for development context.

**Status:** 🟢 Completed
**Priority:** P2
**Difficulty:** Easy
**Batch:** [260109](./README.md)
**Backlog Reference:** [protocol_workflow.md](../../backlog/protocol_workflow.md#p2-protocol-dialog-asset-classification)

---

## 1. The Task

In the protocol detail dialog (opened when clicking a protocol in the library), machines are incorrectly displayed under "Parameters" when they should be under "Asset Requirements".

**Goal:** Ensure machine-type parameters are classified and displayed under the "Asset Requirements" section, while only runtime parameters remain in the "Parameters" section.

**User Value:** Clear separation between hardware requirements and configuration parameters helps users understand what resources a protocol needs vs. what values they can customize.

---

## 2. Technical Implementation Strategy

**Current State Analysis:**

Looking at `ProtocolDetailDialogComponent`, the dialog displays:

- `data.protocol.assets` under "Asset Requirements"
- `data.protocol.parameters` under "Parameters"

The issue is that machine-type parameters (those with type hints like `LiquidHandler`, `PlateReader`, etc.) are in the `parameters` array instead of the `assets` array.

**Frontend Components:**

- Modify the template to filter/separate machine parameters from runtime parameters
- OR ensure backend provides correct classification (check if this is a frontend display issue or backend data issue)

**Approach:**

1. **Identify machine parameters** by checking `type_hint` against known PLR machine classes
2. **Create computed lists** in the component:
   - `machineParameters`: parameters whose `type_hint` indicates a machine class
   - `runtimeParameters`: all other parameters
3. **Display machine parameters** in Asset Requirements section alongside `protocol.assets`

**Data Flow:**

1. Protocol data comes from `ProtocolService.getProtocols()`
2. `ProtocolDefinition.parameters` contains all parameters including machine-typed ones
3. Component filters and separates for display

---

## 3. Context & References

**Primary Files to Modify:**

| Path | Description |
|:-----|:------------|
| `praxis/web-client/src/app/features/protocols/components/protocol-detail-dialog/protocol-detail-dialog.component.ts` | Dialog component - add filtering logic and update template |

**Reference Files (Read-Only):**

| Path | Description |
|:-----|:------------|
| `praxis/web-client/src/app/features/protocols/models/protocol.models.ts` | Protocol and Parameter type definitions |
| `praxis/web-client/src/app/features/assets/models/asset.models.ts` | Machine category constants |
| `praxis/web-client/src/app/shared/constants/asset-icons.ts` | Machine category list for reference |

---

## 4. Constraints & Conventions

- **Commands**: Use `npm` for Angular tasks
- **Frontend Path**: `praxis/web-client`
- **Styling**: Match existing styling patterns in the dialog
- **State**: Can use simple computed properties or getter methods

**Implementation Guidance:**

```typescript
// In the component class
private readonly MACHINE_TYPE_HINTS = [
  'LiquidHandler', 'PlateReader', 'HeaterShaker', 'Centrifuge',
  'Incubator', 'Sealer', 'Peeler', 'Barcode', 'Washer'
];

get machineParameters() {
  return this.data.protocol.parameters.filter(p =>
    this.MACHINE_TYPE_HINTS.some(hint => p.type_hint?.includes(hint))
  );
}

get runtimeParameters() {
  return this.data.protocol.parameters.filter(p =>
    !this.MACHINE_TYPE_HINTS.some(hint => p.type_hint?.includes(hint))
  );
}
```

**Template Update:**

```html
<!-- Asset Requirements Section -->
<section class="info-section">
  <h3 class="section-title">Asset Requirements</h3>
  <!-- Existing assets -->
  <mat-list *ngIf="data.protocol.assets.length > 0 || machineParameters.length > 0">
    <!-- Existing asset items -->
    <mat-list-item *ngFor="let asset of data.protocol.assets">...</mat-list-item>
    <!-- Machine parameters displayed as assets -->
    <mat-list-item *ngFor="let param of machineParameters">
      <mat-icon matListItemIcon>precision_manufacturing</mat-icon>
      <div matListItemTitle>{{ param.name }}</div>
      <div matListItemLine>{{ param.type_hint }}</div>
    </mat-list-item>
  </mat-list>
</section>

<!-- Parameters Section - now only runtime params -->
<section class="info-section">
  <h3 class="section-title">Parameters</h3>
  <mat-list *ngIf="runtimeParameters.length > 0; else noParams">
    <mat-list-item *ngFor="let param of runtimeParameters">...</mat-list-item>
  </mat-list>
</section>
```

---

## 5. Verification Plan

**Definition of Done:**

1. Machine-type parameters appear under "Asset Requirements" section
2. Runtime parameters (strings, numbers, booleans, etc.) appear under "Parameters" section
3. Visual consistency maintained with existing styling
4. No regressions in protocol detail display

**Verification Commands:**

```bash
cd praxis/web-client
npm run build
```

**Manual Verification:**

1. Navigate to Protocol Library
2. Click on a protocol that has machine parameters (e.g., `liquid_handler: LiquidHandler`)
3. Verify machine parameters appear under "Asset Requirements"
4. Verify non-machine parameters appear under "Parameters"

---

## On Completion

- [ ] Commit changes with message: `fix(protocols): classify machine parameters as asset requirements`
- [ ] Update backlog item status in `backlog/protocol_workflow.md`
- [ ] Update `DEVELOPMENT_MATRIX.md` if applicable
- [ ] Mark this prompt complete in batch README and set status to 🟢 Completed

---

## References

- `.agents/README.md` - Development context and agent workflow
- `backlog/protocol_workflow.md` - Full protocol workflow issue tracking
