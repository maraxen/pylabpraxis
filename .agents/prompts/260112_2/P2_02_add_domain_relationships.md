# Agent Prompt: Add Missing Domain Relationships (P2_02)

Examine `.agents/README.md` for development context.

**Status:** 🟢 Not Started
**Priority:** P2
**Batch:** [260112_2](./README.md)
**Backlog Reference:** [sqlmodel_codegen_refactor.md](../../backlog/sqlmodel_codegen_refactor.md) (Phase 7.1)
**Prerequisites:** [P2_01_audit_all_domain_relationships.md](P2_01_audit_all_domain_relationships.md) (Completed)

---

## 1. The Task

Implement the missing `Relationship()` fields identified in `AUDIT_REPORT.md` across the domain model layer. This acts on the findings of the audit to ensure full ORM navigation capabilities.

**User Value**: Fixes broken relationship navigation that causes test failures and runtime errors. Enables `joinedload` performance optimizations.

**Scope**:

- `praxis/backend/models/domain/machine.py`
- `praxis/backend/models/domain/resource.py`
- `praxis/backend/models/domain/schedule.py`
- `praxis/backend/models/domain/outputs.py`
- `praxis/backend/models/domain/resolution.py`

**Out of Scope**:

- `protocol.py` (Handled in P1_01)
- Test fixes (Handled in P3_01)

---

## 2. Technical Implementation Strategy

**Reference Pattern**:
Use the pattern established in `deck.py`.

```python
# 1. Foreign Key
some_id: uuid.UUID = Field(foreign_key="other_table.accession_id")

# 2. Relationship
other: Optional["OtherModel"] = Relationship(
    sa_relationship=relationship("OtherModel", back_populates="these_models")
)
```

**Implementation Steps**:

1. **Read audit report**: `.agents/prompts/260112_2/AUDIT_REPORT.md`
2. **For each file listed**:
    - Add missing `TYPE_CHECKING` imports.
    - Add `Relationship` fields to match every FK identified in the report.
    - Ensure `back_populates` is added to the *target* model as well if bidirectional navigation is needed (usually yes).
    - If `back_populates` already exists on target, match it. If not, add it to target too.

**Specific Tasks**:

- **Machine.py**: Connect `Machine` to `Resource`, `Deck`, `ProtocolRun`. Connect `MachineDefinition` to `ResourceDefinition`, `DeckDefinition`, `AssetRequirement`.
- **Resource.py**: Connect `ResourceDefinition` to `DeckDefinition`. Connect `Resource` to `ProtocolRun`.
- **Schedule.py**: Connect `ScheduleEntry` to `ProtocolRun`. Connect `AssetReservation` to `ScheduleEntry`, `ProtocolRun`.
- **Outputs.py**: Connect `FunctionDataOutput` to `FunctionCallLog`, `ProtocolRun`, `Machine`, `Resource`, `Deck`. Connect `WellDataOutput` to `FunctionDataOutput`, `Resource`.
- **Resolution.py**: Connect `StateResolutionLog` to `ScheduleEntry`, `ProtocolRun`.

---

## 3. Verification Plan

Since P3_01 deals with fixing the tests, the goal here is to ensure the *models* are correct so P3 can succeed.

**Verification command**:
Run `pytest` with collection only on affected files to ensure no syntax errors or circular import crashes.

```bash
uv run pytest tests/models/test_domain/ --collect-only --quiet
```

**Definition of Done**:

1. All missing relationships listed in `AUDIT_REPORT.md` are implemented.
2. Code parses successfully (no `ImportError` or `NameError`).
3. No `sqlalchemy.exc.InvalidRequestError` during model initialization (verified by collect-only).
