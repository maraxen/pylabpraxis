# Agent Prompt: 25_footer_navigation_layout

Examine `.agents/README.md` for development context.

**Status:** 🟢 Not Started  
**Batch:** [260109](../260109/README.md)  
**Backlog:** [ui_consistency.md](../../backlog/ui_consistency.md)  

---

## Task

Refactor the application layout to eliminate the main top header and implement a persistent footer bar with community and support links.

### Requirements

1. **Eliminate Header**:
    * Remove the `<header>` element from `praxis/web-client/src/app/layout/unified-shell.component.ts`.
    * Relocate the `<app-breadcrumb>` if necessary, or remove it if the UI remains intuitive without it (prefer relocation to a more subtle spot if needed).
2. **Implement Footer Bar**:
    * Add a thin, elegant footer bar at the bottom of the `main-wrapper` in `unified-shell.component.ts`.
    * Ensure it matches the application's glassmorphism/themed aesthetics.
3. **Footer Content**:
    * **GitHub**: Small icon link to the repository.
    * **GitHub Star**: A link or button to "Star" the repository.
    * **Raise an Issue**: A link to the GitHub "New Issue" form.
    * **LabAutomation.io**: Link to the Discourse forum.
    * **PyLabRobot.org**: Link to the PyLabRobot Discourse forum.
4. **Styling**:
    * The footer should be persistent and non-intrusive.
    * Use icons (e.g., from FontAwesome or Material Icons) where appropriate.

---

## Context Files

| File | Purpose |
|:-----|:--------|
| [ui_consistency.md](../../backlog/ui_consistency.md) | Backlog tracking |
| [unified-shell.component.ts](../../../praxis/web-client/src/app/layout/unified-shell.component.ts) | Layout implementation |

---

## Project Conventions

* **Frontend Styling**: Use Vanilla CSS in the `@Component` decorator.
* **Icons**: Use `MatIconModule` or custom SVG icons if needed.
* **Frontend Tests**: `cd praxis/web-client && npm test`

---

## On Completion

* [x] Commit changes with descriptive message
* [x] Update [ui_consistency.md](../../backlog/ui_consistency.md) status (Phase 6)
* [x] Update [DEVELOPMENT_MATRIX.md](../../DEVELOPMENT_MATRIX.md) status
* [x] Mark this prompt complete in [README.md](./README.md)

---

## References

* [.agents/README.md](../../README.md) - Environment overview
* [DEVELOPMENT_MATRIX.md](../../DEVELOPMENT_MATRIX.md)
