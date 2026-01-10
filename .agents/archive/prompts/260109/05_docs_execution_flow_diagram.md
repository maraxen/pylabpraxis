# Agent Prompt: Fix Execution Flow Diagram Formatting

Examine `.agents/README.md` for development context.

**Status:** 🟢 Completed
**Priority:** P2
**Batch:** [260109](./README.md)
**Backlog Reference:** [docs.md](../../backlog/docs.md)

---

## 1. The Task

The execution flow diagram in `docs/architecture/execution-flow.md` has formatting issues. This may include:

- Mermaid sequence diagram rendering problems
- Theme/color issues similar to state management diagram
- Layout problems in narrow viewports
- Text overflow or truncation issues

**User Value:** Developers can clearly understand the protocol execution flow, improving onboarding and debugging capabilities.

---

## 2. Technical Implementation Strategy

### Architecture

**Source:** `docs/architecture/execution-flow.md`

- Contains TWO sequence diagrams:
  1. Production Mode (Distributed) - lines 11-45
  2. Browser Mode (Local-Only) - lines 50-75

### Current Diagrams Analysis

**Production Mode Diagram:**

```mermaid
sequenceDiagram
    actor User
    participant UI as Frontend
    participant API as FastAPI
    participant Orch as Orchestrator
    participant Sched as Scheduler
    participant Worker as Celery Worker
    participant WCR as WorkcellRuntime
    participant PLR as PyLabRobot
    ...
```

**Known Issues to Check:**

1. **Long participant names**: May cause horizontal overflow
2. **Alt/loop blocks**: Complex nesting may render incorrectly
3. **Actor styling**: May not theme properly
4. **Arrow labels**: May be cut off or overlap

### Implementation Approach

1. **Audit current rendering:**
   - Load the page in both themes
   - Check for visual issues
   - Note specific problems

2. **Common fixes:**
   - Shorten participant aliases for better fit
   - Adjust participant ordering for clearer flow
   - Add `autonumber` for sequence clarity
   - Ensure consistent theme variables (see prompt #4)

3. **Potential code changes:**

   ```mermaid
   sequenceDiagram
       autonumber
       actor User
       participant UI as Frontend
       participant API
       participant Orch as Orchestrator
       ...
   ```

### Data Flow

Same as prompt #4 (state management diagram) - DocsPageComponent renders via ngx-markdown with mermaid.

---

## 3. Context & References

**Primary Files to Modify:**

| Path | Description |
|:-----|:------------|
| `docs/architecture/execution-flow.md` | Source diagrams |
| `praxis/web-client/src/assets/docs/architecture/execution-flow.md` | In-app copy |
| `praxis/web-client/src/app/features/docs/components/docs-page.component.ts` | Mermaid config (if CSS fixes needed) |

**Reference Files (Read-Only):**

| Path | Description |
|:-----|:------------|
| `docs/architecture/state-management.md` | Similar diagram for consistency |
| `docs/architecture/overview.md` | Other diagrams for pattern reference |

---

## 4. Constraints & Conventions

- **Commands**: Use `npm run start` in `praxis/web-client` to test
- **Frontend Path**: `praxis/web-client`
- **Styling**: Ensure consistency with state management diagram theming
- **Both docs locations**: Keep `docs/` and `praxis/web-client/src/assets/docs/` in sync
- **Responsive**: Diagrams should be readable on various screen widths

---

## 5. Verification Plan

**Definition of Done:**

1. The code compiles without errors:

   ```bash
   cd praxis/web-client && npm run build
   ```

2. Visual verification:
   - Navigate to Docs → Architecture → Execution Flow
   - Both diagrams render without errors
   - Participant names are readable
   - Arrow labels are visible
   - Alt/loop blocks display correctly
   - No horizontal overflow

3. Theme verification:
   - Check in LIGHT mode
   - Toggle to DARK mode
   - Both themes should render diagrams legibly

4. MkDocs verification:

   ```bash
   uv run mkdocs serve
   ```

   - Open <http://localhost:8000/architecture/execution-flow/>
   - Verify diagrams render in built site

---

## On Completion

- [x] Commit changes with message: `docs: fix execution flow diagram formatting`
- [x] Update backlog item status in [docs.md](../../backlog/docs.md)
- [x] Mark this prompt complete in batch README, update DEVELOPMENT_MATRIX.md if applicable, and set the status in this prompt document to 🟢 Completed

---

## References

- `.agents/README.md` - Environment overview
- [Mermaid Sequence Diagrams](https://mermaid.js.org/syntax/sequenceDiagram.html) - Syntax reference
