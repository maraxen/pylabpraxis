# Agent Prompt: G-P1 Tutorial Audit (Planning)

Examine `.agents/README.md` for development context.

**Status:** 🟢 Not Started
**Priority:** P2
**Batch:** [260114_frontend_feedback](./README.md)
**Difficulty:** Medium
**Type:** 🔵 Planning (Audit)
**Dependencies:** None
**Backlog Reference:** [GROUP_G_documentation_init.md](./GROUP_G_documentation_init.md)

---

## 1. The Task

**User Feedback:**
> "end of tutorial resetting, also auditing tutorial"

**Goals:**

1. Investigate the "end of tutorial resetting" issue
2. Audit the tutorial for accuracy after recent UI changes
3. Output: A detailed audit document with specific fix prompts

---

## 2. Initial Analysis (From Reconnaissance)

### Tutorial Implementation

The tutorial is implemented in `praxis/web-client/src/app/core/services/tutorial.service.ts` using **Shepherd.js**.

**Key Findings:**

1. **Tour Structure:** 13 steps covering Dashboard, Assets, Protocols, Run Wizard, Playground, and Settings

2. **State Management:**
   - `OnboardingService.saveTutorialStep(stepId)` saves progress on each step
   - `OnboardingService.startTutorialSession()` starts a fresh session
   - `OnboardingService.markTutorialComplete()` marks completion
   - `OnboardingService.clearTutorialState()` clears saved state

3. **Potential Reset Issue (lines 299-303):**

   ```typescript
   private onComplete() {
       this.onboarding.markTutorialComplete();
       this.onboarding.clearTutorialState();  // This clears step progress!
       this.tour.complete();
   }
   ```

   The `clearTutorialState()` call may be causing the reset issue if the user expects to see completion status preserved.

4. **Resume Logic (lines 51-63):**

   ```typescript
   start(resume: boolean = false) {
       if (resume) {
           const state = this.onboarding.getTutorialState();
           if (state && state.stepId) {
               this.tour.show(state.stepId);
               return;
           }
       }
       // Start fresh
       this.onboarding.startTutorialSession();
       this.tour.start();
   }
   ```

---

## 3. Audit Scope

### Tutorial Steps to Verify

| Step ID | Title | Attachs To | Route | Concerns |
|:--------|:------|:-----------|:------|:---------|
| intro | Welcome to Praxis | `[data-tour-id="dashboard-root"]` | `/app/home` | Does element exist? |
| nav-assets | Asset Management | `[data-tour-id="nav-assets"]` | - | Selector still valid? |
| assets-machines | Machines | `[data-tour-id="add-asset-btn"]` | `/app/assets?type=machine` | Tab structure changed? |
| assets-resources | Labware Resources | `[data-tour-id="resource-list"]` | `/app/assets?type=resource` | Selector valid? |
| nav-protocols | Protocols | `[data-tour-id="nav-protocols"]` | - | Navigation exists? |
| protocols-import | Import Protocols | `[data-tour-id="import-protocol-btn"]` | `/app/protocols` | Button still exists? |
| nav-run | Run Protocol | `[data-tour-id="nav-run"]` | - | Navigation exists? |
| run-step-protocol | 1. Select Protocol | `[data-tour-id="run-step-label-protocol"]` | `/app/run` | Wizard unchanged? |
| run-step-params | 2. Configure Parameters | `[data-tour-id="run-step-label-params"]` | - | Step exists? |
| run-step-machine | 3. Select Machine | `[data-tour-id="run-step-label-machine"]` | - | Step exists? |
| run-step-assets | 4. Map Assets | `[data-tour-id="run-step-label-assets"]` | - | Step exists? |
| run-step-deck | 5. Deck Setup | `[data-tour-id="run-step-label-deck"]` | - | Step exists? |
| nav-playground | Playground | `[data-tour-id="nav-playground"]` | - | Navigation exists? |
| playground-term | Playground Notebook | `[data-tour-id="repl-notebook"]` | `/app/playground` | Component exists? |
| nav-settings | Settings | `[data-tour-id="nav-settings"]` | - | Navigation exists? |
| settings-finish | You're All Set! | `[data-tour-id="settings-onboarding"]` | `/app/settings` | Section exists? |

### Verification Tasks

1. **Selector Audit:** Check each `data-tour-id` exists in current codebase
2. **Route Audit:** Verify routes still exist and work
3. **UI Accuracy:** Descriptions match current UI
4. **Feature Accuracy:** Features mentioned still work (e.g., "Infinite Consumables")
5. **Browser Mode Note:** Step 6 mentions protocol upload limitation - still accurate?

---

## 4. Investigation Commands

```bash
# Find all data-tour-id attributes in codebase
cd praxis/web-client
grep -r "data-tour-id" src/app --include="*.html" --include="*.ts"

# Check OnboardingService implementation
cat src/app/core/services/onboarding.service.ts

# Verify tutorial step routes
grep -r "path.*app/home\|path.*app/assets\|path.*app/protocols\|path.*app/run\|path.*app/playground\|path.*app/settings" src/app
```

---

## 5. Output Format

Create an audit document: `.agents/artifacts/tutorial_audit_260114.md`

**Document Structure:**

```markdown
# Tutorial Audit - Jan 2026

## Summary
- Total Steps: X
- Steps Working: X  
- Steps Needing Update: X

## Issues Found

### Issue 1: [Title]
- **Step:** step-id
- **Problem:** Description
- **Fix:** Specific change needed

## Recommended Changes

### Fix Prompts to Generate
| # | Type | Title | Steps Affected |
|---|------|-------|----------------|
| G-03 | Implementation | Fix Tutorial Step Selectors | 3, 5, 7 |
```

---

## 6. Context & References

**Primary Files to Investigate:**

| Path | Description |
|:-----|:------------|
| `praxis/web-client/src/app/core/services/tutorial.service.ts` | Tutorial steps definition |
| `praxis/web-client/src/app/core/services/onboarding.service.ts` | State persistence |

**Files to Search for Selectors:**

| Path | Description |
|:-----|:------------|
| `praxis/web-client/src/app/features/home/` | Dashboard components |
| `praxis/web-client/src/app/features/assets/` | Assets components |
| `praxis/web-client/src/app/features/protocols/` | Protocols components |
| `praxis/web-client/src/app/features/run/` | Run wizard components |
| `praxis/web-client/src/app/features/playground/` | Playground components |
| `praxis/web-client/src/app/features/settings/` | Settings components |

---

## 7. Constraints & Conventions

- **Commands**: Use `npm` for Angular, `grep` for searching
- **Frontend Path**: `praxis/web-client`
- **Output**: Write audit findings to `.agents/artifacts/`
- **This is a PLANNING task**: Do not implement fixes, only document what needs fixing

---

## 8. Verification

**Definition of Done:**

1. Audit document created with all findings
2. Each tutorial step verified
3. Reset issue root cause identified
4. Follow-up implementation prompts identified

---

## On Completion

- [ ] Create audit document in `.agents/artifacts/`
- [ ] List specific issues found
- [ ] Generate follow-up prompt specs (G-03+)
- [ ] Update backlog item status
- [ ] Mark this prompt complete in batch README

---

## References

- `.agents/README.md` - Environment overview
- `.agents/backlog/docs.md` - Documentation backlog (P2: Tutorial Updates)
