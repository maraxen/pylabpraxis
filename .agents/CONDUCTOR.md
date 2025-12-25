# Conductor Framework: Agent Interaction Rules

The `conductor` directory houses the project's source of truth for planning and execution. As an AI agent, you MUST adhere to the following rules when interacting with this framework.

## 1. Core Principles

1.  **Plan is Law:** Do not execute tasks that are not in the active track's `plan.md`. If a new task arises, add it to the plan first.
2.  **Single Track Focus:** Work on one track at a time. The active track is marked with `[~]` in `conductor/tracks.md`.
3.  **Status Updates:** You are responsible for maintaining the state of `tracks.md` and the track-specific `plan.md`.

## 2. File Structure

-   `conductor/tracks.md`: The high-level roadmap. Lists all tracks and their status.
-   `conductor/tracks/<track_id>/`: The dedicated folder for a specific track.
    -   `spec.md`: The detailed requirements and acceptance criteria.
    -   `plan.md`: The step-by-step implementation plan with task status.
-   `conductor/workflow.md`: The project's standard operating procedures (Git workflow, testing, etc.).
-   `conductor/tech-stack.md`: The approved technology choices.
-   `conductor/product.md`: The high-level product vision.

## 3. Agent Protocol

When asked to "implement a track" or "continue work":

### Step 1: Context Loading
1.  Read `conductor/tracks.md` to identify the active track (`[~]`) or the next available track.
2.  Read the active track's `spec.md` and `plan.md`.
3.  Read `conductor/workflow.md` to understand the rules of engagement.

### Step 2: Task Execution
1.  Identify the next incomplete task in `plan.md`.
2.  Mark it as in-progress (`[~]`).
3.  Execute the task following TDD (Red -> Green -> Refactor).
4.  Verify the fix/feature.
5.  Commit changes.
6.  Mark the task as complete (`[x]`) in `plan.md` and append the commit hash.

### Step 3: Phase Completion
1.  If a task completes a "Phase" in the plan, perform a "Checkpoint".
2.  Run the full test suite.
3.  If you have browser capabilities, perform the "Manual Verification" steps defined in the plan/workflow.
4.  Create a checkpoint commit.

### Step 4: Track Completion
1.  When all tasks in `plan.md` are `[x]`:
    -   Mark the track as `[x]` in `conductor/tracks.md`.
    -   Review `product.md` and `tech-stack.md` for any necessary updates based on the completed work.
    -   Archive the track folder if requested.

## 4. AntiGravity Specifics

If you are an agent with browser capabilities (like AntiGravity):
-   **Self-Verification:** When a task requires "Manual Verification", you MUST use your browser tool to visit the running application (`http://localhost:4200` usually) and verify the acceptance criteria visually.
-   **Screenshot Evidence:** Take screenshots of the verified state if possible to confirm success.
-   **Troubleshooting:** If the app is not loading, check for backend/frontend processes and restart them if necessary (e.g., `uvicorn`, `npm start`).
