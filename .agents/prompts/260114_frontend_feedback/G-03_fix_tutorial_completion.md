# Agent Prompt: G-03 Fix Tutorial Completion UI

**Status:** ✅ Completed
**Priority:** P2
**Batch:** [260114_frontend_feedback](./README.md)
**Difficulty:** Easy
**Type:** 🛠 Implementation
**Dependencies:** None
**Context:** [Tutorial Audit Result](../artifacts/tutorial_audit_260114.md)

---

## 1. The Task

**User Story:**
As a user finishing the tutorial, I want clearly see that I have completed it on the Settings page, instead of being prompted to "Start Tutorial" again, so that I don't feel like my progress was lost.

**Objectives:**

1. Update `SettingsComponent` to distinguish between "Not Started", "In Progress", and "Completed" states for the tutorial.
2. If completed, show "Restart Tutorial" (maybe with a checkmark or specific text).
3. Ensure `OnboardingService` signals are used correctly.

---

## 2. Implementation Details

**File:** `praxis/web-client/src/app/features/settings/components/settings.component.ts`

**Current Logic:**

```typescript
hasTutorialProgress(): boolean {
  return this.onboarding.getTutorialState() !== null;
}
// Template:
// {{ hasTutorialProgress() ? 'Resume...' : 'Start...' }}
// {{ hasTutorialProgress() ? 'Restart' : 'Start Tutorial' }}
```

**Required Changes:**

1. Use `onboarding.hasCompletedTutorial()` signal.
2. Update template logic:
   - **In Progress:** Text: "Resume or restart...", Button 1: "Resume", Button 2: "Restart"
   - **Completed:** Text: "You have completed the tour. Feel free to restart it anytime.", Button: "Restart Tutorial" (Primary or Accent)
   - **Not Started:** Text: "Start the interactive tour...", Button: "Start Tutorial"

**Style Guide:**

- Use existing `mat-card` styles.
- Add a green check icon or similar indicator if completed (optional, use `mat-icon`).

---

## 3. Verification

**Manual Check:**

1. Finish tutorial -> Check Settings text.
2. Clear storage/reset -> Check Settings text.
3. Start and leave -> Check Settings text.

**Automated Tests:**

- Update `settings.component.spec.ts` if it checks these states.

---

## 4. Constraints

- Do not change `TutorialService` logic (the reset of state is correct).
- Only modify the presentation in `SettingsComponent`.
