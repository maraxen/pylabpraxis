# Missing Deck Definitions - Implementation Plan

## Goal Description

Fix the "Missing Deck Definitions" bug where only 2 deck definitions are found in the browser mode database. The goal is to ensure all major decks (Hamilton STAR, STARLet, Vantage, etc.) are correctly discovered via static analysis and seeded into the `deck_definition_catalog` table.

## User Review Required
>
> [!NOTE]
> This change involves modifying the static analysis logic for PyLabRobot resources. It assumes that `STARDeck`, `STARLetDeck`, and `VantageDeck` factory functions are the intended "Deck Definitions" for the user.

## Proposed Changes

### Backend Utils

#### [MODIFY] [resource_factory.py](file:///Users/mar/Projects/praxis/praxis/backend/utils/plr_static_analysis/visitors/resource_factory.py)

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

#### [MODIFY] [generate_browser_db.py](file:///Users/mar/Projects/praxis/scripts/generate_browser_db.py)

**Implement Hybrid Approach**: Static analysis with manual fallback registry.

```python
# Define critical decks that must always be included
CRITICAL_DECKS = [
    {
        'name': 'STARDeck',
        'fqn': 'pylabrobot.liquid_handling.backends.hamilton.STAR.STARDeck',
        'category': 'Deck',
        'brand': 'Hamilton'
    },
    {
        'name': 'STARLetDeck',
        'fqn': 'pylabrobot.liquid_handling.backends.hamilton.STARlet.STARLetDeck',
        'category': 'Deck',
        'brand': 'Hamilton'
    },
    {
        'name': 'VantageDeck',
        'fqn': 'pylabrobot.liquid_handling.backends.hamilton.Vantage.VantageDeck',
        'category': 'Deck',
        'brand': 'Hamilton'
    },
    # Add Opentrons and Tecan as needed
]

def discover_decks_static(parser: PLRSourceParser) -> list:
    """Discover deck definitions using static analysis + manual fallback"""
    
    # Attempt static analysis
    discovered_classes = parser.discover_resource_classes()
    discovered_factories = parser.discover_resource_factories()
    
    # Filter for decks
    deck_classes = [r for r in discovered_classes if r.class_type == PLRClassType.DECK]
    deck_factories = [r for r in discovered_factories if r.class_type == PLRClassType.DECK]
    
    # Combine and deduplicate by FQN
    all_decks = {d.fqn: d for d in deck_classes + deck_factories}
    
    # Add critical decks if missing (fallback)
    for critical in CRITICAL_DECKS:
        if critical['fqn'] not in all_decks:
            logger.warning(f"Static analysis missed {critical['name']}, adding from manual registry")
            # Create a ResourceInfo object from the critical deck dict
            all_decks[critical['fqn']] = create_resource_info_from_dict(critical)
    
    return list(all_decks.values())
```

- Update `discover_decks_static` function to use this hybrid approach
- Log warnings when falling back to manual registry (indicates static analysis needs improvement)

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
