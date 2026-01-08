# Maintenance Prompt: Performance Audit

**Purpose:** Review performance and identify bottlenecks  
**Frequency:** As needed  

---

## Prompt

```markdown
Examine .agents/README.md for development context.

## Task

Review performance and identify potential bottlenecks.

## Phase 1: Triage

1. **Backend Profiling** (if specific endpoints are slow):

   ```bash
   # Use cProfile for specific modules
   uv run python -m cProfile -s cumtime praxis/backend/path/to/script.py 2>&1 | head -n 50
   ```

1. **Frontend Bundle Analysis**:

   ```bash
   cd praxis/web-client && npm run build -- --stats-json
   # Then analyze bundle with webpack-bundle-analyzer
   ```

2. **Database Query Analysis**: Check for N+1 queries, missing indexes.

## Phase 2: Categorize and Strategize

1. **Categorize Issues**:

   | Category | Symptoms | Typical Fix |
   |:---------|:---------|:------------|
   | **Slow DB queries** | High latency on list endpoints | Add indexes, optimize queries |
   | **N+1 queries** | Many small queries | Use eager loading |
   | **Large bundles** | Slow initial load | Code splitting, lazy loading |
   | **Memory leaks** | Growing memory usage | Fix subscriptions, cleanup |
   | **Blocking I/O** | Slow API responses | Use async/await |

2. **Document Strategy** before making changes.

3. **Get User Input**: ⏸️ PAUSE for approval.

## Phase 3: Apply Fixes

1. **Database Optimizations**:
   - Add indexes for frequently queried fields
   - Use eager loading for related data
   - Paginate large result sets

2. **Backend Optimizations**:
   - Use async endpoints for I/O
   - Cache expensive computations
   - Batch database operations

3. **Frontend Optimizations**:
   - Lazy load routes and components
   - Use OnPush change detection
   - Optimize RxJS subscriptions

## Phase 4: Verify and Document

1. **Benchmark Before/After**.
2. **Update Health Audits**.

## References

- [codestyles/python.md](../../../codestyles/python.md)

```

---

## Customization

This prompt is pre-configured for Praxis. No placeholders needed.
