# Agent Prompt: Protocol Well Selection Fix

Examine `.agents/README.md` for development context.

**Status:** 🟢 Not Started
**Priority:** P1
**Batch:** 260109
**Backlog Reference:** Protocol well selection not triggering (P1)

---

## 1. The Task

The user cannot select wells for protocol parameters that require well input (e.g., "Source Wells"). The UI element for well selection appears to be either missing or unresponsive in the Protocol Run setup screen.

Your goal is to ensure that protocol parameters defined with a well-selection type correctly render the well selector UI and allow user selection.

---

## 2. Technical Implementation Strategy

### Current Architecture Analysis

**Well Selection is NOT in `ParameterConfigComponent`:**

The `ParameterConfigComponent` (at `praxis/web-client/src/app/features/run-protocol/components/parameter-config/parameter-config.component.ts`) handles general parameters with Formly, but well selection is handled **separately** in the main `RunProtocolComponent`.

**Actual Implementation Location:**

`praxis/web-client/src/app/features/run-protocol/run-protocol.component.ts` contains:
- `isWellSelectionParameter(param)` - Detects well parameters by name patterns or `ui_hint.type === 'well_selector'`
- `getWellParameters()` - Returns parameters that need well selection
- `openWellSelector(param)` - Opens `WellSelectorDialogComponent`
- `wellSelections` signal - Stores selections per parameter name

**Detection Logic (line ~1044-1062):**
```typescript
private isWellSelectionParameter(param: any): boolean {
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

**Backend Configuration:**

Parameters can have a `ui_hint` field (from `ParameterMetadataModel`):
- `ui_hint_json` stored in DB
- `UIHint` model has `widget_type: str | None`

To enable well selection for a parameter, either:
1. Name the parameter with "well" pattern (auto-detected)
2. Set `ui_hint: { type: 'well_selector' }` in parameter metadata

### Root Cause Investigation

The issue is likely one of:

1. **Template not rendering well selector section** - Check if `getWellParameters()` is returning an empty array when it shouldn't
2. **Parameter filtering removes well params** - `ParameterConfigComponent.buildForm()` filters parameters; ensure well params aren't filtered out entirely
3. **UI binding issue** - The template section for well selection may not be visible or clickable

### Files to Investigate

| Path | Description |
|------|-------------|
| `praxis/web-client/src/app/features/run-protocol/run-protocol.component.ts` | Main component with well selection logic (lines 1042-1110) |
| `praxis/web-client/src/app/features/run-protocol/run-protocol.component.html` | Template - look for well selector section |
| `praxis/web-client/src/app/shared/components/well-selector-dialog/` | Dialog component |
| `praxis/web-client/src/app/shared/formly-types/well-selector-field.component.ts` | Formly field (exists but may not be used) |

---

## 3. Context & References

**Primary Files to Modify:**

| Path | Description |
|------|-------------|
| `praxis/web-client/src/app/features/run-protocol/run-protocol.component.ts` | Well selection detection and handling |
| `praxis/web-client/src/app/features/run-protocol/run-protocol.component.html` | Template rendering |

**Supporting Components:**

| Path | Description |
|------|-------------|
| `praxis/web-client/src/app/shared/components/well-selector-dialog/well-selector-dialog.component.ts` | Dialog for well selection |
| `praxis/web-client/src/app/shared/formly-types/well-selector-field.component.ts` | Formly wrapper (may not be actively used) |

**Backend Models:**

| Path | Description |
|------|-------------|
| `praxis/backend/models/pydantic_internals/protocol.py` | `ParameterMetadataModel` with `ui_hint` field |
| `praxis/backend/models/pydantic_internals/protocol.py` | `UIHint` model with `widget_type` |

---

## 4. Constraints & Conventions

- **Commands**: Use `npm` for Angular operations (from `praxis/web-client/`)
- **Working Directory**: `cd praxis/web-client && npm test -- <spec>`
- **Formly Types**: The `well-selector` type exists but main well selection bypasses Formly
- **Signal State**: Uses Angular signals (`wellSelections`, `isStartingRun`, etc.)

---

## 5. Verification Plan

**Definition of Done:**

1. Well parameters are correctly detected by `isWellSelectionParameter()`
2. Well selection UI is visible and clickable in protocol run setup
3. Dialog opens and allows selection
4. Selected wells are stored in `wellSelections` signal
5. Selections are passed to protocol start request

**Verification Commands:**

```bash
cd praxis/web-client

# Run unit tests for run-protocol component
npm test -- run-protocol.component.spec

# Run tests for well selector dialog
npm test -- well-selector-dialog.component.spec

# Check for TypeScript errors
npm run build
```

**Debug Steps:**

1. Add console.log in `getWellParameters()` to see what's returned
2. Check if well selection section exists in template
3. Verify `selectedProtocol()` has parameters with well-related names or ui_hints

---

## On Completion

- [ ] Commit changes with message: `fix(ui): enable well selector for protocol parameters`
- [ ] Update backlog item status in `PROTOCOL_WORKFLOW.md` (or relevant backlog file)
- [ ] Mark this prompt complete in batch README and set the status in this prompt document to 🟢 Completed
