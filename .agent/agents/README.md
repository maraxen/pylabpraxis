# Agents

> Specialized agent mode definitions and system prompts.

## What Goes Here

Agent prompt files (`.md`) that define different operating modes. Each file contains a system prompt that transforms the base model into a specialized agent with specific behaviors, skills, and constraints.

## How to Use

1. **Load mode**: Read the agent file matching the requested mode
2. **Default mode**: Use `evolving-orchestrator.md` if no mode specified
3. **Mode switching**: User says "Acting as {mode}" to switch

## Available Agents

See the files in this directory. Each follows the pattern `{mode-name}.md`.

## Related

- [AGENTS.md](../../AGENTS.md) - Agent routing and mode selection table
- [skills/](../skills/) - Skills that agents can invoke

---

*Part of the [.agent coordination hub](../README.md)*
