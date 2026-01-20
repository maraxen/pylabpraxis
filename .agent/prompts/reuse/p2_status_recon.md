# Flash Agent Recon Prompts — P2 Status Check

These prompts are for dispatching to flash agents to inspect and report on the status of P2 items. **These are recon tasks only — do not implement or fix anything.**

---

## 1. State Inspection Backend

```markdown
# Recon: State Inspection Backend Status

**Objective**: Determine the implementation status of "State Inspection Backend" (post-run time travel for backend executions).

## Task
1. Check `.agent/tasks/260115_feature_enhancements/state_inspection_backend/` for README and any artifacts
2. Search for `state_inspection`, `time_travel`, `state_history` in:
   - `praxis/backend/`
   - `praxis/web-client/src/app/`
3. Check if `WorkcellRuntime` or `ExecutionMixin` has state capture logic
4. Look for state diffing/replay logic in frontend services

## Output
Return a status report:
- **Status**: ✅ Complete | 🔄 In Progress | ❌ Not Started
- **Evidence**: List of key files/functions implemented
- **Gaps**: What remains to be done (if any)
- **Blockers**: Any identified blockers

**IMPORTANT**: Do NOT implement anything. Report findings only.
```

---

## 2. Simulation Machine Visibility

```markdown
# Recon: Simulation Machine Visibility Status

**Objective**: Determine the implementation status of "Simulation Machine Visibility" (frontend-only sim until instantiation).

## Task
1. Check `.agent/tasks/260115_feature_enhancements/sim_machines_visibility/` for README
2. Search for `is_simulation_override`, `simulated`, `SimulatedBackend` in:
   - `praxis/web-client/src/app/features/`
   - `praxis/web-client/src/app/core/services/`
3. Check `HardwareDiscoveryDialogComponent` for simulation filtering
4. Check `AssetService` or `MachineRepository` for simulation-aware queries

## Output
Return a status report:
- **Status**: ✅ Complete | 🔄 In Progress | ❌ Not Started
- **Evidence**: List of key files/functions implemented
- **Gaps**: What remains to be done (if any)

**IMPORTANT**: Do NOT implement anything. Report findings only.
```

---

## 3. Hardware Validation (STARlet + Plate Reader)

```markdown
# Recon: Hardware Validation Status

**Objective**: Determine the validation status of real hardware connectivity (Hamilton STARlet, Plate Reader).

## Task
1. Check `.agent/backlog/hardware.md` for current tracking
2. Search for `WebSerial`, `WebUSB`, `HamiltonSTARlet`, `PlateReader` in:
   - `praxis/web-client/src/app/`
   - `praxis/backend/`
3. Check if E2E tests exist for hardware workflows
4. Look for any hardware validation logs or notes in `.agent/tasks/`

## Output
Return a status report:
- **Status**: ✅ Validated | 🔄 Partially Tested | ❌ Not Validated
- **Evidence**: Test files, logs, or implementation code found
- **Hardware Tested**: Which hardware has been tested
- **Gaps**: What hardware/workflows remain untested

**IMPORTANT**: Do NOT implement anything. Report findings only.
```

---

## 4. Frontend Protocol Execution

```markdown
# Recon: Frontend Protocol Execution Status

**Objective**: Determine the implementation status of full protocol execution from browser UI.

## Task
1. Check `.agent/backlog/hardware.md` for "Frontend Protocol Execution" item
2. Inspect `praxis/web-client/src/app/features/run-protocol/` for:
   - `ExecutionService`
   - Pyodide worker integration
   - State tracking during execution
3. Check if pause/resume/cancel flows are implemented
4. Look for E2E tests covering protocol execution

## Output
Return a status report:
- **Status**: ✅ Complete | 🔄 In Progress | ❌ Not Started
- **Evidence**: Key files and functions found
- **Flows Implemented**: (Execute, Pause, Resume, Cancel)
- **Gaps**: What remains

**IMPORTANT**: Do NOT implement anything. Report findings only.
```
