# Context Transfer Protocol

Best practices for transferring context between agent sessions using Jules CLI.

---

## 1. Before Starting Work

```bash
# Check current task status
cat .agents/agent_tasks.jsonl | jq -s 'map(select(.status == "TODO" or .status == "IN_PROGRESS"))'

# Review the tiered plan
cat .agents/251208_BACKEND_DEV.md

# Verify test database is running
docker ps | grep postgres || docker compose -f docker-compose.test.yml up -d

# Check current test status
uv run pytest --co -q | tail -5
```

---

## 2. Claiming a Task

Update `.agents/agent_tasks.jsonl` by adding your agent name:
```json
{"id": "T1.1", "status": "IN_PROGRESS", "assignee": "AgentName", ...}
```

---

## 3. Jules CLI Dispatch

### Dispatch a Simple Task (Tier 1)
```bash
# Single task dispatch
jules new "Complete task T1.1: Remove excess files (dependency_analysis.py, verify_db.py, praxis.egg-info/). After removal, update .agents/agent_tasks.jsonl to mark T1.1 as DONE."

# Multiple parallel tasks
jules new --parallel 3 "Complete Tier 1 tasks from .agents/251208_BACKEND_DEV.md"
```

### Dispatch a Medium Task (Tier 2)
```bash
jules new "Complete task T2.2: Fix Ruff linting issues. Run 'uv run ruff check . --statistics' first, then fix F/E/B errors. Update .agents/agent_tasks.jsonl when done."
```

### Dispatch a Complex Task (Tier 3)
```bash
jules new "Complete task T3.1: Fix tests/helpers.py ORM instantiation patterns. Key pattern: do NOT pass init=False relationships to MappedAsDataclass constructors. Pass FK IDs instead, then assign relationship objects after instantiation. Reference agent_history patterns from .agents/REFACTORING_STRATEGY.md. Update .agents/agent_tasks.jsonl when done."
```

### List Active Sessions
```bash
jules remote list --session
```

### Pull and Apply Results
```bash
# Pull results from a session
jules remote pull --session <SESSION_ID>

# Pull and auto-apply patch
jules remote pull --session <SESSION_ID> --apply
```

---

## 4. Task Completion Protocol

After completing work:

1. **Update task status:**
   ```bash
   # Edit .agents/agent_tasks.jsonl - change status to DONE
   ```

2. **Run verification:**
   ```bash
   uv run pytest --cov=praxis/backend --cov-report=term-missing
   uv run ruff check . --fix
   ```

3. **Commit changes:**
   ```bash
   git add -A
   git commit -m "feat(tests): complete task T<ID> - <brief description>"
   ```

---

## 5. Handoff Summary Template

When handing off work, provide:

```markdown
### Last Known State
- **Completed Tasks:** T1.1, T2.2
- **Current Task:** T3.1 (IN_PROGRESS)
- **Test Status:** 45% coverage, X failing tests
- **Branch:** main

### Next Steps
1. Immediate: [specific action]
2. Blocked by: [any blockers]

### Key Learnings
- [Any architectural insights]
- [ORM patterns discovered]
```

---

## 6. Key Files Reference

| File | Purpose |
|------|---------|
| `.agents/251208_BACKEND_DEV.md` | Tiered task checklist |
| `.agents/agent_tasks.jsonl` | Task status tracking |
| `.agents/PRODUCTION_BUGS.md` | Known production bugs |
| `.agents/REFACTORING_STRATEGY.md` | Refactoring patterns |
| `.agents/FRONTEND_DEV.md` | Frontend Architecture & Roadmap |
| `AGENTS.md` | Development conventions |
| `tests/helpers.py` | Test data creation patterns |

---

## 7. ORM Pattern Quick Reference

**WRONG** (causes TypeError):
```python
orm = SomeOrm(relationship_obj=obj, accession_id=uuid7())
```

**CORRECT**:
```python
orm = SomeOrm(relationship_accession_id=obj.accession_id)
orm.relationship = obj  # Assign after construction
```

This pattern is required because MappedAsDataclass uses `init=False` for relationships.
