# Agent Prompt: Update Shepherd Tutorial Steps

Examine `.agents/README.md` for development context.

**Status:** 🟢 Not Started
**Priority:** P2
**Difficulty:** Medium
**Batch:** [260109](./README.md)
**Backlog Reference:** [docs.md](../../backlog/docs.md#p2-tutorial-updates)

---

## 1. The Task

The in-app guided tutorial (Shepherd.js tour) needs to be updated to reflect current UI structure and navigation. The tutorial steps may reference outdated element selectors, missing features, or changed workflows.

**Goal:** Review and update the `TutorialService` to ensure all tutorial steps work correctly with the current UI.

**User Value:** New users get a functional, accurate in-app guided tutorial that properly introduces them to Praxis features.

---

## 2. Technical Implementation Strategy

### Current Implementation

**Tutorial Service:** `praxis/web-client/src/app/core/services/tutorial.service.ts`

Uses Shepherd.js for guided tours with:
- 13 tutorial steps covering: Dashboard, Assets, Protocols, Run Wizard, Playground, Settings
- `data-tour-id` attributes on UI elements for attachment
- Route navigation with `beforeShowPromise` for async transitions
- Section skipping via `skipSection()` method
- Progress persistence via `OnboardingService`

### Tutorial Steps (Current)

| Step ID | Title | Route | Selector |
|---------|-------|-------|----------|
| `intro` | Welcome to Praxis | `/app/home` | `[data-tour-id="dashboard-root"]` |
| `nav-assets` | Asset Management | - | `[data-tour-id="nav-assets"]` |
| `assets-machines` | Machines | `/app/assets?type=machine` | `[data-tour-id="add-asset-btn"]` |
| `assets-resources` | Labware Resources | `/app/assets?type=resource` | `[data-tour-id="resource-list"]` |
| `nav-protocols` | Protocols | - | `[data-tour-id="nav-protocols"]` |
| `protocols-import` | Import Protocols | `/app/protocols` | `[data-tour-id="import-protocol-btn"]` |
| `nav-run` | Run Protocol | - | `[data-tour-id="nav-run"]` |
| `run-step-protocol` | 1. Select Protocol | `/app/run` | `[data-tour-id="run-step-label-protocol"]` |
| `run-step-params` | 2. Configure Parameters | - | `[data-tour-id="run-step-label-params"]` |
| `run-step-machine` | 3. Select Machine | - | `[data-tour-id="run-step-label-machine"]` |
| `run-step-assets` | 4. Map Assets | - | `[data-tour-id="run-step-label-assets"]` |
| `run-step-deck` | 5. Deck Setup | - | `[data-tour-id="run-step-label-deck"]` |
| `nav-playground` | Playground | - | `[data-tour-id="nav-playground"]` |
| `playground-term` | Playground Notebook | `/app/playground` | `[data-tour-id="repl-notebook"]` |
| `nav-settings` | Settings | - | `[data-tour-id="nav-settings"]` |
| `settings-finish` | You're All Set! | `/app/settings` | `[data-tour-id="settings-onboarding"]` |

### Review Checklist

For each step, verify:

1. **Selector exists**: Does `[data-tour-id="X"]` exist in the current UI?
2. **Route works**: Does the route/queryParams combination load correctly?
3. **Element visible**: Is the element visible when the step shows?
4. **Text accurate**: Does the step text describe current functionality?
5. **advanceOn works**: If using click-to-advance, does the element exist?

### Common Issues to Fix

1. **Missing `data-tour-id` attributes**: Add to templates where needed
2. **Changed routes or query params**: Update step configuration
3. **Outdated descriptions**: Update step text to match current UI
4. **Missing waitFor elements**: Adjust selectors or add fallbacks
5. **Section boundaries**: Update `sectionMap` in `skipSection()` if steps changed

---

## 3. Context & References

**Primary Files to Modify:**

| Path | Description |
|:-----|:------------|
| `praxis/web-client/src/app/core/services/tutorial.service.ts` | Tutorial step definitions (305 lines) |
| Component templates with `data-tour-id` | May need to add/update selectors |

**Supporting Files:**

| Path | Description |
|:-----|:------------|
| `praxis/web-client/src/app/layout/unified-shell.component.ts` | Navigation with tour IDs |
| `praxis/web-client/src/app/features/home/home.component.ts` | Dashboard with `dashboard-root` |
| `praxis/web-client/src/app/core/services/onboarding.service.ts` | Tutorial state persistence |
| `praxis/web-client/src/styles/shepherd-theme.scss` | Tutorial styling |

**Templates to Check for `data-tour-id`:**

```bash
grep -r "data-tour-id" praxis/web-client/src/app/
```

---

## 4. Constraints & Conventions

- **Commands**: Use `npm` from `praxis/web-client/`
- **Shepherd.js**: Version 14.5.1 (see package.json)
- **Selectors**: Use `[data-tour-id="X"]` pattern for tour attachment
- **Signal State**: Component uses Angular signals
- **Routing**: Steps use `beforeShowPromise` for async navigation

**Step Configuration Pattern:**

```typescript
this.addStep({
    id: 'step-id',
    title: 'Step Title',
    text: 'Description text. Can include <strong>HTML</strong>.',
    attachTo: { element: '[data-tour-id="element-id"]', on: 'bottom' },
    route: '/app/route',           // Optional: navigate before showing
    queryParams: { key: 'value' }, // Optional: route query params
    waitFor: '[selector]',         // Optional: wait for element
    advanceOn: { selector: '[data-tour-id="X"]', event: 'click' }, // Optional
    buttons: [...]                 // Optional: custom buttons
});
```

---

## 5. Verification Plan

**Definition of Done:**

1. All tutorial steps display correctly
2. All selectors attach to visible elements
3. Route navigation works for each step
4. Step text accurately describes current UI
5. "Skip Section" advances to correct next section
6. Tutorial can be completed start to finish

**Verification Commands:**

```bash
cd praxis/web-client

# Build to catch TypeScript errors
npm run build

# Find all tour IDs in templates
grep -rn "data-tour-id" src/app/ --include="*.ts" --include="*.html"

# Run the app and test tutorial manually
npm start
```

**Manual Testing:**

1. Start app in browser mode
2. Navigate to Settings → Start Tutorial
3. Follow all steps, verifying each one:
   - Element highlights correctly
   - Text is accurate
   - Navigation works
   - Buttons function
4. Test "Skip Section" at various points
5. Test resume functionality (cancel, then restart)

---

## On Completion

- [ ] Commit changes with message: `fix(tutorial): update Shepherd tour steps for current UI`
- [ ] Update backlog item status
- [ ] Mark this prompt complete in batch README and set the status in this prompt document to 🟢 Completed
