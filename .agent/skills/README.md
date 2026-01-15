# Skills Directory

This directory contains Claude-compatible skills using the [Claude Skills Open Format](https://docs.anthropic.com/en/docs/claude-code/skills).

## Structure

Each skill lives in its own subdirectory with a `SKILL.md` file containing YAML frontmatter:

```
skills/
├── jules-remote/
│   └── SKILL.md          # YAML frontmatter + instructions
├── agentic-workflow/
│   └── SKILL.md          # YAML frontmatter + instructions
└── README.md
```

## SKILL.md Format

Each `SKILL.md` must include:

```markdown
---
name: skill-name
description: When to use this skill and what it does.
---

# Skill Title

Instructions and examples...
```

## Available Skills

| Skill | Description |
|-------|-------------|
| [jules-remote](./jules-remote/SKILL.md) | Dispatch tasks to Jules remote AI agent |
| [agentic-workflow](./agentic-workflow/SKILL.md) | Coordinate strategic and tactical agents |

## Adding a New Skill

1. Create directory: `skills/<skill-name>/`
2. Create `SKILL.md` with YAML frontmatter (`name`, `description`)
3. Add markdown instructions and examples
4. Update this README
