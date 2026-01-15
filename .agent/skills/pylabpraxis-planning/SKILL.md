---
name: pylabpraxis-planning
description: Project-specific planning workflows for Pylabpraxis. Handles backlog archiving, prompt generation, and development matrix updates.
---

# Pylabpraxis Planning

This skill encapsulates the planning and project management workflows specific to `pylabpraxis`.

## Tools & Context

- **Master Matrix**: `.agent/DEVELOPMENT_MATRIX.md`
- **Backlog**: `.agent/backlog/*.md`
- **Prompts**: `.agent/prompts/`

## Workflows

### 1. Backlog Archiving

**Trigger**: "Archive backlog", "Cleanup sprint", "Consolidate tasks"

1. **Review**: Check `DEVELOPMENT_MATRIX.md` for ✅ Completed items.
2. **Verify**: Ensure corresponding `backlog/*.md` file has all checkboxes checked.
3. **Archive**:
   - Move file to `.agent/archive/`.
   - Update `DEVELOPMENT_MATRIX.md` (move row to "Completed").
   - Update `ROADMAP.md` if milestone complete.
4. **Consolidate**: If multiple items form a feature, create a summary doc in archive.

### 2. Prompt Generation

**Trigger**: "Generate prompts", "Prepare next batch", "Scaffold tasks"

1. **Select**: Pick N high-priority items from `DEVELOPMENT_MATRIX.md`.
2. **Reconnaissance**: **CRITICAL**. Audit the codebase for *each* item.
   - Find actual paths (e.g. `praxis/web-client/...`).
   - Identify patterns to copy.
3. **Generate**: Create `.agent/prompts/{YYMMDD}_dev_cycle/{Priority}_{Slug}.md`.
   - Use template `.agent/templates/agent_prompt.md`.
   - **Must** include: exact file paths, verification commands, and architectural nuance.

### 3. Matrix Update

**Trigger**: "Update matrix", "Status check"

1. Scan all active columns in `DEVELOPMENT_MATRIX.md`.
2. Verify actual state of code vs. claimed status.
3. Update status emojis (🔴, 🟡, 🟢, ✅).
