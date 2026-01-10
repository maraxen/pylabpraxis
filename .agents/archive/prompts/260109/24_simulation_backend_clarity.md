# Agent Prompt: Clarify Simulated Backend Architecture

Examine `.agents/README.md` for development context.

**Status:** 🟢 Not Started
**Priority:** P2
**Difficulty:** Medium
**Batch:** [260109](./README.md)
**Backlog Reference:** [simulation.md](../../backlog/simulation.md#p2-simulated-backend-clarity)

---

## 1. The Task

The simulated backend/frontend architecture is unclear:
- "Demo" naming persists on simulated frontends
- Unclear what each simulated backend actually does
- Unknown which frontends use ChatterboxBackend vs other approaches
- Need better frontend/backend separation documentation

**Goal:** Audit, document, and clean up the simulated backend architecture for clarity and consistency.

**User Value:** Developers and users understand what simulation provides and how it behaves.

---

## 2. Technical Implementation Strategy

**Phase 1: Investigation**

1. Audit all simulated backend implementations in PyLabRobot definitions
2. Document what each simulated frontend/backend pair provides
3. Identify which use ChatterboxBackend vs custom simulation

**Phase 2: Cleanup**

1. Remove all "Demo" naming from simulated frontends
2. Use consistent "Simulated" prefix
3. Add documentation comments in code

**Phase 3: Documentation**

1. Document simulation architecture
2. Explain what simulation provides (state tracking, timing, etc.)
3. Document per-machine-category simulation capabilities

---

## 3. Context & References

**Primary Files to Modify:**

| Path | Description |
|:-----|:------------|
| `praxis/web-client/src/assets/browser-data/plr-definitions.ts` | Browser-bundled PLR definitions |
| `external/pylabrobot/` | PyLabRobot definitions (if modifications needed) |

**Reference Files (Read-Only):**

| Path | Description |
|:-----|:------------|
| `praxis/web-client/src/app/features/assets/services/asset.service.ts` | How definitions are loaded |
| PyLabRobot source code | Actual backend implementations |

---

## 4. Constraints & Conventions

- **Commands**: Use `uv run` for Python, `npm` for Angular
- **Naming Convention**: Use "Simulated" prefix, not "Demo"
- **Documentation**: Add JSDoc/docstrings where applicable

**Investigation Commands:**

```bash
# Find "Demo" naming in definitions
grep -r "Demo" praxis/web-client/src/assets/browser-data/

# Find simulated backends
grep -r "SimulatedBackend\|ChatterboxBackend\|Simulator" praxis/

# List machine definition files
ls external/pylabrobot/pylabrobot/liquid_handling/backends/
```

**Expected Findings:**

| Machine Category | Simulated Backend | Provides |
|-----------------|-------------------|----------|
| LiquidHandler | ChatterboxBackend | State tracking, no physical ops |
| PlateReader | SimulatedBackend | Mock readings |
| HeaterShaker | SimulatedBackend | Temperature/speed tracking |

**Naming Cleanup:**

```typescript
// Before
{ name: 'DemoHamilton', ... }

// After
{ name: 'SimulatedHamilton', ... }
```

**Documentation to Add:**

Create or update `praxis/web-client/src/assets/docs/architecture/simulation.md`:

```markdown
# Simulation Architecture

## Overview

Praxis supports simulation mode for all hardware categories...

## Per-Category Simulation

### Liquid Handlers
- Uses ChatterboxBackend
- Tracks deck state, volumes, tip usage
- No physical operations

### Plate Readers
- Returns mock absorbance/fluorescence values
- Configurable response patterns

...
```

---

## 5. Verification Plan

**Definition of Done:**

1. All "Demo" naming removed from simulated frontends
2. Consistent "Simulated" prefix used
3. Documentation exists for simulation architecture
4. Each machine category's simulation behavior is documented
5. Code comments explain simulation purpose

**Verification Commands:**

```bash
# Verify no "Demo" naming remains
grep -r "Demo" praxis/web-client/src/assets/browser-data/ | wc -l
# Should return 0

cd praxis/web-client
npm run build
```

**Manual Verification:**
1. Browse machine definitions in UI
2. Verify simulated machines use "Simulated" prefix
3. Check that simulation documentation exists

---

## On Completion

- [ ] Commit changes with message: `refactor(simulation): clarify and document simulated backend architecture`
- [ ] Update backlog item status in `backlog/simulation.md`
- [ ] Update `DEVELOPMENT_MATRIX.md` if applicable
- [ ] Mark this prompt complete in batch README and set status to 🟢 Completed

---

## References

- `.agents/README.md` - Development context and agent workflow
- `backlog/simulation.md` - Full simulation issue tracking
