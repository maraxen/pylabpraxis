# Status: Complete
# Phase 4 Plan: Protocol Arguments & UI Polish

**Goal**: Implement robust Protocol Arguments (Itemized Resources, Dicts) and finish UI Polish.

## Tasks

### Task 1: Tracer Fixes
- [x] Update `praxis/backend/core/tracing/executor.py`.
- [x] Ensure `list[Well]` or `Sequence[Well]` returns `TracedContainerElementCollection`.
- [x] Fix the `__iter__` issue so protocols can loop over these arguments during tracing.

### Task 2: ItemizedResourceSelection
- [x] Define the type/model in Backend.
- [x] Update `TypeAnnotationAnalyzer` to map `list[Well]` -> `field_type: "itemized-selector"`.
- [x] Update Frontend `parameter-config.component.ts` to *not* skip these, but render them.

### Task 3: Formly Widgets
- [x] Implement `DictInputComponent` (key-value repeater).
- [x] Register it in `app.config.ts`.
- [x] (Optional) Update `IndexSelectorComponent` to support general items (Tubes/Tips), not just Wells.

### Task 4: Verification
- [x] Create a test protocol `test_itemized_args.py` that takes `source: list[Well]`.
- [x] Verify it traces correctly (no iter error).
- [x] Verify Frontend renders the selector.
