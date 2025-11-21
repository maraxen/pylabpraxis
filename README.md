# PyLabPraxis

[**Docs**](https://docs.pylabrobot.org) | [**Forum**](https://forums.pylabrobot.org) | [**Installation**](https://docs.pylabrobot.org/installation.html) | [**Getting started**](https://docs.pylabrobot.org/basic.html)

## What is PyLabPraxis?

PyLabPraxis is a comprehensive Python-based platform designed to automate and manage laboratory workflows. It leverages the [PyLabRobot](https://pylabrobot.org/) library to interface with a wide range of lab automation hardware. PyLabPraxis provides a robust backend system built with FastAPI, enabling protocol execution, asset management, real-time hardware control, and persistent state management.

Developed for the Ovchinnikov group in MIT Biology.

## Architecture Overview

PyLabPraxis employs a modular, service-oriented architecture.

```mermaid
graph TD
    A[User/API Client] --> B(API Layer - FastAPI);
    B --> C{Orchestrator};
    C --> D(Protocol Engine);
    C --> E(Scheduler - Celery & Redis);
    E --> F(Task Executor - Celery Worker);
    F --> G(WorkcellRuntime);
    G --> H1(Device Drivers/Simulators);
    G --> H2(Asset Manager);
    D --> I(In-Memory State Objects);
    I --> J(Database - PostgreSQL);
    C --> I;
    G --> I;
    B --> J;
    C --> N(PraxisState - Redis);
    F --> N;
```

For a detailed breakdown of components, services, and workflows, please refer to the [System Architecture](docs/architecture.md) documentation.

## Key Features

*   **FastAPI Backend**: RESTful API for protocol management and execution.
*   **PyLabRobot Integration**: Hardware control for liquid handlers, plate readers, and more.
*   **Robust State Management**: Distributed state tracking using PostgreSQL, Redis (`PraxisState`), and in-memory objects.
*   **Asynchronous Execution**: Celery-based task queue for scheduling and running protocols.
*   **Asset Management**: Comprehensive tracking of labware, machines, and their real-time status.

## Documentation

*   **[System Architecture](docs/architecture.md)**: Deep dive into components, data flow, and services.
*   **[State Management](docs/state_management.md)**: Explanation of how state is persisted and shared across the system.
*   **[Testing Strategy](docs/testing.md)**: Guide to testing patterns, tools, and best practices.
*   **[Installation](docs/installation.md)**: Setup instructions.

## Asset Model Refactor (2025-06)

The asset-related backend models have been **unified and modernized**. All asset types (machines, resources, decks, workcells) now inherit from a single `Asset` base model.

*   **Unified Fields**: `accession_id`, `name`, `fqn`, `asset_type`, `location`, `plr_state`, `plr_definition`, `properties_json`.
*   **Legacy Fields Removed**: Code should be updated to use the new standardized fields.

## Development

PyLabPraxis uses standard Python development tools managed by `uv`.

*   **Test**: `uv run pytest`
*   **Lint**: `uv run ruff check .`
*   **Typecheck**: `uv run pyright`

See [CONTRIBUTING.md](CONTRIBUTING.md) and [AGENTS.md](AGENTS.md) for more details.

---

**Disclaimer:** PyLabPraxis is not officially endorsed or supported by any robot manufacturer. Usage of firmware drivers is at your own risk.
