---
description: Analyze a target conversation, build a timeline, and propose next paths
---
# Conversation Summary Workflow

Adopt a structured approach to analyze a historic or current conversation, parse its chronological timeline, assess its current state, and present clear options for next paths.

## When to Use

- When resuming a long-running conversation or task.
- To hand off context between sessions or agents.
- When the user asks for a recap, timeline, or breakdown of what occurred in a specific thread, Jules session, or pipeline run.
- To untangle a complex debugging session and figure out "where are we, and what's next?".

## Inputs

The user must specify a **target conversation**. This could be:

| Input Type | Example | Retrieval Method |
|------------|---------|------------------|
| **Current conversation** | "Summarize our conversation so far" | Use in-context chat history directly |
| **Jules session** | "Summarize Jules session `d38e73be`" | Run `just jules-pull <session-id>` → read from `eph/jules-diffs/` |
| **Pipeline run** | "Summarize pipeline run 47" | Run `just pipeline-status <run_id>` → read completion artifacts |
| **File transcript** | "@[path/to/transcript.md]" | Use `view_file` to read the referenced file |
| **OV dispatch** | "Summarize dispatch #1234" | Query `dispatch(action: "get", payload: {id: 1234})` for completion summary |

If the target is unclear, ask: *"Which conversation would you like me to summarize? Please provide a session ID, pipeline run ID, file path, or indicate if you mean our current chat history."*

> [!NOTE]
> **Internal Session Data:** For future reference, our session state and thinking process are stored at `/home/marielle/.gemini/antigravity/brain/<CONVO_ID>/.system_generated/steps/`.
> Each step folder (e.g., `/127/`) contains:
> - `content.md`: The AI's thought process and reasoning.
> - `output.txt`: The result of any tool calls.
> The high-level artifacts (Plans, Walkthroughs, Tasks) are in the parent `.../brain/<CONVO_ID>/` directory.

## Phase 1: Load Context and Schema

1. **Locate the conversation.** Use the retrieval method from the Inputs table above.
2. **Load the summary schema.** The output must conform to the following schema:

```json
{
  "metadata": {
    "generated_at": "ISO 8601 timestamp",
    "schema_version": "1.0",
    "analyst": "orchestrator | agent role name"
  },
  "target_conversation": "string (identifier, session ID, or description)",
  "grounding_information": {
    "primary_goals": ["string"],
    "files_and_artifacts_utilized": ["string"],
    "key_constraints_and_assumptions": ["string"],
    "system_or_architecture_context": "string"
  },
  "chronological_timeline": [
    {
      "phase_label": "string (e.g., 'Initial Recon', 'Implementation Attempt 1')",
      "events": [
        {
          "actor": "user | agent | system",
          "action": "string",
          "outcome": "string",
          "timestamp_approx": "string (optional, e.g., 'early in session', '~2h mark')"
        }
      ],
      "key_decisions_made": ["string"],
      "blockers_encountered": ["string"],
      "phase_outcome": "success | partial | failed | abandoned | ongoing"
    }
  ],
  "current_state_assessment": {
    "overall_status": "in_progress | blocked | completed | abandoned",
    "completed_objectives": ["string"],
    "unresolved_threads": ["string"],
    "current_blockers": ["string"]
  },
  "next_path_options": [
    {
      "path_name": "string",
      "description": "string",
      "effort_estimate": "trivial | small | medium | large",
      "pros": ["string"],
      "cons": ["string"],
      "recommended": true
    }
  ]
}
```

### Worked Example (one timeline phase)

```json
{
  "phase_label": "Debugging Force Masking",
  "events": [
    {"actor": "user", "action": "Reported padding atoms drifting to 10^17 Å", "outcome": "Confirmed via position magnitude check", "timestamp_approx": "~30min"},
    {"actor": "agent", "action": "Traced root cause to missing atom_mask in Langevin integrator", "outcome": "Identified fix location in simulate.py:L412", "timestamp_approx": "~45min"},
    {"actor": "agent", "action": "Applied mask to position and momentum updates", "outcome": "Tests pass, padding atoms stable at origin", "timestamp_approx": "~1h"}
  ],
  "key_decisions_made": ["Mask at integrator level rather than force level (belt-and-suspenders)"],
  "blockers_encountered": ["Initial fix broke jax.grad through jnp.where — resolved with stop_gradient"],
  "phase_outcome": "success"
}
```

## Phase 2: Grounding & Entity Extraction

