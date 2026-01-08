# Technical Debt: Plate Reader Only Protocols

## Context

Currently, PyLabPraxis is heavily centered around Liquid Handlers (Hamilton STAR, etc.) as the primary device. However, many checks and workflows only require a Plate Reader (e.g., absorbance scans) without any pipetting.

The user has identified a need to support "LH-less" protocols where the deck might only contain a plate reader, or the protocol consists solely of measurement commands.

## Requirements

### 1. Handler-less Protocol Support

- [ ] **Architecture Support**: Ensure `run_protocol` and `ExecutionManager` do not crash or block if no LiquidHandler backend is initialized.
- [ ] **Deck Visualization**: Handle "null" decks or create a "Bench" deck for standalone devices.
- [ ] **Asset Management**: Allow protocols to declare *only* a Plate Reader requirement, bypassing `layout.json` requirements if no deck interaction occurs.

### 2. Example Protocol

- [ ] **Create `examples/plate_reader_only.py`**: A vanilla Python protocol using PLR that:
  - Initialises a Plate Reader backend (e.g., CLARIOstar).
  - Sets parameters (wavelength, temperature).
  - Performs a read.
  - Exports results.
- [ ] **Praxis Integration**: Ensure this protocol can be uploaded and parsed by the Praxis backend.

### 3. Connection & Drivers

- [ ] **Browser Support**: Verify `CLARIOstar` (FTDI-based) connectivity via WebSerial.
  - *Note:* macOS FTDI drivers (VCP vs D2XX) often conflict. WebSerial might require the VCP driver to be unloaded or loaded depending on implementation.

## Priority

**Medium/High** - Enables testing and usage of the system even when the main robot is unavailable (e.g., hardware issues, being used by others).
