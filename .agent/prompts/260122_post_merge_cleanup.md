# Agent Prompt: Post-Merge Cleanup (Archive Branches + Rename)

**Status:** 🟡 Not Started (Blocked: Requires user actions on GitHub)
**Priority:** P0 (First thing post-merge)
**Difficulty:** Easy-Medium
**Category:** Repository Maintenance

---

## Overview

This prompt covers the FIRST actions to take after the `angular_refactor` → `main` merge:

1. **Archive/Delete Old Branches** - Clean up stale branches (except `main` and `github-pages`)
2. **Rename Project** - Update all internal pointers programmatically

**CRITICAL:** These actions require USER intervention on GitHub for some steps. The agent should prepare everything possible and provide clear instructions for manual steps.

---

## Part 1: Archive Branches

### User Actions Required (GitHub)

The user must perform these actions on GitHub:

1. Go to repository Settings → Branches
2. Change default branch to `main` if not already
3. Delete the following branches (after confirming they're merged or obsolete):

**Branches to KEEP:**

- `main` - Primary branch
- `github-pages` - Documentation hosting

**Branches to ARCHIVE/DELETE:**
(Agent should list all other branches found)

### Agent Recon Tasks

```bash
# List all remote branches
git branch -r

# List all local branches
git branch -a

# Check which branches are merged into main
git branch -r --merged main

# Check which branches are NOT merged (potential data loss)
git branch -r --no-merged main
```

### Output Format for User

```xml
<branch_audit>
<keep>
  <branch name="main" reason="Primary branch"/>
  <branch name="github-pages" reason="Documentation hosting"/>
</keep>

<safe_to_delete merged="true">
  <branch name="[branch]" last_commit="[date]" merged_into="[target]"/>
</safe_to_delete>

<unmerged_branches needs_review="true">
  <branch name="[branch]" last_commit="[date]" status="NOT MERGED - Review before deleting"/>
</unmerged_branches>

<user_instructions>
1. Go to GitHub → Repository → Branches
2. Delete the following branches: [list]
3. For unmerged branches, verify they are obsolete before deleting
</user_instructions>
</branch_audit>
```

---

## Part 2: Project Rename

### Prerequisites

- User provides the NEW project name
- Merge is complete
- Clean working directory

### Rename Scope

The following need to be updated:

1. **package.json files** - `name` field
2. **angular.json** - Project name references
3. **README.md** - Project name/title
4. **Docker files** - Image names if any
5. **CI/CD configs** - If any reference project name
6. **Import paths** - If project name is in import paths

### Agent Tasks

```bash
# Find all package.json files
find . -name "package.json" -not -path "./node_modules/*"

# Find project name references (current name: pylabpraxis, praxis)
grep -r "pylabpraxis\|praxis" --include="package.json" --include="*.json"
grep -r "pylabpraxis" README.md .github/ docker* Docker* 2>/dev/null

# Find angular project references
grep -r "praxis" angular.json
```

### Rename Strategy

1. **Create a sed script** or use search-replace tool
2. **Verify changes before committing** - git diff
3. **Test build after rename** - npm run build
4. **Commit with conventional message** - `chore: rename project from X to Y`

### Output Format

```xml
<rename_plan>
<current_name>pylabpraxis / praxis</current_name>
<new_name>[USER MUST PROVIDE]</new_name>

<files_to_update>
  <file path="package.json" changes="[what changes]"/>
  <file path="praxis/web-client/package.json" changes="[what changes]"/>
  <file path="angular.json" changes="[what changes]"/>
  <file path="README.md" changes="[what changes]"/>
</files_to_update>

<verification_steps>
  1. Run npm install to verify package.json valid
  2. Run npm run build to verify angular.json valid
  3. Run tests to verify nothing broke
</verification_steps>

<commit_message>
chore: rename project from [old] to [new]
</commit_message>
</rename_plan>
```

---

## Context & Notes

**Why First Post-Merge:**

- Rename affects many files - better to do on clean slate
- Branches should be cleaned before more divergence happens
- Sets up clean foundation for v0.1-alpha release

**Safety Checks:**

- ALWAYS create a backup branch before rename: `git checkout -b backup-pre-rename`
- ALWAYS verify build works after rename
- NEVER delete branches without confirming merge status

---

## On Completion

### Branch Cleanup

- [ ] Listed all branches
- [ ] Identified safe-to-delete branches
- [ ] Provided user instructions
- [ ] User confirmed deletions on GitHub

### Rename (if pursued)

- [ ] User provided new name
- [ ] Identified all files to update
- [ ] Created backup branch
- [ ] Executed rename
- [ ] Verified build passes
- [ ] Committed changes

---

## References

- `.agent/README.md` - Project structure
- Git branching best practices
