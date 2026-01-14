# Protocol Execution UX Improvements

This plan addresses several UX issues in the "Run Protocol" flow, focusing on well selection, asset configuration, and protocol information display.

## User Review Required

> [!IMPORTANT]
> **Asset Persistence**: The fix involves modifying `GuidedSetupComponent` to accept initial selections. This changes the initialization flow in that component and requires testing to ensure no regression in the auto-assignment logic.

## Technical Debt Context

> [!NOTE]
> **Selective Transfer Detection**: We are maintaining the current string-matching heuristic for detecting "Selective Transfer" protocols (`name` or `fqn` includes 'selective_transfer') as per existing code. This logic will be an enhancement to the existing heuristic to enforce well count equality.
>
> **Gap Logic**: This heuristic is a temporary bridge. Future work must replace this with a formal protocol capability definition or metadata flag in the backend ProtocolDefinition model to explicitly declare "Source/Target Linkage" requirements, removing reliance on string parsing. This requirement is documented in `TECHNICAL_DEBT.md`.

## Proposed Changes

### 1. Well Arguments Solution

**Goal**: Ensure well selection parameters ONLY appear in the "Select Wells" step, not in "Configure Parameters".

#### [MODIFY] [parameter-config.component.ts](file:///Users/mar/Projects/pylabpraxis/praxis/web-client/src/app/features/run-protocol/components/parameter-config/parameter-config.component.ts)

- Refine `isWellParameter` to be more robust.
- Add check for `field_type === 'well_selection'` in addition to name patterns and UI hints.
- Ensure strict filtering so users don't see duplicate inputs.

### 2. Asset Autocomplete Redesign

**Goal**: Persist asset selections when navigating between steps and improve the selection UX.

#### [MODIFY] [guided-setup.component.ts](file:///Users/mar/Projects/pylabpraxis/praxis/web-client/src/app/features/run-protocol/components/guided-setup/guided-setup.component.ts)

- Add `@Input() initialSelections: Record<string, Resource>` to support restoring state.
- Update `ngOnInit` to use `initialSelections` if provided, instead of running `autoSelect` from scratch.
- Ensure `autoSelect` respects existing selections if partial state is provided.

#### [MODIFY] [run-protocol.component.ts](file:///Users/mar/Projects/pylabpraxis/praxis/web-client/src/app/features/run-protocol/run-protocol.component.ts)

- Pass `configuredAssets()` as `[initialSelections]` to `app-guided-setup` in the template.

### 3. Index Linking Design

**Goal**: Enforce equal number of selected wells for source and destination in selective transfers, and provide live feedback.

#### [MODIFY] [run-protocol.component.ts](file:///Users/mar/Projects/pylabpraxis/praxis/web-client/src/app/features/run-protocol/run-protocol.component.ts)

- Update `areWellSelectionsValid` to check for count equality if `isSelectiveTransferProtocol()` is true.
- Add a computed signal or method `getWellSelectionWarning()` to return a validation message (e.g., "Source and Target well counts must match").
- Update template:
  - Display the live count of selected wells next to each button (e.g., `(4 selected)`).
  - Show an error alert if counts mismatch and validation fails.

### 4. Protocol Summary Formatting

**Goal**: Improve the "Select Protocol" step by organizing information into tabs.

#### [MODIFY] [run-protocol.component.ts](file:///Users/mar/Projects/pylabpraxis/praxis/web-client/src/app/features/run-protocol/run-protocol.component.ts)

- Import `MatTabsModule`.
- Refactor the protocol details card (Step 1) to use `<mat-tab-group>`.
- Create tabs:
  - **Description**: Existing description text.
  - **Required Assets**: List required assets (read-only view).
  - **Parameters**: List configurable parameters (read-only preview).
- Remove the scrollable `description-container` in favor of the tabbed view.

### 5. Guided Deck Setup

**Goal**: Ensure deck starts empty for guided setup.

#### [MODIFY] [run-protocol.component.ts](file:///Users/mar/Projects/pylabpraxis/praxis/web-client/src/app/features/run-protocol/run-protocol.component.ts)

- Ensure `deckGenerator.generateDeckForProtocol` is called with correct initial state.
- (Verification only: ensure logic pulls fresh state or starts empty as requested).

## Verification Plan

### Manual Verification

1. **Test Asset Persistence**:
    - Select a protocol.
    - Go to "Select Assets", select an item manually.
    - Go to "Configure Parameters" (Back/Next).
    - Return to "Select Assets". Verify the manual selection persists.
2. **Test Well Selection Exclusion**:
    - Select a protocol with well parameters (e.g., "Selective Transfer").
    - Go to "Configure Parameters". Verify NO well selection inputs appear.
3. **Test Index Linking**:
    - Select "Selective Transfer" protocol.
    - Go to "Select Wells".
    - Select 3 wells for Source. Verify validation fails (Next disabled, warning shown).
    - Select 4 wells for Target. Verify validation fails.
    - Fix Target to 3 wells. Verify validation passes.
4. **Test Protocol Summary**:
    - View "Select Protocol" step.
    - Verify Tabs appear (Description | Assets | Parameters).
    - Click through tabs and verify content.
