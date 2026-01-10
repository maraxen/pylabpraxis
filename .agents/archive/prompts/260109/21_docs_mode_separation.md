# Agent Prompt: Add Mode Separation to Architecture Docs

Examine `.agents/README.md` for development context.

**Status:** 🟢 Not Started
**Priority:** P2
**Difficulty:** Medium
**Batch:** [260109](./README.md)
**Backlog Reference:** [docs.md](../../backlog/docs.md#p2-mode-separation-in-architecture-docs)

---

## 1. The Task

The architecture documentation should have separate tabs or sections for browser-lite mode vs production mode, as these have significantly different architectures and capabilities.

**Goal:** Add tabbed or sectioned views in architecture docs that clearly distinguish browser-lite mode from production mode.

**User Value:** Users can understand the architectural differences between modes and know what features are available in each.

---

## 2. Technical Implementation Strategy

**Approach:**

Create a tabbed component or use markdown conventions to separate mode-specific content in the architecture overview and backend documentation.

**Options:**

1. **Custom Tab Component**: Create a reusable `DocsTabs` component for mode switching
2. **Markdown Convention**: Use HTML in markdown to create tab-like sections
3. **Separate Pages**: Create `overview-browser.md` and `overview-production.md` with navigation

**Recommended: Markdown with Toggle Pattern**

Use a collapsible/expandable section pattern with custom CSS styling.

**Content to Separate:**

| Topic | Browser Mode | Production Mode |
|-------|--------------|-----------------|
| Database | In-memory SQLite via Pyodide | PostgreSQL/SQLite file |
| Backend | None (all frontend) | FastAPI server |
| Hardware | WebSerial/WebUSB direct | Backend mediated |
| Execution | Frontend Pyodide | Backend Celery workers |

---

## 3. Context & References

**Primary Files to Modify:**

| Path | Description |
|:-----|:------------|
| `praxis/web-client/src/assets/docs/architecture/overview.md` | Main architecture overview |
| `praxis/web-client/src/assets/docs/architecture/backend.md` | Backend-specific docs |
| `praxis/web-client/src/app/features/docs/components/docs-page.component.ts` | Add tab styling support if needed |

**Reference Files (Read-Only):**

| Path | Description |
|:-----|:------------|
| `praxis/web-client/src/assets/docs/getting-started/browser-mode.md` | Browser mode reference |

---

## 4. Constraints & Conventions

- **Commands**: Use `npm` for Angular tasks
- **Frontend Path**: `praxis/web-client`
- **Documentation Format**: Markdown
- **Styling**: Use existing docs CSS variables

**Implementation Option A - Markdown with HTML Tabs:**

```markdown
# Architecture Overview

<div class="mode-tabs">
  <input type="radio" name="mode-tab" id="browser-tab" checked>
  <label for="browser-tab">Browser Mode</label>
  <input type="radio" name="mode-tab" id="production-tab">
  <label for="production-tab">Production Mode</label>

  <div class="tab-content browser-content">
    ## Browser Mode Architecture

    In browser mode, Praxis runs entirely in the browser...

    ```mermaid
    flowchart TB
      Browser[Browser]
      Pyodide[Pyodide Runtime]
      SQLite[In-Memory SQLite]
      WebSerial[WebSerial API]

      Browser --> Pyodide
      Pyodide --> SQLite
      Browser --> WebSerial
    ```
  </div>

  <div class="tab-content production-content">
    ## Production Mode Architecture

    In production mode, a backend server handles...

    ```mermaid
    flowchart TB
      Browser[Browser]
      API[FastAPI Server]
      DB[(PostgreSQL)]
      Celery[Celery Workers]

      Browser --> API
      API --> DB
      API --> Celery
    ```
  </div>
</div>
```

**Add CSS in docs-page.component.ts styles:**

```css
.mode-tabs {
  border: 1px solid var(--theme-border);
  border-radius: 12px;
  overflow: hidden;
  margin: 24px 0;
}

.mode-tabs input[type="radio"] {
  display: none;
}

.mode-tabs label {
  display: inline-block;
  padding: 12px 24px;
  cursor: pointer;
  background: var(--mat-sys-surface-variant);
  border-bottom: 2px solid transparent;
}

.mode-tabs input:checked + label {
  background: var(--mat-sys-surface);
  border-bottom-color: var(--primary-color);
}

.tab-content {
  display: none;
  padding: 24px;
}

#browser-tab:checked ~ .browser-content,
#production-tab:checked ~ .production-content {
  display: block;
}
```

---

## 5. Verification Plan

**Definition of Done:**

1. Architecture overview has mode-specific sections
2. Users can toggle/switch between Browser and Production views
3. Each mode shows relevant architecture diagram
4. Limitations and capabilities are clearly documented per mode
5. Works with both light and dark themes

**Verification Commands:**

```bash
cd praxis/web-client
npm run build
```

**Manual Verification:**
1. Navigate to Docs > Architecture > Overview
2. Verify mode tabs/sections are visible
3. Switch between modes
4. Verify correct diagrams and content shown
5. Test in both light and dark themes

---

## On Completion

- [ ] Commit changes with message: `docs: add mode separation to architecture documentation`
- [ ] Update backlog item status in `backlog/docs.md`
- [ ] Update `DEVELOPMENT_MATRIX.md` if applicable
- [ ] Mark this prompt complete in batch README and set status to 🟢 Completed

---

## References

- `.agents/README.md` - Development context and agent workflow
- `backlog/docs.md` - Full documentation issue tracking
