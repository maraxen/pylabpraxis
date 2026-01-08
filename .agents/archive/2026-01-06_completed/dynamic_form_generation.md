# Dynamic Form Generation for Machine Capabilities

**Priority**: High (MVP → Full Implementation)
**Owner**: Full Stack
**Created**: 2025-12-30
**Status**: ✅ Complete (Phases 1-4 Done - 2025-12-31)

---

## Overview

Replace the JSON textarea for `user_configured_capabilities` in the Machine Dialog with auto-generated forms based on `MachineCapabilityConfigSchema`. This provides a better UX for configuring optional machine modules (iSWAP, CoRe96, etc.).

### Current State (MVP)

```
┌─────────────────────────────────────────────┐
│ User Configured Capabilities (JSON)          │
│ ┌─────────────────────────────────────────┐ │
│ │ {"has_iswap": true, "has_core96": true} │ │
│ └─────────────────────────────────────────┘ │
│ Configure optional modules...                │
└─────────────────────────────────────────────┘
```

### Target State (Full Implementation)

```
┌─────────────────────────────────────────────┐
│ Optional Modules                             │
│ ┌─────────────────────────────────────────┐ │
│ │ ☑ iSWAP Plate Handler                   │ │
│ │   Enables plate transport between sites  │ │
│ │                                          │ │
│ │ ☑ CoRe 96 Head                          │ │
│ │   96-channel parallel pipetting          │ │
│ │                                          │ │
│ │ ☐ HEPA Filter                           │ │
│ │   Integrated HEPA filtration system      │ │
│ └─────────────────────────────────────────┘ │
└─────────────────────────────────────────────┘
```

---

## Architecture

### Data Flow

```
PLR Source Code
      │
      ▼
┌─────────────────────────┐
│ CapabilityExtractor     │ ← LibCST visitor extracts capability signals
│ (capability_extractor.py)│
└───────────┬─────────────┘
            │
            ▼
┌─────────────────────────┐
│ MachineCapabilityConfig │ ← Generate config schema from signals
│ Schema Generator        │
└───────────┬─────────────┘
            │
            ▼
┌─────────────────────────┐
│ MachineDefinitionOrm    │ ← Store capabilities_config JSON
│ (capabilities_config)   │
└───────────┬─────────────┘
            │
            ▼ (API response)
┌─────────────────────────┐
│ MachineDefinition       │ ← Frontend receives schema
│ (capabilities_config)   │
└───────────┬─────────────┘
            │
            ▼
┌─────────────────────────┐
│ DynamicCapabilityForm   │ ← Angular component renders form
│ Component               │
└───────────┬─────────────┘
            │
            ▼
┌─────────────────────────┐
│ MachineOrm              │ ← Store user_configured_capabilities JSON
│ (user_configured_caps)  │
└─────────────────────────┘
```

---

## Implementation Phases

### Phase 1: Backend - Schema Generation ✅ COMPLETE (2025-12-30)

#### 1.1 Define Capability Config Templates

Create machine-type-specific config templates in `capability_extractor.py`:

```python
# praxis/backend/utils/plr_static_analysis/capability_config_templates.py

LIQUID_HANDLER_CONFIG_TEMPLATE = MachineCapabilityConfigSchema(
    machine_type="liquid_handler",
    config_fields=[
        CapabilityConfigField(
            field_name="has_iswap",
            display_name="iSWAP Plate Handler",
            field_type="boolean",
            default_value=False,
            help_text="Integrated plate transport arm for moving labware between positions"
        ),
        CapabilityConfigField(
            field_name="has_core96",
            display_name="CoRe 96 Head",
            field_type="boolean",
            default_value=False,
            help_text="96-channel head for parallel pipetting operations"
        ),
        CapabilityConfigField(
            field_name="has_hepa",
            display_name="HEPA Filter",
            field_type="boolean",
            default_value=False,
            help_text="Integrated HEPA filtration for sterile operations"
        ),
        CapabilityConfigField(
            field_name="num_channels",
            display_name="Number of Channels",
            field_type="select",
            default_value=8,
            options=["1", "4", "8", "12", "16", "96", "384"],
            help_text="Number of independent pipetting channels"
        ),
    ]
)

PLATE_READER_CONFIG_TEMPLATE = MachineCapabilityConfigSchema(
    machine_type="plate_reader",
    config_fields=[
        CapabilityConfigField(
            field_name="has_absorbance",
            display_name="Absorbance",
            field_type="boolean",
            default_value=True,
            help_text="Absorbance measurement capability"
        ),
        CapabilityConfigField(
            field_name="has_fluorescence",
            display_name="Fluorescence",
            field_type="boolean",
            default_value=False,
            help_text="Fluorescence measurement capability"
        ),
        CapabilityConfigField(
            field_name="has_luminescence",
            display_name="Luminescence",
            field_type="boolean",
            default_value=False,
            help_text="Luminescence measurement capability"
        ),
    ]
)

# ... templates for other machine types
```

