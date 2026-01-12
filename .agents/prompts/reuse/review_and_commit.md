# Reusable Prompt: Review and Commit Changes

This prompt guides the agent through the process of reviewing uncommitted changes in the repository and creating logical, atomic commits.

## Steps

1. **Analyze the Current State**
    * Run `git status` to see staged, unstaged, and untracked files.
    * Run `git diff --stat` to see a summary of changes.
    * If necessary, run `git diff <filename>` to understand specific modifications.

2. **Group Changes logically**
    * Identify distinct tasks or features represented in the changes (e.g., "SQLModel Refactor", "Frontend API Client Gen", "Documentation").
    * Separate "docs" and "agent" changes (updates to `.agents/`, `README.md`, etc.) from code changes.
    * Separate "chores" (dependency updates, config tweaks) if they aren't tightly coupled to a feature.

3. **Create Commits**
    * For each logical group:
        1. `git add <files>` (Be specific! Avoid `git add .` unless you are certain everything belongs).
        2. `git commit -m "<type>(<scope>): <description>"`
            * **Types**: `feat`, `fix`, `refactor`, `chore`, `docs`, `test`, `style`.
            * **Scope**: e.g., `api`, `web-client`, `workcell`, `agent`.
            * **Description**: Concise summary of what changed.

4. **Verify**
    * Run `git status` again to ensure nothing was missed.
    * If untracked files remain, verify if they should be ignored (`.gitignore`), deleted, or added.

## Example

If you see changes to `backend/*.py` and `web-client/*.ts`:

1. Commit backend changes: `git add backend/` -> `git commit -m "refactor(api): switch to SQLModel for user routes"`
2. Commit frontend changes: `git add web-client/` -> `git commit -m "feat(client): update API client types"`

## Rules

* **Never** commit secrets or `.env` files.
* **Verify** tests pass if you are making code changes (unless this is a pure "save progress" step).
* **Consult** `.gitignore` if unsure about untracked files.
