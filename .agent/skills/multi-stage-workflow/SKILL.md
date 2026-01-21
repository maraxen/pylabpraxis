# Skill: Structured Multi-Stage Workflow

**Version**: 1.0
**Author**: [Your Name/Team]

## Overview

This skill formalizes the standard Inspect→Plan→Execute development cycle into a structured, multi-stage workflow. It is designed to guide an agent through a systematic process of understanding, implementing, and verifying a change request. Each stage has clear entry and exit criteria, produces specific artifacts, and includes updates to project tracking systems.

---

## Stage 1: Clarification & Specification

**Objective**: To transform an initial user request into a well-defined, actionable specification.

**Entry Criteria**:
- A new task or change request has been received from the user.

**Process**:
1.  **Analyze Request**: Carefully read the user's request to understand the high-level goal.
2.  **Ask Clarifying Questions**: If the request is ambiguous, incomplete, or contains conflicting requirements, use the `request_user_input` tool to ask targeted questions.
3.  **Negotiate Scope**: Work with the user to define clear, achievable boundaries for the task.
4.  **Formalize Specification**: Document the agreed-upon requirements.

**Exit Criteria**:
- All ambiguities in the user request have been resolved.
- A clear, documented specification has been agreed upon with the user.

**Artifacts**:
- **Specification Document**: A clear, written summary of the task requirements, scope, and acceptance criteria. This may be recorded in the agent's internal memory, a project management tool, or a temporary markdown file.

**Tracking**:
- **Task Status**: Update the task from `New` to `In Progress` or `Specification`.
- **Technical Debt**: Log any identified compromises or future work that is out of scope for the current task.

---

## Stage 2: Inspection & Discovery

**Objective**: To build a comprehensive understanding of the existing codebase and its context relevant to the task.

**Entry Criteria**:
- A clear specification from Stage 1.

**Process**:
1.  **File & Directory Listing**: Use `list_files` to explore the repository structure.
2.  **Code Review**: Use `read_file` to examine relevant files identified in the previous step. Pay attention to coding patterns, existing abstractions, and potential areas of impact.
3.  **Search & Grep**: Use `run_in_bash_session` with `grep` to find all occurrences of specific functions, variables, or patterns related to the task.
4.  **Read Documentation**: Review `README.md`, `AGENTS.md`, and any other relevant documentation files.
5.  **Synthesize Findings**: Consolidate the gathered information to build a mental model of the change.

**Exit Criteria**:
- The agent has a sufficient understanding of the codebase to formulate a detailed implementation plan.
- All relevant files, modules, and dependencies have been identified.

**Artifacts**:
- **Discovery Notes**: A collection of findings, including a list of files to be modified, key code snippets, and a summary of the architectural approach.

**Tracking**:
- **Task Status**: No change, remains `In Progress` or `Specification`.
- **Technical Debt**: Update or add items based on discoveries (e.g., outdated dependencies, poor code quality in areas to be modified).

---

## Stage 3: Planning

**Objective**: To create a detailed, step-by-step implementation plan.

**Entry Criteria**:
- Completion of the Inspection stage.
- A set of discovery artifacts.

**Process**:
1.  **Decompose the Problem**: Break down the high-level specification into smaller, manageable implementation steps.
2.  **Sequence the Steps**: Order the steps logically, considering dependencies between them.
3.  **Define Verification for Each Step**: For each step, determine how the outcome will be verified (e.g., "confirm file exists with `ls`," "run unit test and expect it to fail").
4.  **Formalize the Plan**: Use the `set_plan` tool to articulate the final plan. The plan must include a pre-commit step for final checks.

**Exit Criteria**:
- A formal plan has been created and stored using the `set_plan` tool.
- The user has approved the plan if it's the first plan for the task.

**Artifacts**:
- **Implementation Plan**: The structured plan set via the `set_plan` tool.

**Tracking**:
- **Task Status**: Update to `In Progress` or `Implementation`.

---

## Stage 4: Execution

**Objective**: To implement the code changes as defined in the plan.

**Entry Criteria**:
- An approved implementation plan from Stage 3.

**Process**:
1.  **Execute Plan Step-by-Step**: Follow the plan meticulously, executing one step at a time.
2.  **Write Code**: Use tools like `write_file` and `replace_with_git_merge_diff` to create or modify files.
3.  **Write Tests**: When implementing new features or fixing bugs, write corresponding unit or integration tests. Practice test-driven development where appropriate.
4.  **Verify Each Step**: After each modification, use a read-only tool (`read_file`, `list_files`, etc.) to confirm the change was applied correctly.
5.  **Mark Step Complete**: Use `plan_step_complete` to move to the next step.

**Exit Criteria**:
- All steps in the implementation plan have been completed.
- The code has been modified and new tests have been written.

**Artifacts**:
- **Modified Source Code**: The changes made to the repository's files.
- **New Tests**: The test files added to validate the changes.

**Tracking**:
- **Task Status**: Remains `In Progress` or `Implementation`.

---

## Stage 5: Verification & Submission

**Objective**: To validate the completed work against the specification and submit it.

**Entry Criteria**:
- All plan steps from the Execution stage are complete.

**Process**:
1.  **Run All Tests**: Execute the entire test suite to ensure the changes have not introduced any regressions.
2.  **Perform Pre-Commit Checks**: Call `pre_commit_instructions` and follow all required steps (e.g., linting, static analysis, final verification).
3.  **Manual Verification (if applicable)**: If the change impacts a user interface or requires visual confirmation, use appropriate verification tools and generate screenshots.
4.  **Submit for Review**: Once all checks pass, use the `submit` tool with a clear, descriptive commit message.

**Exit Criteria**:
- All tests and pre-commit checks pass.
- The change has been successfully submitted.

**Artifacts**:
- **Test Results**: Output from the test runner.
- **Verification Screenshots** (if applicable).
- **Commit**: The final commit pushed to the repository.

**Tracking**:
- **Task Status**: Update to `Completed`, `In Review`, or `Done`.
- **Technical Debt**: Ensure all related debt items are linked to the completed task.
