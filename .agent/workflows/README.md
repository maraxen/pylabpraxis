# Workflows

> Defined procedures for standard development tasks.

## What Goes Here

Step-by-step workflow definitions for repeatable processes. Each workflow is a `.md` file with YAML frontmatter and markdown instructions.

## How to Use

1. **Follow workflows**: Read and execute workflow steps in order
2. **Reference in matrix**: Link workflows in the Workflows column
3. **Create workflows**: Document new repeatable processes

## Workflow Format

```yaml
---
description: Short description
---
1. Step one
2. Step two
// turbo annotation for auto-run steps
3. Auto-run step
```

## Related

- [pipelines/](../pipelines/) - More complex automation sequences
- [DEVELOPMENT_MATRIX.md](../DEVELOPMENT_MATRIX.md) - Links workflows to tasks

---

*Part of the [.agent coordination hub](../README.md)*
