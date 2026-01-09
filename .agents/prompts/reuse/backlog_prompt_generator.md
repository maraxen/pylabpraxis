# Backlog Prompt Generator

Examine .agents/README.md for development context.

## Task

Act as a **Senior Technical Architect**. Review the development tracking documents, investigate the codebase, and generate highly detailed, scaffolded agent prompts for prioritized backlog items.

## Instructions

1. **Review Documents**:
   - [DEVELOPMENT_MATRIX.md](.agents/DEVELOPMENT_MATRIX.md) - Current priorities and statuses
   - [ROADMAP.md](.agents/ROADMAP.md) - Quarterly milestones
   - [backlog/](.agents/backlog/) - Detailed work item specifications

2. **Select Items**: Identify {N_ITEMS} high-priority items to address based on:
   - Priority (High → Medium → Low)
   - Status (🟢 Planned items ready for work)
   - Dependencies (unblocked items first)
   - Difficulty appropriate for agent dispatch

3. **Phase 1: Reconnaissance (Crucial)**
   Before generating any prompts, you must **Audit the Codebase** for *each* selected item using your tools:
    - Locate the specific files that need modification.
    - Identify relevant existing components, services, or backend endpoints that must be consumed or extended.
    - Check for existing patterns (e.g., "How are dialogs currently implemented in `praxis/web-client`?").
    - *Do not guess file paths. Find the actual paths.*

4. **Phase 2: Scaffolding & Generation**
   For each selected item, create a prompt file following the [agent_prompt.md](.agents/templates/agent_prompt.md) template. You must fill the template with **architectural detail**, not just requirements.
   - **Context Files**: List *absolute* repository paths for every file the agent will need to touch or read.
   - **Technical Implementation Strategy**:
     - **Architecture**: Specify exactly which Angular Services, Python Modules, or Database Tables are involved.
     - **Pseudocode/Flow**: Briefly describe the data flow or component hierarchy.
     - **Sharp Bits**: Warn about specific complexities or known technical debt.
   - **Project Conventions**:
     - Use `uv run` for Python commands
     - Use `praxis/backend` for backend code paths
     - Use `praxis/web-client` for frontend code paths
   - **Verification Plan**:
     - Provide the exact command to run the relevant tests (e.g., `uv run pytest tests/api/test_resources.py`).
     - If no tests exist, instruct the agent to create a specific test file.
   - **Save Location**: `.agents/prompts/{BATCH_DATE}/[priority]_[slug].md`

5. **Create Batch README**: Create `.agents/prompts/{BATCH_DATE}/README.md` listing all generated prompts with status tracking.

6. **Ask for clarification and specification** where:
   - Backlog items lack sufficient detail for implementation
   - Priority conflicts exist between items
   - Dependencies are unclear or blocking

## Output

Provide a summary table of generated prompts with:

- Prompt filename
- Backlog item addressed
- Estimated complexity
- Key implementation targets (Specific files)
- Verification command (Primary test to run)
