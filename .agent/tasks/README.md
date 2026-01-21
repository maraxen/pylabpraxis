# Tasks

> Active task directories linked via DEVELOPMENT_MATRIX ID.

## What Goes Here

Task directories named `{matrix_id}_{task_name}/`. Each contains a README.md with objectives, a `tracking/` subdir for logs, and `artifacts/` for outputs.

## How to Use

1. **Create from matrix**: When starting a matrix item, create `{id}_{name}/`
2. **Follow I-P-E-T**: Inspect → Plan → Execute → Test phases
3. **Move when done**: Archive to `archive/` when complete

## Structure

```
{id}_{name}/
├── README.md      # Task definition and status
├── tracking/      # Progress logs, grep results
└── artifacts/     # Generated outputs
```

## Related

- [DEVELOPMENT_MATRIX.md](../DEVELOPMENT_MATRIX.md) - Task registry (ID source)
- [archive/](../archive/) - Completed tasks move here
- [templates/unified_task.md](../templates/unified_task.md) - Task README template

---

*Part of the [.agent coordination hub](../README.md)*
