# Frontend Development Plan (Refined)

**Goal**: Production-ready Angular v21 interface for PyLabPraxis.
**Reference**: See `FRONTEND_UI_GUIDE.md` for strict UI/UX specifications.
**Last Updated**: 2025-12-20

---

## Phase 1: Foundation & Infrastructure (Completed)
- [x] **Project Setup**: Angular v21, Material 3.
- [x] **Core State**: NgRx Signals `AppStore`.
- [x] **Auth**: Guards, Interceptors, Login flow.
- [x] **Services**: `AssetService`, `ProtocolService`, `ExecutionService`.
- [x] **Unit Tests**: Coverage for Core & Services (Vitest).
- [x] **Removed Deprecated Flutter Frontend**: `praxis/frontend` deleted.

---

## Phase 2: Feature Components (Completed)

### 2.1 Shared UI & Forms Engine
- [x] **Install & Configure Formly**:
    -   `@ngx-formly/core`, `@ngx-formly/material`.
    -   Register custom types in `app.config.ts`.
- [x] **Global Status Bar**:
    -   Implement `StatusBarComponent` in `MainLayout`.
    -   Connect to `ExecutionService.isConnected` and `ExecutionService.status`.

### 2.2 Asset Management (CRUD)
- [x] **Asset List Views**:
    -   `MachineListComponent`: `MatTable` with status badges.
    -   `ResourceListComponent`: `MatTable` with nested/tree view potential.
- [x] **Asset Definitions Tab**:
    -   `DefinitionsListComponent`: Read-only view of `MachineDefinition` / `ResourceDefinition`.

### 2.3 Protocol Workflow (The Core)
- [x] **Protocol Library**: List view with upload button.
- [x] **Protocol Detail**: View metadata.
- [x] **Run Protocol Wizard**:
    -   **Step 1: Selection**: Pick protocol.
    -   **Step 2: Parameters**: **Formly** dynamic form rendering based on Python types.
    -   **Step 3: Deck Config**: Placeholder for SVG visualizer.
    -   **Step 4: Execution**: Live log stream, progress bar.

---

## Phase 3: Visualization & Polish (Completed)
- [x] **Formly Custom Types**:
    -   Implement `asset-selector` (Autocomplete).
    -   Implement `chips` (Boolean/Enum multi-select).
    -   Implement `repeat` (Array input).
- [x] **Deck Visualizer**:
    -   Implement SVG rendering of deck slots.
    -   Integrate PLR visualization data.
- [x] **Refactor: Path Aliases**: Implement TypeScript path aliases (`@core`, `@features`, etc.).
- [x] **UX Refinement**:
    -   Responsive adjustments.
    -   Loading states (skeletons).
    -   Error handling (Global Status Bar integration).

---

## Phase 4: UI/UX Overhaul (In Progress - Dec 2025)

### 4.1 Core Fixes (Completed)
- [x] **Remove Angular Boilerplate**: Removed default `app.html` template that was blocking content.
- [x] **Fix App Routing**: App content now properly renders via `<router-outlet />`.

### 4.2 Typography Upgrade (Completed)
- [x] **Roboto Flex Variable Font**: Replaced static Roboto with Roboto Flex for:
    -   Variable optical sizing (`opsz`)
    -   Full weight range (100-1000)
    -   Better typographic control across components
- [x] **Global Utility Classes**: Added `.font-thin` through `.font-black` classes.

### 4.3 Login Page Redesign (Completed)
- [x] **Dark Gradient Background**: Deep navy to blue gradient matching brand.
- [x] **Aurora Animation**: Subtle animated radial gradients using Rose Pompadour & Moonstone Blue.
- [x] **Glassmorphism Card**: Frosted glass effect with backdrop blur.
- [x] **Logo with Gradient Icon**: Flask icon in gradient container.
- [x] **Form Styling**: Dark-themed inputs with icons (person, lock).
- [x] **Sign-In Button**: Gradient button with hover effects and loading spinner.
- [x] **Responsive Design**: Mobile-first responsive layout.

### 4.4 Public Splash Page (Completed)
- [x] **New Route Structure**:
    -   `/` → Public splash page (no auth)
    -   `/login` → Login page (no auth)
    -   `/app/*` → Authenticated app (with auth guard)
