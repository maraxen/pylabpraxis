# Agent Prompt: Registry UI Browser Mode Improvements

Examine `.agents/README.md` for development context.

**Status:** 🟢 Not Started
**Priority:** P2
**Batch:** [260112](./README.md)
**Backlog Reference:** [asset_management.md](../../backlog/asset_management.md)

---

## 1. The Task

Fix the Registry UI issues in browser mode:
1. The "Add Machine" button incorrectly links to "Add Resource"
2. Add Resource shows confusing message: "definitions are precinct in browser mode" (typo: "precinct" should be "present")
3. Design a clearer registry interface that communicates browser mode limitations

**User Value:** Users understand what registry operations are available in browser mode and can navigate the asset management UI without confusion.

---

## 2. Technical Implementation Strategy

### Frontend Components

1. **Fix navigation in Registry component**
   - Locate where "Add Machine" is routed and fix the navigation path
   - Ensure both buttons route to their correct dialogs

2. **Improve browser mode messaging**
   - Fix typo "precinct" → "present" (or rephrase entirely)
   - Add informative messaging about what can/cannot be done in browser mode
   - Consider showing a read-only registry view with clear explanation

3. **Design improvements**
   - Add visual distinction between actions available in browser vs production mode
   - Consider disabling unavailable actions with tooltips explaining why

### Data Flow

1. User clicks "Add Machine" or "Add Resource" in Registry
2. System checks if in browser mode (via `BrowserModeService` or similar)
3. Either opens dialog or shows informative message about limitations

---

## 3. Context & References

**Primary Files to Modify:**

| Path | Description |
|:-----|:------------|
| `praxis/web-client/src/app/features/assets/components/` | Asset management components |
| `praxis/web-client/src/app/features/assets/assets.routes.ts` | Asset routing configuration |

**Reference Files (Read-Only):**

| Path | Description |
|:-----|:------------|
| `praxis/web-client/src/app/core/services/browser-mode.service.ts` | Browser mode detection |
| `praxis/web-client/src/app/features/assets/components/machine-dialog.component.ts` | Machine creation dialog |
| `praxis/web-client/src/app/features/assets/components/resource-dialog.component.ts` | Resource creation dialog |

---

## 4. Constraints & Conventions

- **Commands**: Use `uv run` for Python, `npm` for Angular.
- **Backend Path**: `praxis/backend`
- **Frontend Path**: `praxis/web-client`
- **Styling**: Use Tailwind utility classes where possible.
- **State**: Prefer Signals for new Angular components.

---

## 5. Verification Plan

**Definition of Done:**

1. The code compiles without errors:
   ```bash
   cd praxis/web-client && npm run build
   ```

2. Manual testing:
   - In browser mode, click "Add Machine" → should open machine dialog OR show clear browser mode message
   - In browser mode, click "Add Resource" → should open resource dialog OR show clear browser mode message
   - No typos in messaging

3. Accessibility: All new UI elements have appropriate ARIA labels

---

## On Completion

- [ ] Commit changes with descriptive message
- [ ] Update backlog item status in `asset_management.md`
- [ ] Update DEVELOPMENT_MATRIX.md if applicable
- [ ] Mark this prompt complete in batch README

---

## References

- `.agents/README.md` - Environment overview
