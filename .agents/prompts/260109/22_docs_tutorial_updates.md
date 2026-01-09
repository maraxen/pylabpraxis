# Agent Prompt: Update Tutorial Documentation

Examine `.agents/README.md` for development context.

**Status:** 🟢 Not Started
**Priority:** P2
**Difficulty:** Medium
**Batch:** [260109](./README.md)
**Backlog Reference:** [docs.md](../../backlog/docs.md#p2-tutorial-updates)

---

## 1. The Task

The tutorial documentation needs to be brought up to date with current UI and functionality. Screenshots may be outdated, steps may reference old UI patterns, and some features may have changed.

**Goal:** Review and update the tutorial/quickstart documentation to reflect the current state of the application.

**User Value:** New users get accurate, up-to-date guidance for getting started with Praxis.

---

## 2. Technical Implementation Strategy

**Review Process:**

1. Follow the existing tutorial steps manually
2. Document discrepancies between docs and actual UI
3. Update text and screenshots as needed
4. Verify all described features work

**Key Areas to Review:**

1. **Getting Started / Quickstart** - Initial setup steps
2. **Browser Mode** - Browser-specific instructions
3. **Assets Guide** - Adding machines and resources
4. **Protocols Guide** - Creating and running protocols
5. **Playground Guide** - Interactive notebook usage

**Documentation Structure:**

```
assets/docs/
├── getting-started/
│   ├── quickstart.md      ← Primary tutorial
│   ├── installation.md
│   ├── browser-mode.md
│   └── browser-script.md
├── user-guide/
│   ├── assets.md
│   ├── protocols.md
│   ├── hardware-discovery.md
│   └── data-visualization.md
```

---

## 3. Context & References

**Primary Files to Modify:**

| Path | Description |
|:-----|:------------|
| `praxis/web-client/src/assets/docs/getting-started/quickstart.md` | Main quickstart tutorial |
| `praxis/web-client/src/assets/docs/getting-started/browser-mode.md` | Browser mode guide |
| `praxis/web-client/src/assets/docs/user-guide/assets.md` | Asset management guide |
| `praxis/web-client/src/assets/docs/user-guide/protocols.md` | Protocol guide |

**Reference Files (Read-Only):**

| Path | Description |
|:-----|:------------|
| Application UI | Compare against actual current UI |

---

## 4. Constraints & Conventions

- **Commands**: Use `npm` for Angular tasks
- **Frontend Path**: `praxis/web-client`
- **Documentation Format**: Markdown
- **Screenshots**: Store in `assets/docs/images/` if adding new images

**Review Checklist:**

For each documentation page, verify:

- [ ] All navigation paths match current UI
- [ ] Button labels match current UI
- [ ] Screenshots (if any) match current UI
- [ ] Code examples work correctly
- [ ] Links to other docs pages work
- [ ] Feature descriptions are accurate

**Common Issues to Fix:**

1. **Outdated Navigation**: "Click on X in the sidebar" when X moved
2. **Changed Button Labels**: "Click 'Create New'" when button says "Add"
3. **Missing Features**: Documented features that don't exist yet
4. **New Features**: Features that exist but aren't documented
5. **Changed Workflows**: Multi-step processes that changed

**Example Update:**

```markdown
<!-- Before (outdated) -->
1. Click "Add Machine" in the sidebar
2. Select a machine type from the dropdown

<!-- After (updated) -->
1. Navigate to **Assets** in the sidebar
2. Click the **+** button in the top right
3. Choose **Add Machine** from the dialog
4. Select a machine category, then a specific type
```

---

## 5. Verification Plan

**Definition of Done:**

1. All tutorial steps can be followed successfully
2. No references to outdated UI or features
3. Screenshots (if any) are current
4. Code examples execute without errors
5. All internal links work

**Verification Commands:**

```bash
cd praxis/web-client
npm run build

# Check for broken internal links
grep -r "\[.*\](\.\./" src/assets/docs/ | head -20
```

**Manual Verification:**
1. Open documentation in browser
2. Follow quickstart tutorial step by step
3. Verify each step matches actual UI
4. Note any discrepancies and fix
5. Test all links in documentation

---

## On Completion

- [ ] Commit changes with message: `docs: update tutorial and quickstart for current UI`
- [ ] Update backlog item status in `backlog/docs.md`
- [ ] Update `DEVELOPMENT_MATRIX.md` if applicable
- [ ] Mark this prompt complete in batch README and set status to 🟢 Completed

---

## References

- `.agents/README.md` - Development context and agent workflow
- `backlog/docs.md` - Full documentation issue tracking
