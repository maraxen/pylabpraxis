# Agent Prompt: Fix Keyboard Shortcut Column Formatting in Docs

Examine `.agents/README.md` for development context.

**Status:** 🟢 Not Started
**Priority:** P2
**Batch:** [260109](./README.md)
**Backlog Reference:** [docs.md](../../backlog/docs.md)

---

## 1. The Task

The keyboard shortcut column in documentation tables is not formatting properly. The docs use special markdown syntax like `++cmd+k++` for keyboard shortcuts (PyMdown Extensions kbd syntax), but these may not be rendering correctly in the Angular markdown viewer or MkDocs build.

**User Value:** Users can clearly see keyboard shortcuts in documentation, improving discoverability of productivity features.

---

## 2. Technical Implementation Strategy

### Architecture

**Two documentation systems exist:**

1. **MkDocs** (source at `docs/`) - Main documentation site built with `mkdocs build`
2. **In-app docs** (source at `praxis/web-client/src/assets/docs/`) - Rendered by `DocsPageComponent` using `ngx-markdown`

### Problem Analysis

The keyboard shortcuts table in `docs/getting-started/quickstart.md` (lines 104-112):

```markdown
| Shortcut | Action |
|----------|--------|
| ++cmd+k++ | Command palette |
| ++alt+h++ | Go to Home |
...
```

The `++key++` syntax is [PyMdown Extensions kbd](https://facelessuser.github.io/pymdown-extensions/extensions/keys/) syntax. This works in MkDocs if the extension is enabled, but `ngx-markdown` does NOT support this by default.

### Implementation Options

**Option A (Recommended):** Convert to standard HTML `<kbd>` tags which work everywhere:

```markdown
| Shortcut | Action |
|----------|--------|
| <kbd>Cmd</kbd>+<kbd>K</kbd> | Command palette |
```

**Option B:** Add CSS styling for `++key++` output if MkDocs is rendering but in-app isn't:

- Check if mkdocs.yml has `keys` extension enabled
- Add CSS in `docs-page.component.ts` to style `.keys` class

### Data Flow

1. Markdown files in `docs/` and `praxis/web-client/src/assets/docs/`
2. MkDocs builds static site from `docs/`
3. DocsPageComponent loads from `src/assets/docs/` via HTTP
4. ngx-markdown renders with mermaid support but not PyMdown keys

### Files to Update

Both doc locations need updating for consistency:

- `docs/getting-started/quickstart.md`
- `praxis/web-client/src/assets/docs/getting-started/quickstart.md`

---

## 3. Context & References

**Primary Files to Modify:**

| Path | Description |
|:-----|:------------|
| `docs/getting-started/quickstart.md` | MkDocs source - keyboard shortcuts table |
| `praxis/web-client/src/assets/docs/getting-started/quickstart.md` | In-app docs copy - keyboard shortcuts table |

**Reference Files (Read-Only):**

| Path | Description |
|:-----|:------------|
| `mkdocs.yml` | MkDocs configuration - check extensions |
| `praxis/web-client/src/app/features/docs/components/docs-page.component.ts` | Angular markdown renderer |

---

## 4. Constraints & Conventions

- **Commands**: Use `uv run mkdocs build` to test MkDocs output
- **Both paths must stay in sync**: `docs/` and `praxis/web-client/src/assets/docs/`
- **Use HTML `<kbd>` tags**: Most compatible across renderers
- **Styling**: Add CSS for `kbd` elements in docs-page.component.ts styles if needed

---

## 5. Verification Plan

**Definition of Done:**

1. The docs build without errors:

   ```bash
   uv run mkdocs build --strict
   ```

2. In-app verification:

   ```bash
   cd praxis/web-client && npm run start
   ```

   - Navigate to Docs → Getting Started → Quick Start
   - Scroll to Keyboard Shortcuts section
   - Verify shortcuts display as styled keyboard keys, not raw `++key++` text

3. MkDocs site verification:

   ```bash
   uv run mkdocs serve
   ```

   - Open <http://localhost:8000>
   - Navigate to Getting Started → Quick Start
   - Verify keyboard shortcuts render properly

---

## On Completion

- [ ] Commit changes with message: `docs: fix keyboard shortcut formatting in quickstart`
- [ ] Update backlog item status in [docs.md](../../backlog/docs.md)
- [ ] Mark this prompt complete in batch README, DEVELOPMENT_MATRIX.md if applicable, and set the status in this prompt document to 🟢 Completed

---

## References

- `.agents/README.md` - Environment overview
- [PyMdown Extensions Keys](https://facelessuser.github.io/pymdown-extensions/extensions/keys/) - Reference for kbd syntax
