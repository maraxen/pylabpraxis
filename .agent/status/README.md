# Status

> Runtime state and progress tracking files.

## What Goes Here

JSON/YAML files tracking agent runtime state, coordination signals, and progress metrics. Machine-readable status for automation.

## How to Use

1. **Check status**: Read `status.json` for current state
2. **Update programmatically**: Scripts update these files
3. **Coordinate agents**: Use for cross-agent signaling

## Related

- [DEVELOPMENT_MATRIX.md](../DEVELOPMENT_MATRIX.md) - Human-readable task status
- [tasks/](../tasks/) - Task-specific tracking in `tracking/` subdirs

---

*Part of the [.agent coordination hub](../README.md)*
