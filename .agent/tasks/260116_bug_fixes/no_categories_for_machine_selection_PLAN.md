# No Categories for Machine Selection Plan (REVISED)

## Goal

Fix the issue where "No categories" appear in the Inventory Dialog when adding a machine in a fresh Browser Mode session. Implement a proper **Catalog-to-Inventory workflow** that allows users to quickly instantiate simulated machines from the Machine Definition catalog without mixing entity types.

## User Review Required

> [!IMPORTANT]
> This revision addresses critical architectural concerns identified in code review:
>
> - **NO mixing of `MachineDefinition` and `Machine` entities** in the same list
> - **NO fake status enums** (`'SIMULATED_DEF'`)
> - **Creates real `Machine` instances** with valid status enums and proper CRUD support

## Problem Analysis

The original plan proposed mixing `MachineDefinition` (catalog items) with `Machine` (inventory instances) by creating "mocked" machine objects. This is an anti-pattern that:

- Breaks type safety
- Causes CRUD operation failures (edit/delete on non-existent DB rows)
- Pollutes component state with ambiguous entities
- Introduces invalid status values

## Proposed Changes

### Inventory Dialog (Catalog-to-Inventory Workflow)

#### [MODIFY] [inventory-dialog.component.ts](file:///Users/mar/Projects/pylabpraxis/praxis/web-client/src/app/features/playground/components/inventory-dialog/inventory-dialog.component.ts)

**Architecture**: Separate the UI into two distinct sections:

1. **"My Lab" (Inventory Tab)**:
   - Shows real `Machine` instances from `AssetService.getMachines()`
   - Standard list with existing functionality (edit, delete, filter by status)
   - If empty, shows empty state with link to "Browse Catalog"

2. **"Catalog" (Add New Tab/Section)**:
   - Shows `MachineDefinition` items from `AssetService.getMachineDefinitions()`
   - Grouped by `machine_category` (LiquidHandler, PlateReader, etc.)
   - Each definition card has a **"Quick Add Simulated"** button

**Implementation Details**:

```typescript
// Add to component
readonly machineDefinitions = toSignal(
  this.assetService.getMachineDefinitions(),
  { initialValue: [] }
);

readonly definitionCategories = computed(() => {
  const defs = this.machineDefinitions();
  const categories = new Set(defs.map(d => d.machine_category));
  return Array.from(categories).sort();
});

// Quick Add handler
async onQuickAddSimulated(definition: MachineDefinition) {
  const newMachine: Partial<Machine> = {
    name: `${definition.brand} ${definition.model} (Simulated)`,
    definition_id: definition.id,
    machine_definition_id: definition.id,
    is_simulated: true,
    status: 'IDLE', // Valid enum status
    location: 'Virtual',
    // ...other required NOT NULL fields with defaults
  };
  
  try {
    const created = await this.assetService.createMachine(newMachine);
    // Switch to "My Lab" tab to show the new instance
    this.selectedTab.set('inventory');
    // Optionally auto-select the new machine for immediate use
    this.onSelectAsset(created);
  } catch (error) {
    // Show error toast
  }
}
```

**Template Structure**:

```html
<mat-tab-group>
  <mat-tab label="My Lab">
    @if (machines().length === 0) {
      <app-empty-state
        icon="heroBeaker"
        title="No Machines in Inventory"
        description="Add a simulated machine from the catalog to get started."
        [action]="{ label: 'Browse Catalog', handler: () => selectedTab.set('catalog') }">
      </app-empty-state>
    } @else {
      <!-- Existing machine list -->
    }
  </mat-tab>

  <mat-tab label="Catalog">
    @for (category of definitionCategories(); track category) {
      <mat-expansion-panel>
        <mat-expansion-panel-header>
          <mat-panel-title>{{ category }}</mat-panel-title>
        </mat-expansion-panel-header>
        @for (def of definitionsInCategory(category); track def.id) {
          <mat-card>
            <mat-card-header>
              <mat-card-title>{{ def.brand }} {{ def.model }}</mat-card-title>
            </mat-card-header>
            <mat-card-actions>
              <button mat-raised-button color="primary"
                      (click)="onQuickAddSimulated(def)">
                <mat-icon>add_circle</mat-icon>
                Quick Add Simulated
              </button>
            </mat-card-actions>
          </mat-card>
        }
      }
    }
  </mat-tab>
</mat-tab-group>
```

### Asset Service (Ensure Defaults)

#### [MODIFY] [asset.service.ts](file:///Users/mar/Projects/pylabpraxis/praxis/web-client/src/app/features/assets/services/asset.service.ts)

Ensure `createMachine` handles all NOT NULL fields with sensible defaults for simulated instances:

```typescript
async createMachine(machine: Partial<Machine>): Promise<Machine> {
  const defaults = {
    status: 'IDLE',
    is_simulated: false,
    location: 'Unknown',
    maintenance_enabled: false,
    maintenance_schedule_json: '{}',
    // ...other defaults
  };
  
  const fullMachine = { ...defaults, ...machine };
  // Validation, then repository.create()
}
```

## Verification Plan

### Automated Tests

1. **Unit Test - Asset Service**:

   ```bash
   npx vitest run praxis/web-client/src/app/features/assets/services/asset.service.spec.ts
   ```

   - Verify `createMachine` with simulated flag creates valid instance

2. **Unit Test - Inventory Dialog**:
   - Mock `getMachineDefinitions()` with test data
   - Verify `onQuickAddSimulated()` calls `createMachine` with correct payload
   - Verify tab switching to "My Lab" after creation

### Manual Verification

1. **Launch App**: Start Browser Mode with clean DB (`?resetdb=1`)
2. **Navigate to Playground**: Click "Add Machine"
3. **Verify Catalog Tab**:
   - See categories (LiquidHandler, PlateReader, etc.)
   - See definition cards with "Quick Add Simulated" buttons
4. **Quick Add Flow**:
   - Click "Quick Add Simulated" on a LiquidHandler definition
   - Verify:
     - Button shows loading state during creation
     - Dialog switches to "My Lab" tab
     - New machine appears in inventory with "(Simulated)" suffix
     - Machine has valid `IDLE` status (not a fake enum)
5. **CRUD Operations**:
   - Verify you can edit the newly created machine's name
   - Verify you can delete the machine
   - Verify standard inventory operations work
6. **Playground Integration**:
   - Select the simulated machine
   - Click "Insert Assets into Notebook"
   - Verify Python code generation works correctly

### Edge Cases

- Adding the same definition twice creates two distinct instances (verify)
- Empty state in "My Lab" tab links to "Catalog" tab (verify)
- Catalog tab shows all definitions even when inventory is empty (verify)
