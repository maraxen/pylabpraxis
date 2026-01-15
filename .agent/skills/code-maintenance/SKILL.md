---
name: code-maintenance
description: Suite of tools and workflows for project health, linting, audits, and cleanup.
---

# Code Maintenance

This skill provides a structured way to perform recurring maintenance tasks on the Pylabpraxis codebase.

## Workflows

Check the [references/](references/) directory for specific protocols.

### 1. Linting & Formatting

**Trigger**: "Run linting", "Fix lint errors", "Format code"

1. Run linters on backend and frontend.
2. Resolve violations.
3. Update health audits in `.agent/`.

Reference: [references/linting.md](references/linting.md)

### 2. Code Audits

**Triggers**: "Dead code cleanup", "Docstring audit", "Performance audit", "Security audit"

Use the specific reference files to guide the audit process:

- [references/dead_code_cleanup.md](references/dead_code_cleanup.md)
- [references/docstring_audit.md](references/docstring_audit.md)
- [references/performance_audit.md](references/performance_audit.md)
- [references/security_audit.md](references/security_audit.md)
- [references/dependency_audit.md](references/dependency_audit.md)

### 3. Health Templates

Templates for audits are stored in [assets/](assets/):

- `health_audit_backend.md`
- `health_audit_frontend.md`

## Project Context

Always consult `.agent/README.md` before performing maintenance to understand the current priority and environment state.