- [x] **Splash Component Features**:
    -   Animated floating orb background using brand colors
    -   Hero section with logo, title, subtitle
    -   CTA buttons: "Sign In" and "View on GitHub"
    -   Feature cards grid (4 features)
    -   Responsive layout for mobile/tablet/desktop
- [x] **Navigation Updates**:
    -   Sidebar links updated to `/app/...` paths
    -   Login redirect to `/app/home` after auth
    -   Legacy route redirects for backwards compatibility

---

## Phase 5: Continued UI/UX Improvements (In Progress)

### User Decisions (Dec 20, 2025)

| Topic | Decision |
|-------|----------|
| **Branding/Logo** | Keep flask icon as placeholder; custom logo to be provided later |
| **Content** | Feature descriptions are fine for now |
| **Registration** | ✅ Add user registration flow |
| **OAuth/Social Login** | ✅ Add if not too challenging |
| **Forgot Password** | ✅ Add forgot password flow |
| **Dashboard** | Real-time monitoring of running experiments + Run/Schedule Protocol button |
| **Light Theme** | ✅ Redesign to match dark aesthetic |
| **Theme Toggle on Splash** | ✅ Add theme toggle |

### 5.1 Implementation Status

#### Priority 1: Theme System & Toggle ✅ COMPLETED
- [x] Create light theme that matches dark aesthetic
- [x] Add theme toggle button to splash page
- [x] Persist theme preference in localStorage
- [x] Theme-aware CSS variables for all components

#### Priority 2: Auth Flow UI ✅ COMPLETED (UI Only)
- [x] **Registration Page** (`/register`): Email, username, password, confirm password, terms checkbox
- [x] **Forgot Password** (`/forgot-password`): Email input, success state
- [x] **OAuth Buttons** (UI only): Google and GitHub buttons rendered
- [x] Login page links to forgot-password and register

**⚠️ NOTE: Auth backend integration pending (see Phase 7 below)**

#### Priority 3: Dashboard Redesign ✅ COMPLETED
- [x] **Real-time Experiment Monitoring**:
  - Live experiments panel with status cards
  - Progress bars for running protocols
  - Integration with ExecutionService signals
  - Time-ago formatting and status tracking
- [x] **Quick Actions**:
  - "Run Protocol" primary CTA button (gradient styled)
  - "Schedule" secondary button
- [x] **Stats Overview**:
  - Running experiments count with pulse indicator
  - Instruments online/total
  - Protocols count
  - Resources count
- [x] **Recent Activity Feed**:
  - Last executed protocols with status chips
  - Duration and time information
  - Status-colored icons
- [x] **Quick Links Panel**:
  - Grid of navigation shortcuts
  - Hover effects with brand colors
- [x] **Responsive Design**:
  - Mobile-optimized grid layouts
  - Touch-friendly sizing

#### Priority 4: Polish (Partially Done)
- [x] Empty state designs (implemented in dashboard)
- [ ] Loading skeletons for all data views
- [ ] 404 and error pages
- [ ] Micro-animations and transitions

---

