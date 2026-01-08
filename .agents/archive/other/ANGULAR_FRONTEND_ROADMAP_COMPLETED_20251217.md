# Angular v21 Frontend Development Roadmap

> **Migration Strategy**: Pre-release Flutter → Angular v21 with Material 3 Components

## Architecture Overview

### Tech Stack

| Layer | Technology |
|-------|------------|
| Framework | Angular v21 |
| UI Components | Angular Material 3 |
| State Management | NgRx Signals |
| HTTP | Angular HttpClient with Interceptors |
| Routing | Angular Router (Lazy Loading) |
| Forms | Reactive Forms |
| Auth | OIDC-compatible (Auth0/Keycloak) |

### Directory Structure

```
src/
├── app/
│   ├── core/                    # Singletons, guards, interceptors
│   │   ├── auth/
│   │   ├── http/
│   │   └── guards/
│   ├── shared/                  # Reusable components, pipes, directives
│   │   ├── components/
│   │   ├── directives/
│   │   └── pipes/
│   ├── features/                # Feature modules (lazy-loaded)
│   │   ├── auth/
│   │   ├── home/
│   │   ├── assets/
│   │   ├── protocols/
│   │   ├── run-protocol/
│   │   ├── visualizer/
│   │   └── settings/
│   └── layout/                  # App shell, nav, sidebar
├── environments/
└── styles/                      # Global styles, M3 theming
```

---

## Hydration Strategy

Angular v21 supports **Incremental Hydration** with `@defer` blocks. Our strategy:

1. **Static Shell First**: Render app shell (nav, sidebar) immediately
2. **Progressive Feature Hydration**: Defer heavy components until viewport/interaction
3. **SSR Consideration**: Prepare for SSR with `@angular/ssr` for future deployment

```typescript
// Example: Defer visualization component until visible
@defer (on viewport) {
  <app-deck-visualizer [layout]="deckLayout" />
} @placeholder {
  <mat-spinner diameter="40" />
}
```

---

## Feature Modules & Pages

### 1. Core Infrastructure (Phase 1)

| Component | Description |
|-----------|-------------|
| App Shell | Navigation, sidebar, user menu |
| Auth Guard | Route protection |
| HTTP Interceptor | Token injection, error handling |
| Theme Service | Material 3 theming support |

---

### 2. Authentication Module

| Page/Component | Type | Description |
|----------------|------|-------------|
| Login | Page | OIDC login flow |
| Logout | Action | Session termination |
| Auth Callback | Page | OAuth redirect handler |

**Flow**: Login → OIDC Provider → Callback → Home

---

### 3. Home Module

| Page/Component | Type | Description |
|----------------|------|-------------|
| Dashboard | Page | System overview, quick actions |
| Recent Activity | Widget | Recent protocol runs |
| System Status | Widget | Backend health indicators |

---

### 4. Asset Management Module

| Page/Component | Type | Description |
|----------------|------|-------------|
| Asset List | Page | Tabbed view: Instruments, Resources, Definitions |
| Asset Detail | Dialog | View/edit asset properties |
| Add Asset | Dialog | Create new asset wizard |
| Delete Confirmation | Dialog | Confirm delete action |

**CRUD Operations**:
- Instruments (Machines)
- Resource Instances (Labware)
- Resource Definitions (Catalog)

**Backend Endpoints**: `/machines`, `/resources`, `/decks`

---

### 5. Protocols Module

| Page/Component | Type | Description |
|----------------|------|-------------|
| Protocol Library | Page | Browse/search uploaded protocols |
| Protocol Upload | Dialog | Upload Python protocol file |
| Protocol Detail | Page | View protocol metadata, parameters |

**Backend Endpoints**: `/protocols`, `/discovery`

---

### 6. Run Protocol Module (Most Complex)

This is the primary workflow with multiple sequential steps.

| Page/Component | Type | Description |
|----------------|------|-------------|
| Protocol Selection | Step 1 | Select protocol from library |
| Parameter Configuration | Step 2 | Configure protocol parameters |
| Asset Assignment | Step 3 | Assign machines/resources to requirements |
| Deck Configuration | Step 4 | Configure deck layout |
| Deck Setup Verification | Step 5 | Visual verification of physical setup |
| Review & Prepare | Step 6 | Final review before execution |
| Start Protocol | Step 7 | Execute and monitor progress |

**Workflow Flow**:
```
Selection → Parameters → Assets → Deck Config → Verify → Review → Execute
```

**Dialogs/Sub-components**:
- Dictionary Parameter Editor
- String Parameter Editor
- Resource Picker
- Deck Slot Editor

**Backend Endpoints**: `/protocols/prepare`, `/protocols/run`, `/scheduler`