3. **Read the historic context deeply.** Identify the true intended outcomes of the conversation — not just what was discussed, but what the user was trying to accomplish.
4. **Extract Grounding Info.** Catalog:
   - Which files were edited, created, or deleted
   - What artifacts were produced (plans, reports, critiques, outputs)
   - What systems were interacted with (cluster, SLURM, MCP tools, NLM)
   - What assumptions were established and whether they held or were falsified

## Phase 3: Chronological Breakdown

5. **Segment the timeline.** Divide the conversation into logical phases. Each phase represents a major direction or effort (e.g., "Initial Recon", "Implementation Attempt 1", "Debugging Error X", "Pivot to Alternative Approach").
6. **Map events within each phase.** For each phase, document the individual events — who did what, what the outcome was. Capture key decisions and any blockers that shifted the trajectory.

## Phase 4: State Assessment

7. **Determine current status.** Provide a precise assessment of where things stand right now. Use the status enum: `in_progress`, `blocked`, `completed`, `abandoned`.
8. **Catalog threads.** List explicitly:
   - What was successfully completed
   - What remains in-progress or deferred
   - What is actively blocked and why

## Phase 5: Path Generation

9. **Generate Next Paths.** Propose at least 2 structured options for moving forward based on the state assessment.
   - Paths should be **distinct and well-differentiated** — each represents a meaningfully different investment of effort or direction. Paths may be complementary (e.g., "do A then B") as long as each is independently viable.
   - Include clear Pros and Cons for each.
   - Include an `effort_estimate` to set expectations.
   - Designate one path as `recommended` based on the project's overall constraints and current momentum.

## Phase 6: Output & Persist

10. **Generate the structured summary.** Emit the JSON mapping to the schema above.
11. **Create a human-readable companion.** Draft a clear, well-formatted Markdown version of this summary.
12. **Persist the artifacts.**
    - Prefer submitting both via OV MCP `artifact(action: "submit")` with `artifact_type: "conversation_summary"`.
    - **Error handling:** If the MCP submission returns an error, read the message and amend the payload. The `artifact(action: "submit")` payload requires at minimum: `id` (string), `artifact_type` (string), and `content` (string). Retry after amending.
    - **Fallback (last resort only):** Save to `.agent/docs/summaries/conversation_summary.json` and `.agent/docs/summaries/conversation_summary.md` if MCP is critically unavailable.

## Phase 7: Archive Session (New)

Use our specialized archive tools to extract and persist the full conversation history. This ensures that thinking processes and tool outputs are searchable across the entire project.

1.  **Search for relevant sessions**:
    Identify the UUID(s) you wish to archive using fuzzy matching or workspace-aware discovery.
    ```bash
    # Find recent sessions for this workspace
    python3 .agent/workflows/scripts/convo_filter.py

    # Search by keyword
    python3 .agent/workflows/scripts/convo_filter.py --query "Boltzmann"
    ```

2.  **Extract and Concatenate**:
    Pass the desired UUID to the extraction script. This creates a tiered archive at `eph/session-archives/`.
    ```bash
    python3 .agent/workflows/scripts/concatenate_session.py <UUID>
    ```

3.  **Auto-Extract Latest**:
    Quickly archive the most recent session for the current workspace.
    ```bash
    python3 .agent/workflows/scripts/convo_filter.py --latest | xargs python3 .agent/workflows/scripts/concatenate_session.py
    ```

### Output Tier Structure
The generated archive is organized into three sections:
-   **Conversation Turns**: Full thinking steps and tool outputs from `.system_generated/steps/`.
-   **Main Artifacts**: Current state of `implementation_plan.md`, `task.md`, and `walkthrough.md`.
-   **All Artifacts**: Every file in the brain folder, including `.metadata.json` and all `.resolved.N` versions.

## Tips

- **One phase per major direction change.** Don't create a phase for every single message — group by intent. A phase boundary occurs when the approach shifts (e.g., "debugging attempt failed → pivot to new strategy").
- **Collapse long debugging spirals.** If a conversation has 15 failed attempts at the same bug, summarize the pattern: "Attempted 15 variations of X; all failed due to Y." Don't list each.
- **Always at least 2 paths.** Even if one is clearly better, presenting an alternative forces explicit trade-off reasoning.
- **Mark the recommended path clearly.** Set `recommended: true` on exactly one path.
- **Include code locations when relevant.** If the conversation resulted in edits to specific files, cite them by path so the next session can pick up without re-discovering.
- **Archive frequently.** Long-running tasks benefit from periodic archival to prevent context loss during session rotations.
