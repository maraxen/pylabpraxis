---
name: atomic-git-commit
description: Interactive workflow to review changes, split them into logical groups, and create atomic conventional commits. Replaces 'git commit -m' with a thoughtful process.
---

# Atomic Git Commit Workflow

This skill guides you through the process of reviewing uncommitted changes, grouping them logically, and creating atomic commits following Conventional Commits standards.

## When to Use

- When the user asks to "commit changes", "review and commit", "save work".
- When you have completed a task and have modified multiple files.
- **Do NOT use** for "fire and forget" saves (use `git-pushing` for that). This is for *thoughtful* committing.

## Workflow

### 1. Analyze State

Run the following checks to understand what has changed:

```bash
git status
git diff --stat
```

### 2. Group Changes

**CRITICAL**: Do not just `git add .` unless all changes are strictly related to a single atomic unit of work.

- **Feat**: New features.
- **Fix**: Bug fixes.
- **Chore**: Maintenance, config, `.agent` updates.
- **Docs**: Documentation changes.

*Interactive Thought Process:*
"I see changes in `backend/` and `frontend/`. Are they part of the same feature? If yes, commit together. If they are separate fixes, split them."

### 3. Commit

For each logical group:

1. Stage specific files: `git add <file1> <file2>`
2. Commit with conventional message:

   ```bash
   git commit -m "<type>(<scope>): <description>"
   ```

**Types**: `feat`, `fix`, `docs`, `style`, `refactor`, `perf`, `test`, `build`, `ci`, `chore`, `revert`.

### 4. Verify

- Ensure no unintended files (secrets, `.env`, temporary logs) are committed.
- Check `git status` one last time.

## Local Overrides

Check if `.agent/local-rules/commit-conventions.md` exists for project-specific commit rules.
