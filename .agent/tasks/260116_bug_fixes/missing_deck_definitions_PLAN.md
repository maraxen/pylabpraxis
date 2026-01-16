# Missing Deck Definitions - Implementation Plan

## Goal Description

Fix the "Missing Deck Definitions" bug where only 2 deck definitions are found in the browser mode database. The goal is to ensure all major decks (Hamilton STAR, STARLet, Vantage, etc.) are correctly discovered via static analysis and seeded into the `deck_definition_catalog` table.

## User Review Required
>
> [!NOTE]
> This change involves modifying the static analysis logic for PyLabRobot resources. It assumes that `STARDeck`, `STARLetDeck`, and `VantageDeck` factory functions are the intended "Deck Definitions" for the user.

## Proposed Changes

### Backend Utils

#### [MODIFY] [resource_factory.py](file:///Users/mar/Projects/pylabpraxis/praxis/backend/utils/plr_static_analysis/visitors/resource_factory.py)

- Update `RESOURCE_RETURN_TYPES` to include:
  - `HamiltonSTARDeck`
  - `VantageDeck`
  - `Deck`
  - `HamiltonDeck`
- Update `RETURN_TYPE_TO_CATEGORY` to map these types to `"Deck"`.
- Update `visit_FunctionDef` method to dynamically assign `class_type`.
  - Instead of hardcoding `PLRClassType.RESOURCE`, check if `category == "Deck"`.
  - If so, set `class_type = PLRClassType.DECK`.
  - (Optional) Also handle `PLRClassType.CARRIER` if helpful, but focus is Deck.

### Scripts

#### [MODIFY] [generate_browser_db.py](file:///Users/mar/Projects/pylabpraxis/scripts/generate_browser_db.py)

- Update `discover_decks_static` function:
  - Call `parser.discover_resource_factories()` in addition to `parser.discover_resource_classes()`.
  - Filter the discovered factories for `class_type == PLRClassType.DECK`.
  - Combine both lists (classes and factories) before iterating and inserting.

## Verification Plan

### Automated Tests

1. **Run generation script**:

    ```bash
    uv run scripts/generate_browser_db.py
    ```

    - Observe output log: `[generate_browser_db] Inserted X deck definitions`.
    - Verify X is > 2 (expecting ~5-10).

2. **Verify Database Content**:

    ```bash
    sqlite3 praxis/web-client/src/assets/db/praxis.db "SELECT name, fqn FROM deck_definition_catalog;"
    ```

    - Check for `STARLetDeck`, `STARDeck`, `VantageDeck`.

### Unit Test (Optional but recommended)

- Run `tests/utils/test_plr_static_analysis.py` if relevant to ensure no regression in general discovery.

### Manual Verification

- N/A (The DB generation log is sufficient proof).
