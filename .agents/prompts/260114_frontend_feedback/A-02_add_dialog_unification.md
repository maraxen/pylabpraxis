# Agent Prompt: Add Dialog Unification

Examine `.agents/README.md` for development context.

**Status:** 🟢 Not Started
**Priority:** P2
**Batch:** [260114_frontend_feedback](./README.md)
**Difficulty:** 🟡 Intricate
**Type:** 🟢 Implementation
**Dependencies:** A-01 (Shared View Controls)
**Backlog Reference:** Group A - View Controls Standardization

---

## 1. The Task

Unify the Add Asset, Add Machine, and Add Resource dialog flows into a consistent pattern. Currently these dialogs have different UX flows and implementations.

### User Feedback

> "maybe we should unify add asset add machine dialog routes (select type, then specific one, then additional configuration)"

### Target Flow

```markdown
Step 1: Select Type (Machine or Resource)
   ↓
Step 2: Select Specific Definition (from catalog)
   ↓  
Step 3: Additional Configuration (name, capabilities, connection info)
   ↓
Step 4: Create Asset
```

### Current State

- **MachineDialogComponent** (704 lines): Stepper flow with Type → Backend → Config
- **ResourceDialogComponent** (561 lines): Grouped selection with faceted filters
- **AddAssetChoiceDialog**: Simple Machine/Resource choice

These need to be consolidated into a unified flow.

## 2. Technical Implementation Strategy

### Option A: Unified Stepper Dialog (Recommended)

Create a single `AddAssetDialogComponent` that handles both machines and resources:

```
shared/dialogs/add-asset-dialog/
├── add-asset-dialog.component.ts
├── add-asset-dialog.component.html
├── add-asset-dialog.component.scss
├── steps/
│   ├── type-selection-step.component.ts
│   ├── definition-selection-step.component.ts
│   └── configuration-step.component.ts
└── index.ts
```

### Stepper Implementation

```typescript
@Component({
  selector: 'app-add-asset-dialog',
  standalone: true,
  // ...
})
export class AddAssetDialogComponent {
  currentStep = signal<'type' | 'definition' | 'config'>('type');
  assetType = signal<'machine' | 'resource' | null>(null);
  selectedDefinition = signal<MachineDefinition | ResourceDefinition | null>(null);
  
  // Step 1: Type Selection
  selectType(type: 'machine' | 'resource') {
    this.assetType.set(type);
    this.currentStep.set('definition');
  }
  
  // Step 2: Definition Selection (reuse existing catalog UI)
  selectDefinition(def: MachineDefinition | ResourceDefinition) {
    this.selectedDefinition.set(def);
    this.currentStep.set('config');
  }
  
  // Step 3: Configuration (dynamic form based on type)
  getConfigSchema() {
    return this.assetType() === 'machine' 
      ? this.getMachineConfigSchema()
      : this.getResourceConfigSchema();
  }
}
```

### Reusable Sub-Components

1. **TypeSelectionStepComponent** - Choose Machine or Resource
2. **DefinitionSelectionStepComponent** - Unified catalog browser with search
3. **ConfigurationStepComponent** - Dynamic form based on definition

### Migration Path

1. Create new unified dialog
2. Keep existing dialogs working (don't break anything)
3. Update `AssetsComponent` to use new dialog
4. Deprecate old dialogs once verified

## 3. Context & References

**Files to Create:**

| Path | Description |
|:-----|:------------|
| `praxis/web-client/src/app/shared/dialogs/add-asset-dialog/add-asset-dialog.component.ts` | Main unified dialog |
| `praxis/web-client/src/app/shared/dialogs/add-asset-dialog/steps/type-selection-step.component.ts` | Step 1 |
| `praxis/web-client/src/app/shared/dialogs/add-asset-dialog/steps/definition-selection-step.component.ts` | Step 2 |
| `praxis/web-client/src/app/shared/dialogs/add-asset-dialog/steps/configuration-step.component.ts` | Step 3 |

**Files to Modify:**

| Path | Description |
|:-----|:------------|
| `praxis/web-client/src/app/features/assets/assets.component.ts` | Update `openAddAsset()` to use new dialog |

**Reference Files (Existing Implementations):**

| Path | Description |
|:-----|:------------|
| `praxis/web-client/src/app/features/assets/components/machine-dialog.component.ts` | Current machine dialog (704 lines) |
| `praxis/web-client/src/app/features/assets/components/resource-dialog.component.ts` | Current resource dialog (561 lines) |
| `praxis/web-client/src/app/features/assets/components/add-asset-choice-dialog.component.ts` | Current choice dialog |
| `praxis/web-client/src/app/features/assets/components/dynamic-capability-form.component.ts` | Reusable capability form |

## 4. Constraints & Conventions

- **Mat Stepper**: Use Angular Material stepper for step navigation
- **Preserve Functionality**: New dialog must support all existing features
- **Backward Compatible**: Don't remove old dialogs until new one is verified
- **Signals**: Use Angular Signals for state management

## 5. Verification Plan

**Definition of Done:**

1. New unified dialog compiles without errors
2. Can create machines through new dialog
3. Can create resources through new dialog
4. Stepper navigation works correctly
5. All machine backends still available
6. All resource types still available

**Test Commands:**

```bash
cd praxis/web-client
npx tsc --noEmit
npm run build
```

**Manual Verification:**

1. Open Assets page
2. Click "+ Add Asset" button
3. Verify step 1 shows Machine/Resource choice
4. Select Machine → verify definitions appear
5. Select definition → verify config form appears
6. Complete flow and verify machine is created
7. Repeat for Resource

---

## On Completion

- [ ] All files created and compiling
- [ ] Manual verification complete
- [ ] Mark this prompt complete in batch README
- [ ] Set status in this document to 🟢 Completed
- [ ] Proceed to A-03 for Quick Add Autocomplete

---

## References

- `.agents/README.md` - Environment overview
- `GROUP_A_view_controls_init.md` - Parent initiative
