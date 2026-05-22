---
description: Create a comprehensive, two-tier documentation suite for a directory
---
# Document Directory Workflow

Generates a comprehensive two-tier documentation suite (`README.md` and `IN_DEPTH.md`) for any target directory, ensuring 100% coverage of all files and maintaining a clear status tagging system.

## When to Use
- When documenting scripts, utilities, or standalone module directories.
- When existing documentation is out of sync with reality (missing files, stale descriptions).
- When standardizing documentation formatting across multiple directories.

## Inputs
| Input | Description |
|-------|-------------|
| `TargetPath` | Absolute or relative path to the directory to document. |
| `Recursive` | Boolean indicating whether to audit and document sub-directories. Defaults to `false`. |

## Phase 1: Audit and Categorization Proposal
Before writing any documentation, perform a complete directory audit to ensure no files are missed.

1. **Audit Files**: Read the directory contents based on the `Recursive` input. Count the total number of target files.
2. **Track the Task**: Create or update the `task.md` artifact with a checklist of every single file discovered in the target path to ensure files are not lost during long contexts.
3. **Review Context**: Read the first few dozen lines of several files to understand the overarching purpose of the directory.
4. **Propose Categories**: Design 4-6 functional categories to group the files. Categories should reflect the lifecycle and usage patterns of the directory (e.g., Infrastructure, Data Engineering, Utilities). 
5. **Draft Proposal**: Formulate the proposed bucketing. Ensure every single file mapped during the audit belongs to precisely one category.

## Phase 2: Documentation Structure Definitions
The standard output for this workflow is two files:

### `README.md` (The Index)
A high-level index focusing on rapid navigation.
- Must include YAML frontmatter with a description.
- A categorized `Navigation Index` table at the top linking to the individual sections.
- One table per category containing:
  - **Script/File**: A markdown link pointing to the file's detailed anchor in `IN_DEPTH.md`.
  - **Status**: Define a project-relevant emoji-based status tagging taxonomy (e.g., Active, Deprecated, Experimental) and apply it. (Example from Phyllo: `✅ AUTH`, `⚠️ LEGA`, `🧪 EXPE`).
  - **Description**: A concise, 1-sentence summary of the file's purpose.

### `IN_DEPTH.md` (The Deep Dive)
A technical reference manual detailing execution instructions.
- A `Category Index` linking to the sections below.
- One section per category. Within each category, wrap the file listings in `<details open>` and `<summary>View Scripts</summary>` tags for collapsibility.
- For every file, use an `### filename.ext` heading (ensure this matches the link from `README.md`) and include:
  - **Logic**: A 1-3 sentence explanation of the underlying algorithm or primary effect.
  - **Execution**: How/where to run it (e.g. Local vs. Cluster), and external dependencies if highly specific.
  - **Caveats**: Hardcoded paths, extreme memory requirements, warnings, or known side-effects.

## Phase 3: Iterative Execution Strategy
1. For directories larger than 15 files, strictly perform execution in batches (e.g., 10-15 files at a time) to maintain technical depth and response quality.
2. For each batch, read the actual code or docstrings of the files to extract logic and caveats.
3. Append (do not overwrite) the updates to `README.md` and `IN_DEPTH.md`.
4. Check off the completed files in `task.md`.
5. Continue until all batches are completed.

## Phase 4: Final Validation and Critique
After all files are documented:

1. **Conduct Gap Analysis**: Check the items written into `README.md` against the master checklist in `task.md`. Ensure there is exactly 100% overlap. No files should be missing, no files should be duplicated.
2. **Verify Anchors**: Validate that all markdown links in `README.md` correctly point to the generated `###` headers in `IN_DEPTH.md`.
3. **Category Bleed Check**: Ensure each file is listed in the correct category section and `<details>` block without cross-category bleeding.
4. **Fix Issues**: Immediately rectify any omissions or link breakages.
