# Task: Hardware Discovery Menu Restoration (P2)

## Context

The hardware discovery menu needs restoration and UX improvements:
1. All discovery triggers should use USB icon (not magnifying glass)
2. Discovery menu should be accessible from multiple locations
3. Simulator backend should NOT appear in discovery results (always available separately)

## Backlog Reference

See: `.agents/backlog/hardware_discovery_menu.md`

## Scope

### Phase 1: Icon Audit & Replacement

Find ALL hardware discovery trigger buttons and change icons from magnifying glass to USB.

**Locations to check:**
- Asset Management toolbar
- REPL sidebar
- Run Protocol wizard (machine selection)
- Command Palette
- Home page quick actions
- `HardwareDiscoveryButtonComponent`

**Icon to use:** Material Symbol `usb` or `cable`

### Phase 2: Verify Discovery Menu Functionality

Ensure the discovery dialog:
- Opens on button click
- Shows scanning animation
- Lists discovered devices
- Allows adding devices
- Has refresh button

### Phase 3: Exclude Simulator Backend

- Filter out simulator backends from discovery results
- Simulator should be always-available in machine selection (separate section)
- Identification: `backend.type.includes('Simulator')` or `backend.simulator === true`

### Phase 4: Quick Access Points

Ensure discovery is accessible from:
- Asset Management: Toolbar button
- Command Palette: "Discover Hardware" command
- REPL: Sidebar action

## Files to Modify

- `praxis/web-client/src/app/shared/components/hardware-discovery-button/`
- `praxis/web-client/src/app/features/assets/assets.component.ts`
- `praxis/web-client/src/app/features/repl/repl.component.ts`
- `praxis/web-client/src/app/features/run-protocol/components/machine-selection/`
- `praxis/web-client/src/app/shared/components/command-palette/`

## Expected Outcome

- All discovery triggers use USB icon consistently
- Discovery menu works from all entry points
- Simulator never appears in discovery results
- Simulator always available in machine selection
