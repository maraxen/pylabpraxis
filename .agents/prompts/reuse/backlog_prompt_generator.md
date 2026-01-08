# Reusable Prompt: Backlog Prompt Generator

Examine .agents/README.md for development context.

**Purpose:** Review development tracking docs and generate targeted agent prompts for backlog items  
**Use when:** Planning a sprint or batch of work, dispatching agents to address backlog items

---

## Prompt

```
Examine .agents/README.md for development context.

## Task

Review the development tracking documents and generate targeted agent prompts to address prioritized backlog items.

## Instructions

1. **Review Documents**:
   - [DEVELOPMENT_MATRIX.md](.agents/DEVELOPMENT_MATRIX.md) - Current priorities and statuses
   - [ROADMAP.md](.agents/ROADMAP.md) - Quarterly milestones
   - [backlog/](.agents/backlog/) - Detailed work item specifications

2. **Select Items**: Identify {N_ITEMS} items to address based on:
   - Priority (High → Medium → Low)
   - Status (🟢 Planned items ready for work)
   - Dependencies (unblocked items first)
   - Difficulty appropriate for agent dispatch

3. **Generate Prompts**: For each selected item, create a prompt file following the [agent_prompt.md](.agents/templates/agent_prompt.md) template:
   - Save to `.agents/prompts/{BATCH_DATE}/NN_item_name.md`
   - Include specific context files and implementation details from the backlog item
   - Reference relevant codestyles and project conventions:
     - Use `uv run` for Python commands
     - Use `praxis/backend` for backend code paths
     - Use `praxis/web-client` for frontend code paths
   - Include on-completion step to commit changes with descriptive message

4. **Create Batch README**: Create `.agents/prompts/{BATCH_DATE}/README.md` listing all generated prompts with status tracking (use `agent_tasks.jsonl` format if applicable or standard markdown table from templates).

5. **Ask for clarification and specification** where:
   - Backlog items lack sufficient detail for implementation
   - Priority conflicts exist between items
   - Dependencies are unclear or blocking

## Output

Provide a summary table of generated prompts with:
- Prompt filename
- Backlog item addressed
- Estimated complexity
- Key implementation targets
```

---

## Customization

| Placeholder | Description | Example |
|:------------|:------------|:--------|
| `{N_ITEMS}` | Number of items to select | 5 |
| `{BATCH_DATE}` | Date folder YYMMDD format | 260108 |

---

## Example Usage

```
Examine .agents/README.md for development context.

## Task

Review the development tracking documents and generate targeted agent prompts to address prioritized backlog items.

## Instructions

1. **Review Documents**:
   - [DEVELOPMENT_MATRIX.md](.agents/DEVELOPMENT_MATRIX.md) - Current priorities and statuses
   - [ROADMAP.md](.agents/ROADMAP.md) - Quarterly milestones
   - [backlog/](.agents/backlog/) - Detailed work item specifications

2. **Select Items**: Identify 5 items to address based on:
   - Priority (High → Medium → Low)
   - Status (🟢 Planned items ready for work)
   - Dependencies (unblocked items first)
   - Difficulty appropriate for agent dispatch

3. **Generate Prompts**: For each selected item, create a prompt file following the [agent_prompt.md](.agents/templates/agent_prompt.md) template:
   - Save to `.agents/prompts/260108/NN_item_name.md`
   - Include specific context files and implementation details from the backlog item
   - Reference relevant codestyles and project conventions
   - Include on-completion step to commit changes with descriptive message

4. **Create Batch README**: Create `.agents/prompts/260108/README.md` listing all generated prompts with status tracking.

5. **Ask for clarification and specification** where:
   - Backlog items lack sufficient detail for implementation
   - Priority conflicts exist between items
   - Dependencies are unclear or blocking

## Output

Provide a summary table of generated prompts with:
- Prompt filename
- Backlog item addressed
- Estimated complexity
- Key implementation targets
```
