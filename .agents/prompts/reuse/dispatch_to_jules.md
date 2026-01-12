# Reusable Prompt: Dispatch to Jules

Examine `.agents/README.md` and `.agents/skills/jules-remote/SKILL.md` for context.

**Purpose:** Dispatch incomplete prompt files from `prompts/YYMMDD/` to the Jules agent, monitor progress, review the result, and apply the changes.
**Use when:** You have a specific, atomic prompt file ready for execution by Jules.

---

## Prompt

You are tasked with executing the prompt file located at `{PROMPT_FILE}` using the Jules agent.

### 1. Contextualize

Read the content of `{PROMPT_FILE}`. Identify the "Task" or "Goal" and the "Technical Implementation Strategy" sections. Construct a clear, self-contained description for Jules that includes:

- The core objective.
- Specific file paths to modify or create.
- Any strict constraints (e.g., "Do not delete existing tests").
- The content of the prompt file itself as context.

### 2. Dispatch

Run the following command to start a Jules session:
`jules new --session "{TITLE}" "<Constructed Description>"`

*Note the Session ID returned by this command.*

### 3. Monitor

Enter a monitoring loop:

- Check status every 5 minutes using `jules remote list --session`.
- Wait until the session status is `COMPLETED` (or similar success state).
- If the session fails or requires input, report it and stop.

### 4. Review

Once completed, pull the changes *without applying* to review them:
`jules remote pull --session <SESSION_ID>`

*Review Guidelines:*

- **Context:** Re-read `{PROMPT_FILE}` to ensure the solution matches the requirements.
- **Read the patch/diff:** Check the downloaded artifacts (inspect the patch file or diff).
- **Scope Check:** Ensure the changes are strictly related to the requested task.
- **Safety Check:** Verify no unnecessary deletions of existing code, tests, or configuration.
- **Quality Check:** Ensure the code looks syntactically correct and follows project patterns.

### 5. Apply

If the review passes:

- Apply the changes: `jules remote pull --session <SESSION_ID> --apply`
- Verify the application by running relevant tests (e.g., `npm test`, `uv run pytest`).

If the review fails:

- Do not apply.
- Report the specific issues found in the review.

---

## Customization

| Placeholder | Description | Example |
|:------------|:------------|:--------|
| `{PROMPT_FILE}` | Path to the prompt file | `.agents/prompts/260109/14_assets_filter.md` |
| `{TITLE}` | Short title for the Jules session | `Fix Asset Filters` |

---

## Example Usage

```
Use the "Dispatch to Jules" prompt to execute the asset filter fix:
PROMPT_FILE=".agents/prompts/260109/14_assets_filter.md"
TITLE="Fix Asset Filters"
```
