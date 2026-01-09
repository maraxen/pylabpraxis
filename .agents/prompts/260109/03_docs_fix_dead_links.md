# Agent Prompt: Fix Dead Links in Documentation

Examine `.agents/README.md` for development context.

**Status:** 🟢 Completed
**Priority:** P2
**Batch:** [260109](./README.md)
**Backlog Reference:** [docs.md](../../backlog/docs.md)

---

## 1. The Task

Dead links exist in the documentation. This task involves running a link checker across all documentation files, identifying broken links, and fixing or removing them.

**User Value:** Users can navigate documentation without encountering 404 errors, improving trust and usability.

---

## 2. Technical Implementation Strategy

### Architecture

**Documentation locations:**

1. `docs/` - MkDocs source files
2. `praxis/web-client/src/assets/docs/` - In-app documentation copy

### Implementation Steps

1. **Run link checker on docs/**:

   ```bash
   # Using linkchecker or a similar tool
   uv run linkchecker docs/ --check-extern
   ```

   OR use MkDocs strict mode which catches broken internal links:

   ```bash
   uv run mkdocs build --strict 2>&1 | grep -i "warning\|error"
   ```

2. **Manual grep for common link patterns:**

   ```bash
   # Find all markdown links
   grep -rn '\[.*\](.*\.md)' docs/
   grep -rn '\[.*\](\.\./' docs/
   ```

3. **Common dead link patterns to check:**
   - Links to moved/renamed files
   - Links with incorrect relative paths (`../` depth issues)
   - Links to non-existent anchors (`#section-name`)
   - External links to deprecated URLs

4. **Fix categories:**
   - **Update path:** If file was moved, update the link
   - **Remove link:** If target no longer exists and isn't needed
   - **Create stub:** If linked content should exist but doesn't

### Data Flow

1. Scan all `.md` files in `docs/` and `praxis/web-client/src/assets/docs/`
2. Extract all links (internal and external)
3. Validate each link target exists
4. Generate report of broken links
5. Fix each broken link appropriately
6. Sync fixes between both doc locations

---

## 3. Context & References

**Primary Files to Modify:**

| Path | Description |
|:-----|:------------|
| `docs/**/*.md` | All MkDocs documentation files |
| `praxis/web-client/src/assets/docs/**/*.md` | All in-app documentation files |

**Reference Files (Read-Only):**

| Path | Description |
|:-----|:------------|
| `mkdocs.yml` | Nav structure defines expected file organization |
| `praxis/web-client/src/app/features/docs/docs.routes.ts` | Angular doc routes |

---

## 4. Constraints & Conventions

- **Commands**: Use `uv run mkdocs build --strict` to validate
- **Both paths must stay in sync**: `docs/` and `praxis/web-client/src/assets/docs/`
- **Preserve anchor links**: When fixing, ensure `#anchor` references still work
- **External links**: Only fix if clearly broken; don't remove useful external references

---

## 5. Verification Plan

**Definition of Done:**

1. MkDocs builds without link warnings:

   ```bash
   uv run mkdocs build --strict
   ```

   Should complete with no "WARNING" messages about broken links.

2. Manual spot-check of fixed links:

   ```bash
   uv run mkdocs serve
   ```

   - Click through navigation in sidebar
   - Verify cross-references in key pages work

3. In-app verification:

   ```bash
   cd praxis/web-client && npm run start
   ```

   - Navigate to Docs section
   - Click links within documentation pages
   - Verify no 404 or missing content errors

---

## On Completion

- [ ] Document which links were fixed in commit message
- [ ] Commit changes with message: `docs: fix dead links across documentation`
- [ ] Update backlog item status in [docs.md](../../backlog/docs.md)
- [ ] Mark this prompt complete in batch README, update DEVELOPMENT_MATRIX.md if applicable, and set the status in this prompt document to 🟢 Completed

---

## References

- `.agents/README.md` - Environment overview
- `mkdocs.yml` - Site navigation structure