#### 1.2 Update Capability Extractor

Modify `build_machine_capabilities()` to also generate `capabilities_config`:

```python
def build_capabilities_config(self, class_type: PLRClassType) -> MachineCapabilityConfigSchema | None:
    """Generate config schema based on machine type and detected signals."""
    template = CAPABILITY_CONFIG_TEMPLATES.get(class_type)
    if not template:
        return None

    # Clone template and customize based on detected capabilities
    config = template.model_copy(deep=True)

    # Pre-fill defaults based on what we detected in the source
    for field in config.config_fields:
        if field.field_name in self._signals:
            field.default_value = self._signals[field.field_name]

    return config
```

#### 1.3 Update Parser

Pass `capabilities_config` through the discovery pipeline to `MachineDefinitionOrm`.

---

### Phase 2: Frontend - Dynamic Form Component (3-4 hours)

#### 2.1 Create DynamicCapabilityFormComponent

```typescript
// src/app/shared/components/dynamic-capability-form/dynamic-capability-form.component.ts

@Component({
  selector: 'app-dynamic-capability-form',
  template: `
    <div class="capability-form" *ngIf="schema">
      <h4 class="text-sm font-medium text-gray-700 mb-3">{{ schema.machine_type | titlecase }} Configuration</h4>

      <div class="space-y-4">
        @for (field of visibleFields(); track field.field_name) {
          <div class="capability-field" [class.disabled]="isDisabled(field)">

            <!-- Boolean Toggle -->
            @if (field.field_type === 'boolean') {
              <mat-slide-toggle
                [formControl]="getControl(field.field_name)"
                [matTooltip]="field.help_text || ''">
                {{ field.display_name }}
              </mat-slide-toggle>
            }

            <!-- Number Input -->
            @if (field.field_type === 'number') {
              <mat-form-field appearance="outline" class="w-full">
                <mat-label>{{ field.display_name }}</mat-label>
                <input matInput type="number" [formControl]="getControl(field.field_name)">
                <mat-hint *ngIf="field.help_text">{{ field.help_text }}</mat-hint>
              </mat-form-field>
            }

            <!-- Select -->
            @if (field.field_type === 'select') {
              <mat-form-field appearance="outline" class="w-full">
                <mat-label>{{ field.display_name }}</mat-label>
                <mat-select [formControl]="getControl(field.field_name)">
                  @for (option of field.options; track option) {
                    <mat-option [value]="option">{{ option }}</mat-option>
                  }
                </mat-select>
                <mat-hint *ngIf="field.help_text">{{ field.help_text }}</mat-hint>
              </mat-form-field>
            }

            <!-- Multi-select -->
            @if (field.field_type === 'multiselect') {
              <mat-form-field appearance="outline" class="w-full">
                <mat-label>{{ field.display_name }}</mat-label>
                <mat-select [formControl]="getControl(field.field_name)" multiple>
                  @for (option of field.options; track option) {
                    <mat-option [value]="option">{{ option }}</mat-option>
                  }
                </mat-select>
                <mat-hint *ngIf="field.help_text">{{ field.help_text }}</mat-hint>
              </mat-form-field>
            }

          </div>
        }
      </div>
    </div>
  `
})
export class DynamicCapabilityFormComponent {
  @Input() schema: MachineCapabilityConfigSchema | null = null;
  @Input() initialValues: Record<string, any> = {};
  @Output() valueChange = new EventEmitter<Record<string, any>>();

  private formGroup = new FormGroup({});

  // ... implementation
}
```

