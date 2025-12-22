# Frontend Development Documentation

## Architecture Overview

The frontend is built using **Flutter** (targeting Web) and follows a **Feature-First + Clean Architecture** hybrid approach.

### Directory Structure (`lib/src`)

- **`core/`**: Contains shared code used across multiple features.
  - `widgets/`: Reusable UI components (Buttons, Inputs, etc.) - **DRY Principle**.
  - `theme/`: App-wide theming and styling.
  - `network/`: Dio client setup and interceptors.
  - `error/`: Failure classes and error handling logic.
- **`data/`**: Shared data layer components.
  - `repositories/`: Implementations of repositories that might be shared.
  - `models/`: DTOs and shared data models.
  - `services/`: API service definitions.
- **`features/`**: Independent functional modules of the application.
  - `auth/`: Authentication (Login, Register).
  - `assetManagement/`: Managing lab assets.
  - `protocols/`: Protocol definitions and management.
  - `run_protocol/`: Execution interface for protocols.
  - `visualizer/`: Visualization tools.
  - `settings/`, `home/`, `splash/`: Standard app features.

### Tech Stack

- **State Management**: `flutter_bloc`
- **Routing**: `go_router`
- **Networking**: `dio`
- **Dependency Injection**: `get_it` / `injectable` (implied)
- **Code Generation**: `freezed`, `json_serializable`, `build_runner`
- **Testing**: `flutter_test`, `bloc_test`, `mockito`

## Development Roadmap

### Phase 1: Audit & Environment (Current)

- [x] Audit existing structure.
- [ ] Ensure Flutter/Dart SDKs are up to date (`flutter upgrade`).
- [ ] Verify proper environment setup for all developers.

### Phase 2: Feature Implementation & Connection

- [ ] **Auth**: Connect login forms to Backend API Token endpoints.
- [ ] **Asset Management**: Implement CRUD operations against Backend.
- [ ] **Visualizer**: Port or integrate existing visualization logic (from notebooks/scripts) into Flutter Web Canvas/CustomPainter or WebGL.

### Phase 3: Testing & Polish

- [ ] **Unit Tests**: Coverage for blocs and repositories.
- [ ] **Widget Tests**: verify UI components.
- [ ] **Integration Tests**: End-to-end flows.

## Context & "Memories"

### Important Lessons

1. **Code Generation**: This project uses `freezed`. You **MUST** run the build runner after modifying models or blocs:

   ```bash
   dart run build_runner build --delete-conflicting-outputs
   ```

2. **Web Support**: We are targeting Web. Ensure imports do not rely on `dart:io` (except where conditional imports are used). Use `dart:html` or `package:web` cautiously, preferring `universal_html` if needed.
3. **State Logic**: Keep UI dumb. All logic goes into `Bloc` or `Cubit`.
4. **DRY Components**: Before building a new widget, check `core/widgets`.

### Guidelines

- Prefer `const` constructors where possible.
- Use `repository` pattern for all data access.
- Handle errors globally where possible (via Dio interceptors or global BlocListener).
