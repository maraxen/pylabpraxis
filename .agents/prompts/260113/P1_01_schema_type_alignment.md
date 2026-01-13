# Agent Prompt: Schema Type Alignment

Examine `.agents/README.md` for development context.

**Status:** 🟢 Complete
**Priority:** P1
**Batch:** [260113](./README.md)
**Backlog Reference:** [frontend_schema_sync.md](../../backlog/frontend_schema_sync.md)

---

## 1. The Task

After the backend migration to SQLModel, the frontend `schema.ts` was regenerated with table-based naming (e.g., `MachineDefinition` instead of `MachineDefinitionCatalog`). The `repositories.ts` file still imports legacy type names that no longer exist, causing TypeScript compilation errors.

**User Value:** Restore frontend compilation by aligning type imports with the regenerated schema.

---

## 2. Technical Implementation Strategy

**Root Cause Analysis:**

The `repositories.ts` file imports these types that don't exist in the new `schema.ts`:

- `Asset` - Base class for Machine/Resource/Deck (Joined Table Inheritance)
- `MachineDefinitionCatalog` → should be `MachineDefinition`
- `ResourceDefinitionCatalog` → should be `ResourceDefinition`

**Implementation Options:**

1. **Option A (Recommended): Add type aliases to `schema.ts`**
   - Add `export type MachineDefinitionCatalog = MachineDefinition;`
   - Add `export type ResourceDefinitionCatalog = ResourceDefinition;`
   - Create a minimal `Asset` interface or union type for JTI compatibility

2. **Option B: Update all import consumers**
   - Directly update `repositories.ts` to use new names
   - Risk: May break other files importing the legacy names

**Recommended Approach:** Implement Option A for backward compatibility, then audit all consumers.

**Data Flow:**

1. `schema.ts` exports interfaces from browser SQLite schema
2. `repositories.ts` imports these interfaces for type-safe queries
3. Services/components import from `repositories.ts` for data access

---

## 3. Context & References

**Primary Files to Modify:**

| Path | Description |
|:-----|:------------|
| `scripts/generate_browser_schema.py` | Modify generator to append type aliases |

**Reference Files (Read-Only):**

| Path | Description |
|:-----|:------------|
| `praxis/web-client/src/app/core/db/schema.ts` | Generated output - verify aliases appear |
| `praxis/web-client/src/app/core/db/repositories.ts` | Consumer - shows expected type names |

---

## 4. Constraints & Conventions

- **Commands**: Use `uv run` for Python scripts, `npm` for Angular.
- **Frontend Path**: `praxis/web-client`
- **Backend Path**: `scripts/` for generation scripts
- Modify the generator script, then regenerate `schema.ts`.
- Do not manually edit the generated `schema.ts` file.

---

## 5. Implementation Details

Modify `scripts/generate_browser_schema.py` to append the backward compatibility aliases to the generated TypeScript file.

target file: `scripts/generate_browser_schema.py`

In the `generate_typescript_interfaces` function (around line 251), find the end of the content generation (before `return "\n".join(lines)`) and add the aliases.

**Python Code to Add:**

```python
    # ... existing generation loop ...

    # Add legacy aliases for backward compatibility
    lines.append("// =============================================================================")
    lines.append("// TYPE ALIASES FOR BACKWARD COMPATIBILITY")
    lines.append("// =============================================================================")
    lines.append("")
    lines.append("/** Legacy alias for MachineDefinition (was 'machine_definition_catalog' table) */")
    lines.append("export type MachineDefinitionCatalog = MachineDefinition;")
    lines.append("")
    lines.append("/** Legacy alias for ResourceDefinition (was 'resource_definition_catalog' table) */")
    lines.append("export type ResourceDefinitionCatalog = ResourceDefinition;")
    lines.append("")
    lines.append("/**")
    lines.append(" * Asset is the base type for Machine, Resource, and Deck entities.")
    lines.append(" * In the backend, these use Joined Table Inheritance (JTI).")
    lines.append(" */")
    lines.append("export type Asset = Machine | Resource | Deck;")
    lines.append("")

    return "\n".join(lines)
```

**Verification:**

After modifying the script, **run the generator** to verify it works and creates the expected `schema.ts`:

```bash
uv run scripts/generate_browser_schema.py
```

Then verify `schema.ts` contains the aliases.

---

## 6. Verification Plan

**Definition of Done:**

1. The code compiles without errors related to missing `Asset`, `MachineDefinitionCatalog`, or `ResourceDefinitionCatalog`.
2. The following commands pass:

   ```bash
   cd praxis/web-client && npm run build 2>&1 | grep -E "(error TS|Cannot find)"
   ```

   Expected: No errors mentioning `Asset`, `MachineDefinitionCatalog`, or `ResourceDefinitionCatalog`.

3. Run type checking:

   ```bash
   cd praxis/web-client && npx tsc --noEmit 2>&1 | head -50
   ```

---

## On Completion

- [ ] Commit changes with descriptive message referencing the backlog item
- [ ] Update backlog item status (Phase 1 tasks)
- [ ] Mark this prompt complete in batch README

---

## References

- `.agents/README.md` - Environment overview
- [schema.ts](file:///Users/mar/Projects/pylabpraxis/praxis/web-client/src/app/core/db/schema.ts)
- [repositories.ts](file:///Users/mar/Projects/pylabpraxis/praxis/web-client/src/app/core/db/repositories.ts)
