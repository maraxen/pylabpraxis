# Agent Prompt: Fix API Documentation Pages

Examine `.agents/README.md` for development context.

**Status:** 🟢 Not Started
**Priority:** P2
**Difficulty:** Medium
**Batch:** [260109](./README.md)
**Backlog Reference:** [docs.md](../../backlog/docs.md#p2-api-docs-not-working)

---

## 1. The Task

The API documentation pages are not working/rendering properly. This includes REST API, WebSocket API, and Services documentation.

**Goal:** Investigate and fix the API documentation rendering issues so users can access API reference documentation.

**User Value:** Developers integrating with Praxis need working API documentation.

---

## 2. Technical Implementation Strategy

**Investigation Steps:**

1. Navigate to `/docs/api/rest-api` and observe what happens
2. Check browser console for errors
3. Verify markdown files exist at `praxis/web-client/src/assets/docs/api/`
4. Check `DocsPageComponent` for path resolution issues

**Potential Issues:**

1. **Path mismatch**: Docs routes may not match asset file structure
2. **Markdown loading failure**: HTTP requests for `.md` files may be failing
3. **Missing files**: API docs may not have been created yet
4. **Route configuration**: `docs.routes.ts` may be misconfigured

**Frontend Components:**

1. Verify routes in `docs.routes.ts`
2. Check `DocsPageComponent.loadMarkdown()` path resolution
3. Ensure API markdown files exist and have content

---

## 3. Context & References

**Primary Files to Modify:**

| Path | Description |
|:-----|:------------|
| `praxis/web-client/src/app/features/docs/docs.routes.ts` | Route configuration |
| `praxis/web-client/src/app/features/docs/components/docs-page.component.ts` | Markdown loading logic |
| `praxis/web-client/src/assets/docs/api/*.md` | API documentation content |

**Reference Files (Read-Only):**

| Path | Description |
|:-----|:------------|
| `praxis/web-client/src/app/features/docs/docs-layout.component.ts` | Docs navigation structure |
| `praxis/backend/app/api/v1/` | Actual API endpoints to document |

---

## 4. Constraints & Conventions

- **Commands**: Use `npm` for Angular tasks
- **Frontend Path**: `praxis/web-client`
- **Documentation Format**: Markdown with optional Mermaid diagrams
- **Path Convention**: `assets/docs/{section}/{page}.md`

**Investigation Commands:**

```bash
# Check if API docs files exist
ls -la praxis/web-client/src/assets/docs/api/

# Check route configuration
grep -A 20 "api" praxis/web-client/src/app/features/docs/docs.routes.ts
```

**If files are missing, create them with basic structure:**

```markdown
# REST API Reference

## Overview

The Praxis REST API provides endpoints for managing assets, protocols, and execution.

## Base URL

- Production: `http://localhost:8000/api/v1`
- Browser Mode: Uses in-memory SQLite via Pyodide

## Endpoints

### Assets

#### GET /assets/machines
Returns list of registered machines.

#### GET /assets/resources
Returns list of registered resources.

...
```

**If path resolution is the issue:**

```typescript
// In DocsPageComponent.loadMarkdown()
private loadMarkdown(section: string, page: string): void {
  // Ensure path is correctly constructed
  const path = `assets/docs/${section}/${page}.md`;
  console.log('[DocsPage] Loading:', path);
  // ... rest of loading logic
}
```

---

## 5. Verification Plan

**Definition of Done:**

1. API documentation pages load without errors
2. REST API reference is accessible at `/docs/api/rest-api`
3. WebSocket API reference is accessible at `/docs/api/websocket-api`
4. Services reference is accessible at `/docs/api/services`
5. Content is accurate and useful

**Verification Commands:**

```bash
cd praxis/web-client
npm run build

# Verify assets are included in build
ls -la dist/*/assets/docs/api/
```

**Manual Verification:**
1. Navigate to Docs section
2. Click on API > REST API
3. Verify page loads with content
4. Check WebSocket API and Services pages

---

## On Completion

- [ ] Commit changes with message: `fix(docs): restore API documentation pages`
- [ ] Update backlog item status in `backlog/docs.md`
- [ ] Update `DEVELOPMENT_MATRIX.md` if applicable
- [ ] Mark this prompt complete in batch README and set status to 🟢 Completed

---

## References

- `.agents/README.md` - Development context and agent workflow
- `backlog/docs.md` - Full documentation issue tracking