#### 2.2 Update MachineDialogComponent

Replace JSON textarea with dynamic form:

```typescript
// In template, replace:
<mat-form-field *ngIf="selectedDefinition">
  <mat-label>User Configured Capabilities (JSON)</mat-label>
  <textarea matInput formControlName="user_configured_capabilities" ...></textarea>
</mat-form-field>

// With:
<app-dynamic-capability-form
  *ngIf="selectedDefinition?.capabilities_config"
  [schema]="selectedDefinition.capabilities_config"
  [initialValues]="form.get('user_configured_capabilities')?.value || {}"
  (valueChange)="onCapabilitiesChange($event)">
</app-dynamic-capability-form>

<!-- Fallback to JSON for definitions without schema -->
<mat-form-field *ngIf="selectedDefinition && !selectedDefinition.capabilities_config">
  <mat-label>User Configured Capabilities (JSON)</mat-label>
  <textarea matInput formControlName="user_configured_capabilities" ...></textarea>
</mat-form-field>
```

---

### Phase 3: Conditional Field Visibility (1-2 hours)

#### 3.1 Implement `depends_on` Logic

Handle fields that should only appear when another field has a specific value:

```typescript
visibleFields = computed(() => {
  if (!this.schema) return [];

  return this.schema.config_fields.filter(field => {
    if (!field.depends_on) return true;

    // Parse depends_on: "has_iswap" or "has_iswap=true"
    const [depField, depValue] = field.depends_on.split('=');
    const currentValue = this.formGroup.get(depField)?.value;

    if (depValue !== undefined) {
      return String(currentValue) === depValue;
    }
    return !!currentValue; // Truthy check
  });
});
```

---

### Phase 4: Validation & Polish (1-2 hours)

#### 4.1 Add Field Validation

- Required fields
- Number ranges
- Custom validators

#### 4.2 Styling

- Match Material Design 3 theme
- Dark/light mode support
- Responsive layout

#### 4.3 Accessibility

- ARIA labels
- Keyboard navigation
- Screen reader support

---

## Files to Create/Modify

### Create

| File | Description |
|------|-------------|
| `praxis/backend/utils/plr_static_analysis/capability_config_templates.py` | Machine-type config templates |
| `src/app/shared/components/dynamic-capability-form/` | New Angular component |

### Modify

| File | Description |
|------|-------------|
| `praxis/backend/utils/plr_static_analysis/visitors/capability_extractor.py` | Add `build_capabilities_config()` |
| `praxis/backend/utils/plr_static_analysis/parser.py` | Pass config through pipeline |
| `src/app/features/assets/components/machine-dialog.component.ts` | Use dynamic form |
| `src/app/features/assets/models/asset.models.ts` | Already has TypeScript interfaces |

---

## Testing

### Unit Tests

- [ ] `test_capability_config_templates.py` - Template validation
- [ ] `test_capability_extractor.py` - Config generation
- [ ] `dynamic-capability-form.component.spec.ts` - Form rendering
- [ ] `machine-dialog.component.spec.ts` - Integration

### E2E Tests

- [ ] Create machine with dynamic form
- [ ] Verify capabilities saved correctly
- [ ] Test conditional field visibility
- [ ] Test fallback to JSON textarea

---

## Success Metrics

1. **UX**: No JSON typing required for common configurations
2. **Validation**: Invalid values prevented at input time
3. **Discoverability**: Users can see all available options
4. **Fallback**: JSON still works for edge cases

---

## Estimated Effort

| Phase | Effort | Priority |
|-------|--------|----------|
| Phase 1: Backend Schema | 2-3 hours | High |
| Phase 2: Frontend Component | 3-4 hours | High |
| Phase 3: Conditional Fields | 1-2 hours | Medium |
| Phase 4: Polish | 1-2 hours | Medium |
| **Total** | **7-11 hours** | |

---

## Related Backlogs

- [capability_tracking.md](./capability_tracking.md) - Phase 3 enhancement
- [protocol_execution.md](./protocol_execution.md) - Wizard state persistence
- [ui-ux.md](./ui-ux.md) - General UI items
