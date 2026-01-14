# Agent Prompt: Workcell Explorer Sidebar

Examine `.agents/README.md` for development context.

    **Status:** 🟢 Completed

    **Priority:** P2

    **Batch:** [260115](README.md)

    **Difficulty:** Medium

    **Dependencies:** K-03_workcell_dashboard.md

    **Backlog Reference:** WCX-001-IMPL (P1.2)



    ---



    ## 1. The Task



    Create the hierarchical tree component for the sidebar as defined in Phase 1.2 of the [Workcell Implementation Plan](../artifacts/workcell_implementation_plan.md). This component handles navigation and

    filtering within the workcell context.



    ## 2. Technical Implementation Strategy



    **(From workcell_implementation_plan.md)**



    **Frontend Components:**



    - Generate `src/app/shared/components/workcell/workcell-explorer/` containing:

      - `workcell-explorer.component.ts` (Container & Search)

      - `workcell-group/workcell-group.component.ts` (Collapsible section)

      - `machine-tree-node/machine-tree-node.component.ts` (List item)

    - Implement `WorkcellExplorer`:

      - Input: `WorkcellGroup[]`

      - Logic: Search filtering (filters machines, expands parent group if match found).

    - Implement `WorkcellGroup`:

      - Logic: Persist expanded state to `localStorage` (key: `workcell-expanded-${id}`).



    **Backend/Services:**



    - None directly; consumes data passed from Dashboard.



    **Data Flow:**



    1. Dashboard passes `WorkcellGroup[]` data to Explorer.

    2. User types in Search -> Explorer filters the groups/machines locally.

    3. User clicks Machine -> Explorer emits `machineSelected` event.



    ## 3. Context & References



    **Primary Files to Modify:**



    | Path | Description |

    |:-----|:------------|

    | `src/app/shared/components/workcell/workcell-explorer/` | New directory for explorer components |



    **Reference Files (Read-Only):**



    | Path | Description |

    |:-----|:------------|

    | `.agents/artifacts/workcell_ux_redesign.md` | UX Redesign (Section 2.1) |

    | `.agents/prompts/260115_dev_cycle/K-03_workcell_dashboard.md` | Parent component context |



    ## 4. Constraints & Conventions



    - **Commands**: Use `npm` for Angular.

    - **Frontend Path**: `praxis/web-client`

    - **Generics**: Use strongly typed Inputs/Outputs.

    - **Linting**: Run `eslint` or equivalent before committing.



    ## 5. Verification Plan



    **Definition of Done:**



    1. The code compiles without errors.

    2. The following tests pass:



       ```bash

       npm run test -- workcell-explorer

       ```



    3. Expanding/collapsing a group persists state after page reload.

    4. Search input correctly filters the machine list.



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
