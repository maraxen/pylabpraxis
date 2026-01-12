# Reusable Prompt: Dispatch to Jules

Examine `.agents/README.md` and `.agents/skills/jules-remote/SKILL.md` for context.

**Purpose:** Dispatch incomplete prompt files from `prompts/YYMMDD/` to the Jules agent, monitor progress, review the result, and apply the changes.
**Use when:** You have a specific, atomic prompt file ready for execution by Jules.

---

## Prompt

You are tasked with executing the prompt file(s) specified in `{PROMPT_TARGET}` (which can be a file path, a list of files, or a directory glob) using the Jules agent.

### 1. Analysis & Preparation

**For each prompt file identified in `{PROMPT_TARGET}`:**

1. **Read Content:** Read the full content of the prompt file verbatim.
2. **Prepare Description:**
    - Take the full file content.
    - Append a footer to link back to the source file:

      ```text
      
      ---
      > **Meta:** This task is defined in `{ABSOLUTE_PATH_TO_PROMPT_FILE}`.
      > **Instruction:** When the task is successfully completed, please edit `{ABSOLUTE_PATH_TO_PROMPT_FILE}` to change the `**Status:**` to `Complete`.
      ```

### 2. Dispatch

Iterate through the prepared tasks and dispatch them.

**Strategy:**

- **Parallel:** If tasks touch *different, non-overlapping* files, dispatch them immediately.
- **Sequential:** If tasks touch the *same* files or dependencies, dispatch one, wait for completion/application, then dispatch the next.

**Command:**

```bash
# Recommendation: Use pipe to avoid shell escaping issues with complex prompts
cat "{PREPARED_DESCRIPTION_FILE}" | jules remote new --session -
# OR if passing directly (less safe for complex content):
# jules remote new --session "Title: {TITLE} ({FILENAME})... {REST_OF_CONTENT}"
```

*Maintain a map of `[Prompt File] -> [Session ID]`.*

### 3. Monitor

Enter a monitoring loop for all active Session IDs:

- **Check status:** `jules remote list --session 2>&1 | grep <SESSION_ID>`
- **Action:**
  - If `COMPLETED`: Move to Review/Apply for that session immediately.
  - If `IN_PROGRESS` (> 5 mins): Check for dry-run artifacts (`jules remote pull`).
  - If `FAILED`: Report and stop that specific track.

### 4. Review & Apply (Per Session)

As each session completes, process it:

1. **Pull (Review):** `jules remote pull --session <SESSION_ID>`
2. **Review Guidelines:**
    - **Sanity:** Does it match the prompt?
    - **Conflicts:** If conflicts exist, **do not force apply**. Extract intent and apply manually.
3. **Apply:**
    - Clean: `jules remote pull --session <SESSION_ID> --apply`
    - Manual: Apply logic by hand.
4. **Verify:** Run the specific acceptance tests for this usage.

- **Stop:** If the issue is severe (e.g., deleting core functionality), stop the process and report the issue to the user and ask for clarification.

---

## Customization

| Placeholder | Description | Example |
|:------------|:------------|:--------|
| `{PROMPT_TARGET}` | File, Glob, or Directory of prompts | `.agents/prompts/260109/*.md` |
| `{TITLE}` | Derived from the prompt content | `Fix Asset Filters` |

---

## Example Usage

```
PROMPT_TARGET=".agents/prompts/260110/*.md"
# The agent will iterate through all matching files, dispatching them to Jules.
```
