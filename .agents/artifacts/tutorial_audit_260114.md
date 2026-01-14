# Tutorial Audit - Jan 2026

## Summary

- **Total Steps:** 13
- **Steps Working:** 13/13 verified against codebase selectors.
- **Critical Issues:** 0 functional breaks.
- **UX Issues:** 1 major confusion regarding completion state ("Resetting" feeling).

## Detailed Verification

All `data-tour-id` selectors referenced in `TutorialService` were found in the codebase templates.

| Step ID | Title | Route | Status | Selector Found In |
|:--------|:------|:------|:-------|:------------------|
| intro | Welcome to Praxis | `/app/home` | ✅ Verified | `HomeComponent` |
| nav-assets | Asset Management | - | ✅ Verified | `UnifiedShellComponent` |
| assets-machines | Machines | `/app/assets?type=machine` | ✅ Verified | `AssetsComponent` |
| assets-resources | Labware Resources | `/app/assets?type=resource` | ✅ Verified | `AssetsComponent` |
| nav-protocols | Protocols | - | ✅ Verified | `UnifiedShellComponent` |
| protocols-import | Import Protocols | `/app/protocols` | ✅ Verified | `ProtocolLibraryComponent` |
| nav-run | Run Protocol | - | ✅ Verified | `UnifiedShellComponent` |
| run-step-protocol | 1. Select Protocol | `/app/run` | ✅ Verified | `RunProtocolComponent` |
| run-step-params | 2. Configure Parameters | - | ✅ Verified | `RunProtocolComponent` |
| run-step-machine | 3. Select Machine | - | ✅ Verified | `RunProtocolComponent` |
| run-step-assets | 4. Map Assets | - | ✅ Verified | `RunProtocolComponent` |
| run-step-deck | 5. Deck Setup | - | ✅ Verified | `RunProtocolComponent` |
| nav-playground | Playground | - | ✅ Verified | `UnifiedShellComponent` |
| playground-term | Playground Notebook | `/app/playground` | ✅ Verified | `PlaygroundComponent` |
| nav-settings | Settings | - | ✅ Verified | `UnifiedShellComponent` |
| settings-finish | You're All Set! | `/app/settings` | ✅ Verified | `SettingsComponent` |

## Issues Found

### Issue 1: End of Tutorial "Reset" Confusion

- **Symptoms:** User reports "end of tutorial resetting".
- **Root Cause:** When the tutorial finishes:
    1. `TutorialService.onComplete()` runs, calling `onboarding.clearTutorialState()`.
    2. The user is left on the **Settings** page (`SettingsComponent`).
    3. The "Onboarding" card in Settings checks `hasTutorialProgress()`.
    4. Since state is cleared, `hasTutorialProgress()` is `false`.
    5. The UI defaults to showing a primary button **"Start Tutorial"** with text "Start the interactive tour of features".
    6. This gives the user the impression that their progress was lost or the system reset, rather than acknowledging completion.
- **Fix:** Update `SettingsComponent` to check `onboarding.hasCompletedTutorial()` (which is signal-based and persistent) and update the UI accordingly (e.g., "Tutorial Completed", "Restart Tutorial").

### Issue 2: Feature Accuracy Checks

- **Browser Mode Upload:** Step `protocols-import` states upload is not available in browser mode.
  - **Verification:** `ProtocolService.uploadProtocol` performs a direct HTTP POST, which is not intercepted by Browser Mode logic.
  - **Status:** ✅ Accurate (Constraint exists).
- **Infinite Consumables:** Step `settings-finish` mentions "Infinite Consumables".
  - **Verification:** `SettingsComponent` contains the "Infinite Consumables" toggle.
  - **Status:** ✅ Accurate.

## Recommended Changes

### Fix Prompts to Generate

| # | Type | Title | Purpose |
|---|------|-------|---------|
| G-03 | Implementation | Fix Tutorial Completion UI | Updates `SettingsComponent` to properly reflect completed tutorial state, fixing the "reset" confusion. |