## Phase 6.5: Keycloak Theming (Backlog - Post-MVP)
- [ ] **Custom Theme**: Implement `lex` keycloak theme aligned with app design.
- [ ] **Keycloakify**: Investigate [keycloakify](https://github.com/keycloakify/keycloakify) for streamlined React/Angular wrapper generation.
- [ ] **Styling**: Match gradient background, fonts (Roboto Flex), and glassmorphism cards.

---

## Phase 6: E2E Testing (BLOCKED)
- [ ] **Playwright Scenarios**:
    -   Login -> Upload Protocol -> Configure Params -> Start Run.
    -   Asset CRUD operations.
- [x] **Smoke Test**: Basic navigation and rendering (passing when runnable).
- [x] **User Journeys**: Asset listing and Protocol Wizard flow (passing when runnable).
- [ ] **Advanced Scenarios**: CRUD operations, Error states.

---

## Phase 7: Auth Integration (In Progress - Dec 2025)

### Overview
Integrating **Keycloak** for enterprise-grade identity management. The frontend integration is complete; backend token validation is pending.

### Recommended Approach: keycloak-angular

**Library**: `keycloak-angular@20` + `keycloak-js@26`
- Installed with `--legacy-peer-deps` due to Angular 21 compatibility
- **Docs**: https://github.com/mauriciovigolo/keycloak-angular

### Frontend Tasks
| Task | Status | Notes |
|------|--------|-------|
| Install keycloak-angular | ✅ Done | Installed v20 with keycloak-js v26 |
| Configure KeycloakService | ✅ Done | Custom service with Angular signals |
| APP_INITIALIZER setup | ✅ Done | Initializes Keycloak on app startup |
| Replace custom AuthGuard | ✅ Done | Uses KeycloakService.isAuthenticated() |
| Replace HTTP interceptor | ✅ Done | Custom interceptor with async token fetch |
| Token refresh handling | ✅ Done | Automatic via keycloak-js |
| Logout cleanup | ✅ Done | Keycloak session invalidation |
| Update auth UI components | ✅ Done | Login/Register/ForgotPassword redirect to Keycloak |

### Backend Tasks
| Task | Status | Notes |
|------|--------|-------|
| Keycloak server setup | ✅ Done | Docker compose with praxis realm |
| Realm/Client configuration | ✅ Done | praxis-realm.json pre-configured |
| Token validation middleware | ❌ Pending | Validate Keycloak JWTs (deferred) |
| OAuth provider setup | ❌ Pending | Configure Google/GitHub in Keycloak |

### Key Files Changed (Dec 20, 2025)
- `app/core/auth/keycloak.service.ts` - NEW: Keycloak wrapper with Angular signals
- `app/app.config.ts` - APP_INITIALIZER + Bearer token interceptor
- `app/core/guards/auth.guard.ts` - Uses KeycloakService
- `app/core/store/app.store.ts` - Auth state from Keycloak via computed signals
- `app/features/auth/{login,register,forgot-password}.component.ts` - Redirect to Keycloak
- `environments/environment.ts` - Keycloak config added
- `public/silent-check-sso.html` - NEW: SSO iframe page

### Test User
- **Username**: `testuser`
- **Password**: `password123`
- Created via `kcadm.sh` in Keycloak praxis realm

---

## Technical Constraints
-   **Strict Typing**: No `any`. Define interfaces for all API responses.
-   **OnPush**: All components must use `ChangeDetectionStrategy.OnPush`.
-   **Signals**: Use Signals for all local state.
-   **Typography**: Use Roboto Flex with appropriate `font-weight` and `font-optical-sizing: auto`.

---

## How to Run the Frontend

### Prerequisites
- Docker Desktop running (for database)
- Node.js 20.x or higher
- npm 11.x or higher

### Quick Start

```bash
# Terminal 1: Start database
cd /Users/mar/MIT\ Dropbox/Marielle\ Russo/PLR_workspace/pylabpraxis
make db-test

# Terminal 1: Run migrations and start backend
uv run alembic upgrade head
PRAXIS_DB_DSN="postgresql+asyncpg://test_user:test_password@localhost:5433/test_db" uv run uvicorn main:app --reload --port 8000

# Terminal 2: Start frontend
cd praxis/web-client
npm install  # first time only
npm start
```

### Access Points
- **Splash Page**: http://localhost:4200/
- **Login Page**: http://localhost:4200/login
- **App (after login)**: http://localhost:4200/app/home
- **Backend Docs**: http://localhost:8000/docs

---

## Troubleshooting (Dec 20, 2025)

### 1. Server Connection Errors
**Symptoms**: `net::ERR_CONNECTION_REFUSED` or `[vite] server connection lost`
**Cause**: The background server processes (uvicorn or ng serve) may stop or be terminated by the environment.
**Fix**: Restart the servers.
```bash
# Backend
PRAXIS_DB_DSN="postgresql+asyncpg://test_user:test_password@localhost:5433/test_db" uv run uvicorn main:app --reload --port 8000

# Frontend
cd praxis/web-client && npm start
```

### 2. Browser Quota Exceeded
**Symptoms**: `Error: Resource::kQuotaBytes quota exceeded`
**Cause**: Often a side effect of connection loops filling logs or a corrupted browser state after a server crash.
**Fix**:
1. Check if backend is running.
2. Clear browser Local Storage / Site settings for localhost:4200.
3. Refresh page.

### 3. Test User Credentials
Since the database is initially empty, a test user must be created.
**User**: `admin`
**Password**: `password123`
(Created via manual script, verified in running DB).
