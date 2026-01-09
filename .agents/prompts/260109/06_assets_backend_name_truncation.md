# Agent Prompt: Backend Name Truncation

Examine `.agents/README.md` for development context.

**Status:** 🟢 Completed
**Priority:** P2
**Batch:** [260109](./README.md)
**Backlog Reference:** [asset_management.md](../../backlog/asset_management.md)

---

## 1. The Task

The backend selector in the Machine Dialog displays backend names that are too long to be useful. Names like `pylabrobot.liquid_handling.backends.hamilton.HamiltonSTARBackend` overflow their containers and make it hard to compare options.

The task is to implement intelligent name truncation with tooltips showing the full name on hover.

**User Value:** Users can quickly scan and select backends without UI clutter, while still having access to full names when needed.

---

## 2. Technical Implementation Strategy

### Architecture

**Component:** `MachineDialogComponent`

- Located at: `praxis/web-client/src/app/features/assets/components/machine-dialog.component.ts`

**Current Implementation (lines 137-163):**

```typescript
<div class="grid grid-cols-1 md:grid-cols-2 gap-3 max-h-[300px] overflow-y-auto pr-1">
  @for (def of filteredBackends; track def.accession_id) {
    <button type="button" class="selection-card definition-card" ...>
      <div class="flex items-start gap-3 w-full">
        <div class="icon-chip subtle">
          <mat-icon>memory</mat-icon>
        </div>
        <div class="flex flex-col items-start min-w-0">
          <div class="flex items-center gap-2 w-full">
            <span class="font-medium truncate">{{ def.name }}</span>  <!-- Name -->
            ...
          </div>
          <span class="text-xs sys-text-secondary truncate">
            {{ def.manufacturer || 'Unknown vendor' }}
          </span>
          <span class="text-[11px] text-sys-text-tertiary fqn-wrap">{{ getShortFqn(def.fqn || '') }}</span>  <!-- FQN -->
        </div>
      </div>
    </button>
  }
</div>
```

### Current `getShortFqn` Implementation (line 536)

```typescript
getShortFqn(fqn: string): string {
  const parts = fqn.split('.');
  return parts.length > 2 ? parts.slice(-2).join('.') : fqn;
}
```

This already shortens FQN but may need enhancement.

### Proposed Changes

1. **Enhance name display with truncation + tooltip:**

   ```html
   <span class="font-medium truncate" 
         [matTooltip]="def.name" 
         matTooltipShowDelay="300">
     {{ getTruncatedName(def.name) }}
   </span>
   ```

2. **Add `getTruncatedName` method:**

   ```typescript
   getTruncatedName(name: string, maxLength: number = 25): string {
     if (name.length <= maxLength) return name;
     return name.substring(0, maxLength - 3) + '...';
   }
   ```

3. **Improve FQN display with tooltip:**

   ```html
   <span class="text-[11px] text-sys-text-tertiary fqn-wrap"
         [matTooltip]="def.fqn"
         matTooltipShowDelay="300">
     {{ getShortFqn(def.fqn || '') }}
   </span>
   ```

4. **Consider extracting display-friendly name from FQN:**
   - `pylabrobot.liquid_handling.backends.hamilton.HamiltonSTARBackend` → `HamiltonSTARBackend`
   - Show class name prominently, full path in tooltip

### Data Flow

1. Backend definitions loaded from `AssetService.getMachineDefinitions()`
2. Definitions contain `name`, `fqn`, `manufacturer` properties
3. Template displays with truncation
4. Tooltip shows full value on hover

---

## 3. Context & References

**Primary Files to Modify:**

| Path | Description |
|:-----|:------------|
| `praxis/web-client/src/app/features/assets/components/machine-dialog.component.ts` | Add truncation methods and tooltips |

**Reference Files (Read-Only):**

| Path | Description |
|:-----|:------------|
| `praxis/web-client/src/app/features/assets/services/asset.service.ts` | Backend definition data source |
| `praxis/web-client/src/app/features/assets/models/asset.models.ts` | MachineDefinition interface |

---

## 4. Constraints & Conventions

- **Commands**: Use `npm` for Angular commands
- **Frontend Path**: `praxis/web-client`
- **Styling**: Use existing Tailwind classes (`truncate`, `text-xs`, etc.)
- **Tooltips**: Use `MatTooltipModule` (already imported)
- **Accessibility**: Tooltips provide full context for screen readers

---

## 5. Verification Plan

**Definition of Done:**

1. The code compiles without errors:

   ```bash
   cd praxis/web-client && npm run build
   ```

2. Visual verification:
   - Navigate to Assets → Machines → Add Machine
   - Select a machine type (e.g., Liquid Handler)
   - Step 2 (Backend Selection) shows:
     - Names truncated to readable length
     - FQNs shortened to last 2 segments
   - Hover over truncated text shows full value in tooltip
   - Cards maintain consistent height regardless of name length

3. No regressions:
   - Backend selection still works
   - Selected backend populates form correctly
   - All backend types display properly

---

## On Completion

- [ ] Commit changes with message: `feat(assets): truncate backend names with tooltips`
- [ ] Update backlog item status in [asset_management.md](../../backlog/asset_management.md)
- [ ] Mark this prompt complete in batch README, update DEVELOPMENT_MATRIX.md if applicable, and set the status in this prompt document to 🟢 Completed

---

## References

- `.agents/README.md` - Environment overview
- `.agents/codestyles/typescript.md` - TypeScript conventions
