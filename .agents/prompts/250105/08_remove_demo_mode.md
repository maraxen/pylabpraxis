# Prompt 8: Remove Demo Mode Toggle

Remove the separate demo mode toggle and related code.

## Context

Browser mode IS the demo experience. Demo mode toggle is no longer needed.

## Tasks

1. Remove demo mode toggle from WelcomeDialogComponent (keep tutorial start)

2. Remove demo mode toggle from SettingsComponent

3. Delete ExitDemoDialogComponent entirely

4. Remove `isDemoMode()` from ModeService (browser mode implies simulation)

5. Remove `demoMode` signal from AppStore

6. Remove or refactor DemoInterceptor (may still be useful for mock API responses)

7. Update OnboardingService to remove demo state tracking

8. Update tutorial text to remove demo mode references

9. Test full flow: first visit, tutorial, settings

## Files to Modify/Delete

- `praxis/web-client/src/app/features/welcome-dialog/`
- `praxis/web-client/src/app/features/settings/`
- `praxis/web-client/src/app/core/services/mode.service.ts`
- `praxis/web-client/src/app/core/services/onboarding.service.ts`
- `praxis/web-client/src/app/core/interceptors/demo.interceptor.ts` (review)

## Reference

- `.agents/backlog/browser_mode_defaults.md`
