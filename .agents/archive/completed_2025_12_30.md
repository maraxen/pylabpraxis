# Completed Items Archive - 2025-12-30

**Source**: `ROADMAP.md`, `backlog/backend.md`, `backlog/ui-ux.md`
**Archived By**: Antigravity

---

## 🚀 Released Features (December Sprint)

### UI/UX & Polish

- [x] **Chip Hover Information**: Tooltips added to resource chips explaining their usage (Consumable, Protocol constraints).
- [x] **Rename to Praxis**: Global search/replace completed (PyLabPraxis -> Praxis).
- [x] **"Machines" Wording**: Standardized on "Machines" instead of "Instruments" throughout frontend and backend.
- [x] **Data Viz Dashboard**: Added protocol selector, integrated deterministic demo data, and Plotly charts.
- [x] **Command Palette Fixes**: Fixed Alt/Option mapping and keyboard navigation.
- [x] **Visual Polish**: Refined aesthetics, spacing, gradients, and dark mode consistency.

### Backend & Hardware

- [x] **PLR Definitions Sync**:
  - Curated demo dataset (`plr-definitions.ts`) created and wired.
  - Demo interceptor handling type definitions.
- [x] **Machine Autodiscovery**:
  - `DiscoveryService` implementing `discover_serial_ports`, `discover_simulators`.
  - API endpoints: `/hardware/discover`, `/connect`, `/disconnect`, `/register`.
- [x] **Hardware Discovery UI**:
  - Dialog component with scan/connect/register workflows.
  - WebSerial/WebUSB API integration in frontend service.
  - PLR device inference from VID/PID.

### Documentation

- [x] **Docs Building**: MkDocs Material setup with comprehensive documentation structure.

---

## 📜 From `backlog/backend.md`

- [x] Protocol discovery via AST parsing
- [x] Backend execution flow (`ExecutionMixin`)
- [x] WebSocket log streaming
- [x] Simulation flag flow through stack
- [x] Orchestrator execution (100% coverage)
- [x] Hardware discovery service foundation
- [x] Hardware API endpoints (discover, connect, disconnect, register, repl)

## 📜 From `backlog/ui-ux.md`

- [x] ResourceDialog chip filtering
- [x] Skeleton loaders for categories/facets
- [x] Dark/Light theme with system variables
- [x] Basic context menu support
- [x] Deck visualizer integration (legacy iframe version)
