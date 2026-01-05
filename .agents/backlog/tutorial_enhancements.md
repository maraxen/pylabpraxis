# Tutorial Enhancements

**Priority:** P2  
**Status:** Planning  
**Created:** 2026-01-05  
**Depends On:** Tutorial & Demo Mode (Complete)

## Summary

Two enhancements needed for the guided tutorial:

1. **Theme Sync**: Shepherd.js popovers must match the app's light/dark theme.
2. **Interactive Navigation**: Tutorial should navigate users into each feature page, not just highlight nav items.

### User Requirements (Added 2026-01-05)

1. **Click-to-Advance**: Allow users to click actual UI elements to advance (e.g., clicking "Add Machine" button moves to next step).
2. **Detailed Run Wizard**: Expand the Run Protocol step to cover all sub-steps of the wizard (Parameters, Machine Selection, Asset Selection, Deck Setup).
3. **Session-Based Tracking**:
    - Track completed steps *per tutorial session* (since last toggle).
    - If user manually restarts tutorial via Settings, reset this session state to show everything fresh.
    - If user pauses/leaves and comes back, resume where they left off (or skip completed steps).

---

## Issue 1: Light/Dark Mode Sync

### Problem

The Shepherd.js default styles use their own colors, creating a jarring visual mismatch when the app is in light or dark mode.

### Proposed Solution

1. **Create Custom Shepherd Theme CSS**:
    - Add a new file: `src/styles/shepherd-theme.scss`.
    - Override Shepherd's default classes (`.shepherd-element`, `.shepherd-header`, `.shepherd-text`, `.shepherd-button`) to use `var(--mat-sys-*)` CSS variables.
    - Example:

        ```scss
        .shepherd-element {
            background: var(--mat-sys-surface-container-high);
            color: var(--theme-text-primary);
            border: 1px solid var(--theme-border);
        }
        .shepherd-button {
            background: var(--mat-sys-primary);
            color: white;
        }
        .shepherd-button-secondary {
            background: transparent;
            color: var(--theme-text-secondary);
        }
        ```

2. **Import in `styles.scss`**: Replace or supplement the default `shepherd.js/dist/css/shepherd.css` import.
3. **Dynamic Updates (Optional)**: If theme changes mid-tour, the CSS variables will auto-update since they are defined at `:root` and `.light-theme`.

### Acceptance Criteria

- [ ] Tutorial popovers match dark theme (default)
- [ ] Tutorial popovers match light theme when toggled
- [ ] No jarring color transitions

---

## Issue 2: Feature-by-Feature Interactive Navigation

### Problem

Currently, the tutorial steps just highlight navigation items from the home page. Users don't actually visit each section, so they don't get hands-on exposure to the features.

### Proposed Solution

Restructure the tutorial into **interactive "chapters"** where each step:

1. **Navigates** to the target page via `beforeShowPromise`.
2. **Waits** for content to render (short delay or `waitForSelector`-like logic).
3. **Highlights** a key element *on that page* (not the nav item).
4. **Describes** what the user can do there.
5. **Optionally prompts** user interaction (e.g., "Click 'Add Machine' to try it").

### Proposed Step Flow

| Step | Page | Highlight | Description | Interaction |
|------|------|-----------|-------------|-------------|
| 1 | `/app/home` | Dashboard Stats | "This is your dashboard. See running experiments and quick stats." | Next Button |
| 2 | `/app/assets` | Assets Nav Item | "Click here to manage your lab inventory." | **Click Nav** |
| 3 | `/app/assets` | Machines Tab | "Here are your liquid handlers. Click 'Add Machine' to define a new one." | **Click Add** |
| 4 | `/app/assets` | Resources Tab | "View and add labware resources (plates, tips, etc.)." | Next Button |
| 5 | `/app/protocols` | Protocols Nav Item | "Click here to manage protocols." | **Click Nav** |
| 6 | `/app/protocols` | Import Button | "Import new Python protocols here." | Next Button |
| 7 | `/app/run` | Run Nav Item | "Let's set up a run. Click here." | **Click Nav** |
| **8a** | `/app/run` | Protocol Selector | "First, select the protocol to run." | Next Button |
| **8b** | `/app/run` | Parameters Step | "Enter run parameters defined in your script." | Next Button |
| **8c** | `/app/run` | Machine Selection | "Choose the available machine for this run." | Next Button |
| **8d** | `/app/run` | Asset Selection | "Map required labware to your inventory items." | Next Button |
| **8e** | `/app/run` | Deck Setup | "Verify the deck layout visually." | Next Button |
| 9 | `/app/repl` | REPL Nav Item | "Click to access the Python console." | **Click Nav** |
| 10 | `/app/visualizer` | Deck Nav Item | "Click to visualize your robot deck." | **Click Nav** |
| 11 | `/app/settings` | Settings Nav Item | "Finally, let's look at settings." | **Click Nav** |
| 12 | `/app/settings` | Tutorial/Demo | "You can restart this tutorial or toggle demo mode here." | Finish Button |

### Technical Notes

- Use `beforeShowPromise` to navigate and wait:

    ```typescript
    beforeShowPromise: () => {
        return this.router.navigate(['/app/assets']).then(() => {
            return new Promise(resolve => setTimeout(resolve, 500)); // Wait for render
        });
    }
    ```

- Add `data-tour-id` attributes to key elements on each page (e.g., `[data-tour-id="machine-list"]`, `[data-tour-id="protocol-table"]`).
- Consider using Shepherd's `advanceOn` to allow user clicks to advance the tour (e.g., click "Add Machine" progresses to next step).

### Acceptance Criteria

- [ ] Tutorial navigates user to each page
- [ ] Key UI element on each page is highlighted (not just nav)
- [ ] Tutorial is ~13 steps covering all major features
- [ ] User can exit tour at any time
- [ ] Tour resumes gracefully if interrupted (optional/stretch)

---

## Files to Modify

| File | Change |
|------|--------|
| `src/styles/shepherd-theme.scss` | **[NEW]** Custom theme overrides |
| `src/styles.scss` | Import custom theme |
| `core/services/tutorial.service.ts` | Update steps, add navigation & wait logic |
| `features/assets/*` | Add `data-tour-id` to key elements |
| `features/protocols/*` | Add `data-tour-id` to key elements |
| `features/run-protocol/*` | Add `data-tour-id` to key elements |
| `features/repl/*` | Add `data-tour-id` to key elements |
| `features/data/*` | Add `data-tour-id` to key elements |
| `features/execution-monitor/*` | Add `data-tour-id` to key elements |
| `features/visualizer/*` | Add `data-tour-id` to key elements |
| `features/settings/*` | Add `data-tour-id` to key elements |

---

## Estimated Effort

| Task | Difficulty |
|------|------------|
| Theme Sync CSS | S (1-2 hours) |
| Interactive Navigation | M (4-6 hours) |
| Adding `data-tour-id` attributes | S (1-2 hours) |
| Testing & Polish | S (1-2 hours) |

**Total:** M-L (8-12 hours)
