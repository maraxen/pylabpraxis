# Agent Prompt: Simulated Backend Clarity

Examine `.agents/README.md` for development context.

**Status:** 🟢 Not Started
**Priority:** P2
**Batch:** [260112](./README.md)
**Backlog Reference:** [simulation.md](../../backlog/simulation.md)

---

## 1. The Task

Clean up and clarify the simulation architecture:
1. Remove all "demo" naming from simulated frontends/backends
2. Use consistent "Simulated" prefix for all simulation components
3. Document what each simulated component does
4. Clarify which simulated frontends use ChatterboxBackend vs other approaches

**User Value:** Developers and users clearly understand simulation behavior. No confusion from legacy "demo" terminology.

---

## 2. Technical Implementation Strategy

### Investigation Phase

1. **Audit simulation implementations**
   - Search for "demo", "Demo" across codebase
   - Identify all simulated backend classes
   - Map which frontends connect to which backends

2. **Document current architecture**
   - List all `Simulated*` classes
   - Note which use `ChatterboxBackend`
   - Identify any inconsistencies

### Cleanup Phase

1. **Rename "demo" to "simulated"**
   - Any class/variable with "demo" prefix → "simulated"
   - Update imports and references
   - Update any user-facing strings

2. **Standardize naming convention**
   - `SimulatedPlateReader`, `SimulatedHeaterShaker`, etc.
   - Ensure 1:1 mapping of simulated frontend per machine category

3. **Add documentation**
   - Document simulation behavior in code comments
   - Update `praxis/web-client/src/assets/docs/architecture/simulation.md` if needed

### Files to Check

Based on grep results, these files contain "demo" references:
- `praxis/web-client/src/app/features/assets/components/machine-filters/`
- `praxis/backend/configure.py`
- `praxis/protocol/protocols/*.py`
- `praxis/backend/core/storage/`

---

## 3. Context & References

**Primary Files to Modify:**

| Path | Description |
|:-----|:------------|
| `praxis/backend/configure.py` | Backend configuration with simulation setup |
| `praxis/web-client/src/app/features/assets/components/machine-filters/machine-filters.component.ts` | Filter UI with demo references |
| `praxis/protocol/protocols/*.py` | Protocol files with demo backends |

**Reference Files (Read-Only):**

| Path | Description |
|:-----|:------------|
| `praxis/web-client/src/assets/docs/architecture/simulation.md` | Current simulation documentation |
| `praxis/backend/core/storage/` | Storage adapters (may have demo references) |

---

## 4. Constraints & Conventions

- **Commands**: Use `uv run` for Python, `npm` for Angular.
- **Backend Path**: `praxis/backend`
- **Frontend Path**: `praxis/web-client`
- **Naming**: Use "Simulated" prefix consistently (not "Demo", "Mock", "Fake")

---

## 5. Verification Plan

**Definition of Done:**

1. No remaining "demo" references (case-insensitive search):
   ```bash
   grep -ri "demo" praxis/ --include="*.py" --include="*.ts" | grep -v node_modules | grep -v ".pyc"
   ```

2. The code compiles without errors:
   ```bash
   uv run python -c "from praxis.backend import configure"
   cd praxis/web-client && npm run build
   ```

3. Tests pass:
   ```bash
   uv run pytest tests/ -x -q
   cd praxis/web-client && npm test
   ```

4. Documentation updated if simulation behavior changed

---

## On Completion

- [ ] Commit changes with descriptive message
- [ ] Update backlog item status in `simulation.md`
- [ ] Update DEVELOPMENT_MATRIX.md if applicable
- [ ] Mark this prompt complete in batch README

---

## References

- `.agents/README.md` - Environment overview
- `praxis/web-client/src/assets/docs/architecture/simulation.md` - Current simulation docs
