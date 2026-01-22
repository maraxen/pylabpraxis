# Simulation Architecture

## Overview

Praxis supports a robust simulation mode for all hardware categories, allowing users to develop and test protocols without physical hardware. This simulation layer is built on top of PyLabRobot's backend architecture.

## Per-Category Simulation

Each hardware category uses a specific backend implementation to provide simulation capabilities.

### Liquid Handlers
- **Backend:** `SimulatorBackend` (`pylabrobot.liquid_handling.backends.simulation.SimulatorBackend`)
- **Capabilities:**
  - Tracks deck state (tip availability, liquid volumes, resource positions).
  - Logs all commands (aspirate, dispense, move) without performing physical operations.
  - **Visualizer:** Supports real-time rendering of the deck state in the frontend.
- **Behavior:** Returns successful responses for all valid operations immediately.

### Plate Readers
- **Backend:** `SimulatedPlateReader` (wraps `PlateReaderChatterboxBackend`)
- **Capabilities:**
  - Returns mock absorbance, fluorescence, or luminescence values.
  - Configurable response patterns (e.g., random noise, gradients).
- **Behavior:** Simulates the time taken for reading plates if configured.

### Heater Shakers
- **Backend:** `SimulatedHeaterShaker` (wraps `HeaterShakerChatterboxBackend`)
- **Capabilities:**
  - Tracks temperature and shaking speed setpoints.
  - Simulates temperature ramp-up/ramp-down times.
- **Behavior:** Reports "current" temperature approaching "target" temperature over time.

## Architecture Details

The simulation architecture relies on the Dependency Injection of simulation backends during the `Machine` or `Resource` initialization.

1. **Frontend Definitions:** Machines defined with `backend: 'simulation'` in `machines.ts` or `plr-definitions.ts` signal the system to instantiate the appropriate simulation backend.
2. **Backend Instantiation:** When a protocol is run against a simulated machine, the Praxis backend (or browser-side Pyodide environment) imports the corresponding class:
   - `LiquidHandler` is initialized with `SimulatorBackend`.
   - Other devices use their respective `Simulated` variants.
3. **State Tracking:** The simulation backends maintain an in-memory state of the deck (resources, volumes) which allows for valid logic verification (e.g., checking if there is enough liquid) even without physical sensors.

## Usage

Simulation is used in:
- **Browser Mode:** Where the entire Python environment runs in the browser via Pyodide.
- **Hybrid Mode:** Where the Praxis backend runs locally but connects to simulated hardware for development/testing.
- **CI/CD:** For automated testing of protocols.
