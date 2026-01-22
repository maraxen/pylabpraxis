# Architecture Overview

Source: praxis/backend/core/protocols/orchestrator.py

Praxis is designed as a modular, service-oriented system for laboratory automation. This document provides a comprehensive overview of the architecture, components, and data flow.

## System Diagram

### Browser Mode (Pyodide)

In Browser Mode, Praxis runs entirely within the browser using Pyodide (WebAssembly Python). There is no backend server.

```mermaid
graph TD
    subgraph Frontend_Browser ["Frontend (Browser Only)"]
        UI_B[Web UI]
        Store_B[NgRx Store]
        IO_Shim[IO Shim Service]
    end
    style Frontend_Browser fill:transparent,stroke:var(--mat-sys-primary),stroke-width:2px,color:var(--mat-sys-on-surface)

    subgraph WebWorker ["Web Worker (Pyodide)"]
        PyBridge[Python Bridge]
        Core_B[Core Engine]
        PLR_B[PyLabRobot]
    end
    style WebWorker fill:transparent,stroke:var(--mat-sys-secondary),stroke-width:2px,color:var(--mat-sys-on-surface)

    subgraph BrowserData ["Browser Storage"]
        IDB[(IndexedDB)]
        LocalStorage[(LocalStorage)]
    end
    style BrowserData fill:transparent,stroke:var(--mat-sys-primary),stroke-width:2px,color:var(--mat-sys-on-surface)

    subgraph Hardware ["Physical Hardware"]
        USB[WebSerial / USB]
        Bluetooth[WebBluetooth]
    end
    style Hardware fill:transparent,stroke:var(--mat-sys-secondary),stroke-width:2px,color:var(--mat-sys-on-surface)

    UI_B --> Store_B
    Store_B --> PyBridge
    PyBridge --> Core_B
    Core_B --> PLR_B
    
    PLR_B --> IO_Shim
    IO_Shim --> USB
    IO_Shim --> Bluetooth
    
    Store_B --> IDB
    Store_B --> LocalStorage
```

## Layer Responsibilities

### Frontend Layer

| Component | Responsibility |
|-----------|----------------|
| **Web UI** | Angular 19+ application with Material Design components |
| **NgRx Store** | Centralized state management with signal-based reactivity |
| **Frontend Services** | HTTP clients, WebSocket handlers, local storage |
| **IO Shim** | Bridges PyLabRobot hardware calls to Web APIs |

### Web Worker (Pyodide)

| Component | Responsibility |
|-----------|----------------|
| **Python Bridge** | Translates JS messages to Python function calls |
| **Core Engine** | Runs the same Orchestrator/AssetManager logic as Production |
| **PyLabRobot** | Standard PLR library running in WASM |

### Browser Storage

| Component | Responsibility |
|-----------|----------------|
| **IndexedDB** | Persistent storage for protocols and history (via SQLite Wasm) |
| **LocalStorage** | User preferences and session state |

## Key Design Principles

### 1. Code Reusability

The **Core Engine** and **PyLabRobot** logic is identical between Production and Browser modes. Only the I/O layer differs.

### 2. Zero-Install

Browser Mode requires no local installation, Docker, or Python environment. It runs entirely in the user's browser.

### 3. Direct Hardware Access

Unlike Production mode where the server controls hardware, Browser Mode uses WebSerial and WebBluetooth to connect directly from the browser tab to the robot.

## Component Deep Dives

For detailed documentation on each component:

- [Backend Components](backend.md) - Orchestrator, Services, Models (adapted for Pyodide)
- [Frontend Components](frontend.md) - Angular architecture, Store, Services
- [State Management](state-management.md) - How state flows through the system
- [Execution Flow](execution-flow.md) - Protocol execution lifecycle

## Technology Stack

### Runtime

| Technology | Purpose |
|------------|---------|
| Pyodide | Python 3.11+ in WebAssembly |
| Web Workers | Off-main-thread execution |
| SQLite Wasm | In-browser SQL database |

### Hardware Interfaces

| Technology | Purpose |
|------------|---------|
| WebSerial API | Serial/USB communication |
| WebBluetooth API | Bluetooth Low Energy communication |
