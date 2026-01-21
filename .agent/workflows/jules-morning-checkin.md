---
description: Systematic process for reviewing, merging, and recording completed Jules sessions
---

# Jules Morning Check-in Workflow

Use this workflow at the start of the day to process the overnight work from Jules agents.

## Phase 1: Assessment

### 1.1 Check Local State

Ensure your local branch is clean and up to date.

```bash
git status
git pull origin $(git branch --show-current)
```

### 1.2 List Completed Sessions

Identify sessions that finished overnight.

```bash
# List all completed sessions
jules remote list --session 2>&1 | cat | grep "Completed"

# Get a quick count
echo "Completed sessions: $(jules remote list --session 2>&1 | cat | grep -c "Completed")"
```

### 1.3 Identify Verification Failures

Check for sessions that require user feedback or failed.

```bash
jules remote list --session 2>&1 | cat | grep -E "Failed|Awaiting User"
```

## Phase 2: Review and Merge Loop

Perform this cycle for each completed session you intend to merge.

### 2.1 Preview Changes (Safe Mode)

**Always** preview the diff before applying. Jules may have worked on the wrong branch or halluncinated files.

```bash
# Replace <SESSION_ID> with the actual ID
jules remote pull --session <SESSION_ID> 2>&1 | head -n 100
```

*Tip: If the output shows `diff --git ...`, check that file paths match your project structure.*

### 2.2 Apply Changes

If the diff looks good:

```bash
jules remote pull --session <SESSION_ID> --apply 2>&1
```

### 2.3 Verify functionality

Quickly run relevant checks (e.g., lint, test) if the change was code-heavy.

```bash
# Example
npm run lint
uv run pytest
```

### 2.4 Update MCP Database

Mark the task as completed in the agent database to keep tracking in sync.

```bash
sqlite3 .agent/agent.db "UPDATE dispatches SET status = 'completed', result = 'Merged via morning check-in' WHERE claimed_by LIKE '%<SESSION_ID>%'"
```

## Phase 3: Handling Issues

### 3.1 Wrong Branch / Merge Conflict

If `jules remote pull --apply` fails:

1. Pull the patch to a file: `jules remote pull --session <ID> > patch.diff`
2. Try applying manually: `git apply --reject patch.diff`
3. Resolve conflicts in your editor.

### 3.2 Poor Quality / hallucination

If the work is unusable:

1. Mark as failed in MCP:

    ```bash
    sqlite3 .agent/agent.db "UPDATE dispatches SET status = 'failed', result = 'Quality check failed' WHERE claimed_by LIKE '%<SESSION_ID>%'"
    ```

2. Create a **new** dispatch with clarified instructions (don't reuse the old one).

## Phase 4: Finalization

### 4.1 Commit Merged Work

Group related changes into atomic commits.

```bash
git add .
git commit -m "feat(agent): merge completed Jules sessions for [topic]"
```

### 4.2 Push

```bash
git push origin $(git branch --show-current)
```

### 4.3 Dispatch Follow-ups

If the morning's work unblocked new tasks, dispatch them immediately.

```bash
# Example: If research is done, dispatch implementation
mcp_orbitalvelocity_dispatch({ target: "jules", prompt: "Implement features based on <research_doc>..." })
```
