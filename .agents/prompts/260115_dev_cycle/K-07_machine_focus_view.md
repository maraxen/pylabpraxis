# Agent Prompt: Machine Focus View

Examine `.agents/README.md` for development context.

  **Status:** 🟢 Completed

  **Priority:** P2

  **Batch:** [260115](README.md)

  **Difficulty:** Medium

  **Dependencies:** K-06_machine_card.md

  **Backlog Reference:** WCX-001-IMPL (P2.2)



  ---



  ## 1. The Task



  Create the detailed single-machine focus view as defined in Phase 2.2 of the [Workcell Implementation Plan](../artifacts/workcell_implementation_plan.md). This view allows deep inspection of a specific

  machine.



  ## 2. Technical Implementation Strategy



  **(From workcell_implementation_plan.md)**



  **Frontend Components:**



  - Generate `src/app/features/workcell/machine-focus-view/` with:

    - `machine-focus-view.component.ts`

    - `protocol-progress-panel.component.ts`

    - `resource-inspector-panel.component.ts`

  - Layout:

    - Header: Back button + Machine Info.

    - Body: Full-width `app-deck-view`.

    - Footer Panels: Progress + Inspector.

  - Navigation Logic:

    - Listen for "Back" click -> Signal parent to switch to Grid mode.

    - Listen for 'Escape' key -> Exit focus view.



  **Backend/Services:**



  - None.



  **Data Flow:**



  - Inputs: `MachineWithRuntime`.

  - User interacts with Deck View -> Updates Resource Inspector.



  ## 3. Context & References



  **Primary Files to Modify:**



  | Path | Description |

  |:-----|:------------|

  | `src/app/features/workcell/machine-focus-view/` | New view directory |



  **Reference Files (Read-Only):**



  | Path | Description |

  |:-----|:------------|

  | `.agents/artifacts/workcell_ux_redesign.md` | Design reference (Section 3.2) |

  | `.agents/prompts/260115_dev_cycle/K-06_machine_card.md` | Navigation source |



  ## 4. Constraints & Conventions



  - **Commands**: Use `npm` for Angular.

  - **Frontend Path**: `praxis/web-client`

  - **Linting**: Run `eslint` or equivalent before committing.



  ## 5. Verification Plan



  **Definition of Done:**



  1. The code compiles without errors.

  2. The following tests pass:



     ```bash

     npx vitest run src/app/features/workcell/machine-focus-view

     ```



  3. Clicking "Back" returns to the dashboard grid correctly.

  4. Deck view renders at full size.



  ---



  ## On Completion



  - [x] Commit changes with descriptive message referencing the backlog item

  - [x] Update backlog item status

  - [x] Update DEVELOPMENT_MATRIX.md if applicable

  - [x] Mark this prompt complete in batch README and set the status in this prompt document to 🟢 Completed

---

## References

- `.agents/README.md` - Environment overview
- `TECHNICAL_DEBT.md` - Known issues
