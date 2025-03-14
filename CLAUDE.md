# PyLabPraxis Development Guide

## Commands

* Python Backend: `uvicorn main:app --reload`
* Python Tests: `python -m pytest --cov=./praxis`
* Python Lint: `make lint`
* Python Type Check: `make typecheck`
* Frontend Dev: `cd frontend && npm run dev`
* Frontend Tests: `cd frontend && npm test` or `npm test -- -t "test name"` (Jest)
* Frontend Tests with Coverage: `cd frontend && npm test -- --coverage`
* Frontend Lint: `cd frontend && npm run lint`
* Frontend Build: `cd frontend && npm run build`

## Code Style

* Python: Google Style docstrings with type hints
* Python naming: snake_case for functions/variables, PascalCase for classes
* TypeScript/React: Functional components with hooks
* TypeScript naming: camelCase for functions/variables, PascalCase for components/classes/interfaces
* Frontend structure: Feature-based organization (features/shared pattern)
* Error handling: Use try/catch blocks for async operations, proper error messages
* Imports: Group by external libs, then internal project imports, alphabetically sorted
* Styling: The frontend uses Chakra UI. Custom themes and component styles are defined in `src/styles/theme.ts` and `src/shared/recipes/`.

## Git Workflow

* Feature branches from main
* Descriptive commit messages
* PR template for consistency

## Project Information

* Architecture:
  * Backend: Python (FastAPI), Uvicorn
  * Frontend: React/TypeScript
  * State Management: Redux Toolkit
  * Database: PostgreSQL
  * Cached State Management: Redis
  * Laboratory Automation: Pylabrobot
* Backend:
  * `praxis/api`: FastAPI routers for different functionalities (protocols, assets, etc.).
  * `praxis/core`: Core application logic, including workcell management and orchestration.
  * `praxis/interfaces`: Database and hardware interfaces.
* Frontend:
  * React/TypeScript: Used for building the user interface and application logic.
  * State Management: Redux Toolkit is used for managing the application's state. Redux slices are defined within feature directories (e.g., `src/features/protocols/store/slice.ts`) and the main store configuration is in `src/store/index.ts`.
  * Routing: React Router (or similar) is used for handling navigation between different pages and views. (Note: While not explicitly shown, this is a standard React practice)
  * UI Library: Chakra UI is used for building accessible and reusable UI components. Custom themes and component styles are defined in `src/styles/theme.ts` and component "recipes" are in `src/shared/recipes/`.
  * API Communication: `src/services/api.ts` uses Axios to handle communication with the backend API, including request interception and error handling.
  * Authentication: OIDC (OpenID Connect) is used for user authentication, implemented using `oidc-spa/react` in `src/oidc.ts`.
  * Form Handling: Custom hooks and components are used to manage form state and validation, particularly within feature areas like protocol configuration.
  * Component Structure: The frontend follows a feature-based structure, organizing code by functionality (e.g., protocols, lab assets, settings).  Within features, components are often further organized using atomic design principles (atoms, molecules, organisms). See `src/features/*/components`.
* Key Modules/Components:
  * Backend:
    * `praxis/api`: FastAPI routers for different functionalities (protocols, assets, etc.).
    * `praxis/core`: Core application logic, including workcell management and orchestration.
    * `praxis/interfaces`: Interfaces to allow complex interaction with data structures without circular imports.
  * Frontend:
    * `src/App.tsx`: (Implied) The main application entry point, responsible for setting up routing, authentication providers, and global styles.
    * `src/features`: Contains the main features of the application, such as:
      * `src/features/protocols`: For creating, running, and managing protocols. This includes components for parameter configuration, asset selection, and protocol execution.
      * `src/features/labAssets`: For managing laboratory equipment and resources.
      * `src/features/settings`: For user settings and preferences.
    * `src/services/api.ts`: Handles API communication, request/response logging, and error handling.
    * `src/store`: Redux store configuration and slice definitions for application state management. Redux Toolkit is used.
    * `src/oidc.ts`: Implements OIDC authentication.
    * `src/shared`: Contains reusable components, hooks, types, and styles used across the application:
      * `src/shared/components/ui`: Reusable UI components (e.g., buttons, inputs, cards).
      * `src/shared/hooks`: Custom React hooks (e.g., `useAppDispatch`, `useAppSelector` for Redux).
      * `src/shared/recipes`: Chakra UI component recipes for consistent styling.
      * `src/shared/types`: Shared TypeScript types for data structures (e.g., `Protocol`, `Asset`, `User`).
    * `src/styles`: Global styles, theming (Chakra UI theme), and custom CSS.
* Authentication: The frontend uses OIDC for authentication (see `src/oidc.ts`).
* State Management: Redux Toolkit is used for frontend state management (see `src/store/`).

## Environment Variables

* Set the API URL using the `VITE_API_URL` environment variable (e.g., `VITE_API_URL=http://localhost:8000`).

## Database

* PostgreSQL is used as the main database. See the project's `README.md` or `praxis/config` for database setup details.

## Cached State

* Redis is used for cached state management. Ensure a Redis server is running and configured correctly.

## Laboratory Automation

* The backend integrates with Pylabrobot for laboratory automation tasks.
