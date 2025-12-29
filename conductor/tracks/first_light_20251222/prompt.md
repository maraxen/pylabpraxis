# Prompt for Track A Agent: E2E Protocol Execution

## 🎯 Your Mission

You are implementing **Operation "First Light"** – enabling end-to-end protocol execution in PyLabPraxis. Your goal is for a user to successfully run `simple_transfer.py` from the Protocol Wizard.

---

## 📚 Required Reading

Before starting, read these documents in order:

1. **`.agents/TRACK_A_PLAN.md`** – Your detailed implementation plan
2. **`GEMINI.md`** – Project conventions and architecture
3. **`.agents/HANDOFF.md`** – Latest handoff notes
4. **`praxis/protocol/protocols/simple_transfer.py`** – The target protocol

---

## 🚀 Getting Started

### 1. Start Services

```bash
# Terminal 1: Database
make db-test

# Terminal 2: Backend
PRAXIS_DB_DSN="postgresql+asyncpg://test_user:test_password@localhost:5433/test_db" \
  uv run uvicorn main:app --reload --port 8000

# Terminal 3: Frontend
cd praxis/web-client && npm start
```

### 2. Sync Definitions

```bash
curl -X POST http://localhost:8000/api/v1/discovery/sync-all
```

---

## 📋 Your Tasks (In Order)

### Phase A.1: Minimum Viable Resource Binding

The `asset-selector` Formly type needs to:

1. Accept a `plrTypeFilter` option to filter by PLR type
2. Allow launching `ResourceDialogComponent` to browse definitions
3. Return the asset's `accession_id` as the form value

**Key Files**:

- `praxis/web-client/src/app/shared/formly-types/asset-selector.component.ts`
- `praxis/web-client/src/app/features/run-protocol/components/parameter-config/parameter-config.component.ts`

### Phase A.2: Backend Asset Resolution

Verify the backend can resolve asset IDs during execution:

- Check `_prepare_arguments` in `execution.py`
- Check `AssetManager` can acquire resources by ID

### Phase A.3: Execution Flow Integration

Wire up `RunProtocolComponent.startRun()` to:

- Collect asset bindings from the form
- Add a "Simulation Mode" toggle (default: ON)
- Pass everything to `ExecutionService.startRun()`

### Phase A.4: Verification

Manually verify the complete flow:

1. Select protocol → Configure with real assets → Start execution
2. Confirm logs stream via WebSocket
3. Confirm status reaches COMPLETED

---

## ⚠️ Constraints

- **NO AI/LLM code** – All filtering must be deterministic
- **Simulation mode first** – Don't worry about real hardware
- **Reuse existing components** – ResourceDialogComponent already works

---

## ✅ Definition of Done

- [ ] User can select resources for `source_plate`, `dest_plate`, `tip_rack`
- [ ] "Start Execution" triggers backend execution (simulation mode)
- [ ] Logs appear in real-time
- [ ] Run completes successfully with status COMPLETED