---

### 7. Visualizer Module

| Page/Component | Type | Description |
|----------------|------|-------------|
| Deck Visualizer | Page | 2D/3D deck layout visualization |
| Resource Inspector | Panel | Selected resource details |
| Animation Controls | Widget | Playback for protocol simulation |

**Rendering Options**:
- Canvas 2D (simpler)
- Three.js (for 3D features)
- SVG-based (for accessibility)

---

### 8. Settings Module

| Page/Component | Type | Description |
|----------------|------|-------------|
| User Preferences | Page | Theme, notifications, display settings |
| System Config | Page | Backend URL, connection settings |

---

## Forms Inventory

| Form | Module | Fields (High-Level) |
|------|--------|---------------------|
| Login | Auth | username, password |
| Protocol Upload | Protocols | file, name, description |
| Parameter Configuration | Run Protocol | Dynamic based on protocol |
| Asset Create/Edit | Assets | name, type, properties |
| Deck Layout Edit | Assets | slots, positions |
| User Preferences | Settings | theme, locale |

---

## Development Phases

### Phase 1: Foundation (Week 1-2)

- [ ] Initialize Angular v21 project
- [ ] Configure Material 3 theming
- [ ] Setup NgRx Signals store
- [ ] Implement HTTP interceptor layer
- [ ] Create app shell (nav, sidebar)
- [ ] Implement auth guard & OIDC flow

**Deliverable**: Authenticated app shell with navigation

---

### Phase 2: Core Features (Week 3-4)

- [ ] Home dashboard
- [ ] Asset Management CRUD
- [ ] Protocol Library (read-only)
- [ ] Basic error handling & snackbar notifications

**Deliverable**: Working asset management with backend integration

---

### Phase 3: Protocol Workflow (Week 5-7)

- [ ] Protocol Selection screen
- [ ] Parameter Configuration (dynamic forms)
- [ ] Asset Assignment screen
- [ ] Deck Configuration screen
- [ ] Deck Setup Verification
- [ ] Review & Prepare screen
- [ ] Execution monitoring

**Deliverable**: Complete protocol run workflow

---

### Phase 4: Visualization (Week 8-9)

- [ ] 2D Deck Visualizer component
- [ ] Resource inspector panel
- [ ] Protocol simulation/animation

**Deliverable**: Interactive deck visualization

---

### Phase 5: Polish & Testing (Week 10+) - **ACTIVE**

- [ ] Unit tests (Jasmine/Karma or Jest) -> **Targeting Vitest per package.json**
- [ ] E2E tests (Playwright/Cypress) -> **Targeting Playwright per package.json**
- [ ] Accessibility audit
- [ ] Performance optimization
- [ ] Documentation

---

## API Integration Points

| Endpoint | Method | UI Usage |
|----------|--------|----------|
| `/api/v1/machines` | GET/POST/PUT/DELETE | Asset Management |
| `/api/v1/resources` | GET/POST/PUT/DELETE | Asset Management |
| `/api/v1/decks` | GET/POST/PUT/DELETE | Asset Management |
| `/api/v1/protocols` | GET/POST | Protocol Library |
| `/api/v1/protocols/prepare` | POST | Protocol Preparation |
| `/api/v1/protocols/run` | POST | Protocol Execution |
| `/api/v1/scheduler` | GET/POST | Job Scheduling |
| `/api/v1/discovery` | GET | Type Definitions |
| `/api/v1/outputs` | GET | Run Outputs |
| `/api/v1/workcell` | GET | Workcell Configuration |

---

## Component Development Priority

1. **Shared Components** (Build first, reuse everywhere)
   - Data tables with pagination
   - Confirmation dialogs
   - Form field wrappers
   - Loading indicators
   - Error boundaries

2. **Feature Components** (Build per-feature)
   - Feature-specific forms
   - Feature-specific visualizations
   - Feature-specific dialogs

---

## Design Decisions

| Decision | Choice | Notes |
|----------|--------|-------|
| Visualization | **SVG** | Simpler, accessible, Three.js can be added later |
| Real-time Updates | **WebSockets** | Best practice for low-latency execution monitoring; can start with polling and migrate |
| Responsive Layouts | **Progressive** | Ensure responsive structure, but don't sacrifice dev agility initially |
| Offline Capability | TBD | Not a priority for initial release |
| Internationalization | TBD | Not a priority for initial release |

> **WebSocket Strategy**: Use RxJS `webSocket` for protocol execution status. Backend should expose a `/ws/protocol/{run_id}` endpoint for real-time execution events.

---

## Next Steps

1. **Review this roadmap** for completeness
2. **Start Phase 1** with project initialization
3. **Define detailed specs** for each component as development begins
