
# Review Plan: Jules Batch 2026-01-23 (Revised)

**Status**: Partial completion.
**Correction**: Many tasks were already merged (marked ✅ Done in tracking).
Refocusing on truly pending items.

## Pending Tasks (Actionable)

### 1. SPLIT-01: Decompose run-protocol (High Risk)

*Status*: Awaiting Plan Approval (⏳)
*Attributes*: Large refactor (1477 lines).
*Action*: **Worktree `split-run-proto`** (In Progress)

- Create worktree
- Apply patch
- Run tests: `npm test src/app/features/run-protocol`

### 2. REFACTOR-01: Core Aliases (Low Risk)

*Status*: Awaiting Plan Approval (⏳)
*Action*: **Worktree `refactor-core`**

- Use worktree to avoid conflicts.
- Apply patch.

### 3. E2E-NEW-03: Workcell Dashboard Tests (Medium Risk)

*Status*: ⏳ (Partial?)
*Action*: **Check status / Cherry pick**

- Pull diff and inspect.

## Completed / Merged (Verified)

- SPLIT-04, SPLIT-05, SPLIT-06 (Already in main)
- REFACTOR-02, REFACTOR-03 (Already in main - reapplying caused conflicts)
- OPFS-03 (Re-applied successfully)
- JLITE-03 (Failed re-apply, assumed done)

## Next Steps

1. Verify `SPLIT-01` in worktree.
2. Setup `REFACTOR-01` in worktree.
3. Report results for manual review.
