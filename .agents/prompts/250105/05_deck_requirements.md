# Prompt 5: Deck Setup Requirements Surface

Surface inferred requirements in the Deck Setup wizard step.

## Context

Backend caches inferred_requirements_json with deck placement, tip requirements, liquid state needs.

## Tasks

1. Create `RequirementIndicatorComponent` with states: ✅ met, ⚠️ warning, 🔴 not met

2. In Deck Setup step, display list of requirements from simulation data

3. For each requirement, validate against current deck configuration:
   - "on_deck" requirements: check if resource is placed
   - "has_liquid" requirements: check if source wells have volume
   - "tips_available" requirements: check tip rack availability

4. Highlight deck slots with issues visually

5. Block "Next" button if critical requirements unmet

## Files to Create

- `praxis/web-client/src/app/features/run-protocol/components/requirement-indicator/`

## Files to Modify

- `praxis/web-client/src/app/features/run-protocol/components/deck-setup-wizard/`

## Reference

- `.agents/backlog/simulation_ui_integration.md` (Phase 8.3)
