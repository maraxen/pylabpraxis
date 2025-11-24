# Context Transfer Best Practices

This document outlines the procedure for transferring context between agent sessions or developers to ensure seamless handoffs, minimize knowledge loss, and accelerate onboarding for new contributors.

## 1. Principle of Explicit Context

The core principle is **explicit context**. Do not assume the next agent or developer has the same implicit understanding of the project. All relevant information must be documented in a structured and accessible way.

## 2. Context Transfer Procedure

When pausing or handing off work, create a context transfer package consisting of the following:

### 2.1. Update `agent_history.jsonl`
-   Append a new JSON object to `agent_history.jsonl` summarizing the completed work, key decisions made, and the state of the repository. Use the format specified in `AGENTS.md`.

### 2.2. Provide a Structured Handoff Summary
Create a summary that includes the following sections:

-   **Last Known State**:
    -   **Objective**: What was the overall goal of the work you were doing?
    -   **Current Plan Step**: Which step of the plan were you working on?
    -   **File Status**: List any files that were created, modified, or deleted.
    -   **Branch**: What is the name of the current Git branch?
    -   **Verification Status**: Have the latest changes been verified? Is the test suite passing?

-   **Next Steps**:
    -   **Immediate Goal**: What is the immediate next action to be taken?
    -   **Potential Blockers**: Are there any anticipated challenges, open questions, or dependencies?

-   **Key Learnings and Discoveries**:
    -   **Architectural Insights**: Did you uncover any important details about the system's architecture?
    -   **Tooling or Process Notes**: Are there any new findings related to the development process, tools, or commands?

## 3. Onboarding Procedure

When starting a new session or taking over work, follow these steps:

1.  **Review Core Documentation**:
    -   Read `AGENTS.md` to understand the project's development norms and standards.
    -   Read `docs/architecture.md` to understand the system's design.

2.  **Review Historical Context**:
    -   Consult `agent_history.jsonl` to understand the evolution of the project and past agent contributions. As this is a JSONL file, you can search it programmatically without loading the entire file.

3.  **Review the Latest Handoff**:
    -   Locate and read the most recent context transfer summary.

4.  **Verify the Current State**:
    -   Use `git status` to check for uncommitted changes.
    -   Run the test suite (`uv run pytest`) to confirm that the project is in a stable state.
    -   List the files in the repository to familiarize yourself with the current structure.

By following this structured process, we can ensure that every contributor has the necessary information to work effectively, leading to faster progress and higher-quality outcomes.
