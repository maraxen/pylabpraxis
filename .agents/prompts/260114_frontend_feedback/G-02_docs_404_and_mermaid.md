# Agent Prompt: G-02 Documentation 404 & Mermaid Fixes

Examine `.agents/README.md` for development context.

**Status:** 🟢 Not Started
**Priority:** P1/P2
**Batch:** [260114_frontend_feedback](./README.md)
**Difficulty:** Medium
**Type:** 🟢 Implementation
**Dependencies:** None
**Backlog Reference:** [GROUP_G_documentation_init.md](./GROUP_G_documentation_init.md)

---

## 1. The Task

Fix two documentation issues:

### Issue 1: 404 on installation-production.md (P1)

**User Feedback:**
> "Error Code: 404 Message: Http failure response for <http://localhost:4200/assets/docs/getting-started/installation-production.md>: 404 Not Found"

**Root Cause (from reconnaissance):**  
The `DocsPageComponent` has mode-switching logic that tries to load `{page}-{mode}.md` files:

```typescript
// docs-page.component.ts lines 512-515
const modePath = `assets/docs/${section}/${page}-${mode}.md`;
const defaultPath = `assets/docs/${section}/${page}.md`;
```

When viewMode is 'production', it tries to load `installation-production.md` which doesn't exist. The fallback to `installation.md` should work, but this 404 appears in user's error log.

### Issue 2: Mermaid/System Diagrams Not Rendering (P2)

**User Feedback:**
> "system diagrams and mermaid not rendering"
> "Trying to expand the system architecture views does not work and instead yields just the text, not the actual visual view."

**Analysis:**  
The `DocsPageComponent` uses `ngx-markdown` with mermaid support configured. The expand button is injected via `onMarkdownReady()` (line 567-598). Issues may be:

1. Mermaid library not loading
2. Expand button event handler not working
3. CSS issues with diagram display

---

## 2. Technical Implementation Strategy

### Fix 1: Installation Docs 404

**Option A (Recommended):** Create the missing mode-specific files

- Create `installation-production.md` for production-specific install instructions
- Create `installation-browser.md` for browser-specific install instructions
- Update `installation.md` as the common fallback

**Option B (Alternative):** Remove mode-switching for installation page

- Modify `DocsPageComponent` to not show mode switcher for installation page
- The mode switcher currently only shows for architecture pages (line 487):

  ```typescript
  this.showModeSwitch.set(section === 'architecture' && (page === 'overview' || page === 'backend'));
  ```

- If the error is spurious (mode switcher not shown but mode still affects URL), fix the logic

### Fix 2: Mermaid Rendering

**Debug Steps:**

1. Check if mermaid library is loading in browser console
2. Verify `MarkdownModule` properly configured with mermaid
3. Test expand button functionality
4. Check `DiagramOverlayComponent` for rendering issues

**Files to Check/Modify:**

| Path | Purpose |
|:-----|:--------|
| `praxis/web-client/src/app/features/docs/components/docs-page.component.ts` | Main docs renderer |
| `praxis/web-client/src/app/shared/components/diagram-overlay/diagram-overlay.component.ts` | Fullscreen diagram view |
| `praxis/web-client/angular.json` | Check mermaid script loading |

---

## 3. Context & References

**Primary Files to Modify:**

| Path | Description |
|:-----|:------------|
| `praxis/web-client/src/assets/docs/getting-started/installation.md` | Existing installation docs |
| `praxis/web-client/src/assets/docs/getting-started/installation-production.md` | [NEW] Production mode install guide |
| `praxis/web-client/src/app/features/docs/components/docs-page.component.ts` | Docs page with mermaid rendering |

**Reference Files (Read-Only):**

| Path | Description |
|:-----|:------------|
| `praxis/web-client/src/app/features/docs/docs-layout.component.ts` | Docs sidebar navigation |
| `praxis/web-client/src/app/features/docs/docs.routes.ts` | Docs routing configuration |
| `praxis/web-client/src/app/shared/components/diagram-overlay/diagram-overlay.component.ts` | Diagram fullscreen overlay |

**Current Getting Started Files:**

```
praxis/web-client/src/assets/docs/getting-started/
├── browser-mode.md
├── browser-script.md
├── installation.md
└── quickstart.md
```

---

## 4. Constraints & Conventions

- **Commands**: Use `npm` for Angular.
- **Frontend Path**: `praxis/web-client`
- **Styling**: Follow existing docs page styling patterns
- **Mermaid**: Uses `ngx-markdown` mermaid integration

---

## 5. Verification Plan

**Definition of Done:**

1. No 404 errors for documentation pages
2. Mermaid diagrams render correctly
3. Expand button opens diagrams in fullscreen overlay
4. All existing docs pages still load correctly

**Test Commands:**

```bash
cd praxis/web-client
npm run start:browser
```

**Manual Verification:**

1. Navigate to `/docs/getting-started/installation`
2. Check browser console for 404 errors - should be none
3. Navigate to `/docs/architecture/overview`
4. Toggle between Production/Browser mode - both should load content
5. Scroll to any mermaid diagram - should render visually (not as text)
6. Click expand button on diagram - should open fullscreen overlay
7. Press Escape or close button - overlay should close

---

## On Completion

- [ ] Commit changes with descriptive message
- [ ] Update backlog item status in `.agents/backlog/docs.md`
- [ ] Mark this prompt complete in batch README

---

## References

- `.agents/README.md` - Environment overview
- `.agents/backlog/docs.md` - Documentation backlog items
