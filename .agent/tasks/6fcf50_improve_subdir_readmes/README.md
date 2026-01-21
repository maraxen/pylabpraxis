# Task: Improve .agent Subdirectory READMEs

## Matrix ID: 6fcf50

## Status: ✅ DONE

## Context

- Priority: P2
- Difficulty: med
- Mode: librarian (planning phase), fixer (execution phase)
- Skills: doc-coauthoring, orchestration
- Research: -
- Workflows: -

## Objective

Improve all `.agent/` subdirectory READMEs to be:

1. **DRY**: No duplicate information across READMEs
2. **Separation of Concerns**: Each README focuses only on its directory's purpose
3. **Consistent Format**: All follow the same structure
4. **Cross-Reference**: Link to related directories/docs instead of duplicating

## Current State

Subdirectories with READMEs:

- `agents/` - Agent mode definitions
- `archive/` - Completed work
- `backlog/` - Future work items
- `codestyles/` - Coding standards
- `pipelines/` - Automation sequences
- `prompts/` - Prompt fragments
- `references/` - External docs
- `reports/` - Status reports
- `research/` - Investigation docs
- `skills/` - Skill definitions (already detailed)
- `status/` - Runtime state
- `tasks/` - Active work
- `templates/` - Document templates
- `workflows/` - Defined procedures

Most READMEs are 3-4 lines with just a title and one-line description.

## Proposed Template

Each subdirectory README should follow this structure:

```markdown
# {Directory Name}

{One-line purpose statement}

## Contents

{Description of what files/subdirs belong here}

## Usage

{How agents should interact with this directory}

## Related

- [{Related Dir}]({path}) - {relationship}
```

## Deliverables

1. **Template**: Create `.agent/templates/subdir_readme.md`
2. **Update READMEs**: Apply template to all 14 subdirectories
3. **Cross-References**: Ensure each README links to related directories
4. **DRY Check**: Verify no duplicate information across READMEs

## Execution Plan

### Phase 1: Create Template (librarian)

- Design the standard README template
- Save to `.agent/templates/subdir_readme.md`

### Phase 2: Generate READMEs (fixer, parallel)

Dispatch parallel updates for each subdirectory. Each dispatch:

- Reads the template
- Writes README specific to that directory
- Includes cross-references

### Phase 3: Verify (explorer)

- Verify all READMEs exist and follow template
- Check for duplicate content across READMEs

## CLI Dispatch Commands

```bash
# Phase 1: Create template
gemini --model gemini-3-pro-preview \
  "Create a standard README template for .agent subdirectories. 
   Follow DRY principles. Output to .agent/templates/subdir_readme.md" \
  --context .agent/README.md

# Phase 2: Update each README (parallel)
for dir in agents archive backlog codestyles pipelines prompts references reports research status tasks templates workflows; do
  gemini --model gemini-3-flash-preview \
    "Update .agent/$dir/README.md using the template. Focus only on this directory's purpose." \
    --context .agent/templates/subdir_readme.md \
    --context .agent/$dir/ &
done
wait

# Phase 3: Verify
gemini --model gemini-3-flash-preview \
  "Verify all subdirectory READMEs follow the template and have no duplicate content" \
  --context .agent/
```

## Success Criteria

- [ ] Template created at `.agent/templates/subdir_readme.md`
- [ ] All 14 subdirectory READMEs updated
- [ ] Each README follows the template
- [ ] No duplicate content across READMEs
- [ ] Cross-references are valid links
