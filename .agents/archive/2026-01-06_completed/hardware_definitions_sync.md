# Technical Debt: Dynamic Hardware Definitions (VID/PID)

## Context

Currently, the frontend `HardwareDiscoveryService` relies on a hardcoded `KNOWN_DEVICES` map to identify supported USB/Serial devices (VID/PID) and map them to PLR backend classes. This is brittle and duplicates information that should ideally reside within the PyLabRobot (PLR) library or be inspected from it.

The user has requested that we generate this list dynamically by inspecting the PLR backend classes.

## Requirements

### 1. Backend Metadata Inspection

- [ ] **Enhance Type Definition Services**: Update `ResourceTypeDefinitionService` / `MachineTypeDefinitionService` (or the underlying inspection utility) to extract:
  - `USB_VENDOR_ID` / `USB_PRODUCT_ID` constants (if they exist on the Backend class).
  - Or add a method/property to our own wrappers (if we wrap them) to expose this.
  - *Challenge*: PLR backends might not standardise where they store VIDs/PIDs. We might need to contribute this to PLR or maintain a mapping in our Python layer, but centrally.

### 2. Frontend Schema Generation

- [ ] **Expose via API**: The Backend should serve a JSON endpoint (e.g., `/api/hardware/definitions`) listing all supported machines and their USB identifiers.
- [ ] **Frontend Consumption**:
  - `HardwareDiscoveryService` should fetch this list on startup.
  - `navigator.serial.requestPort({ filters })` should use this dynamic list.

### 3. Benefits

- Single source of truth (Python/PLR code).
- Easier to add new device support (just add the backend class).
- Removes magic hex numbers from TypeScript.
