# PyLabPraxis Roadmap

**Last Updated**: 2025-12-26

---

## ✅ Completed Phases

| Phase | Description | Status |
|-------|-------------|--------|
| 0 | Fix PLR Discovery Filtering | ✅ Dec 21 |
| 1 | Protocol Library & Simulation Mode | ✅ Dec 21 |
| 2.1-2.5 | Asset Management Enhancements | ✅ Dec 22 |

---

## 🚧 Active Development

### Phase 2.7: Resource Selection & Protocol Execution

This phase is split into two parallel conductor tracks:

| Track | Focus | Location |
|-------|-------|----------|
| **first_light** | E2E Protocol Execution | `conductor/tracks/first_light_20251222/` |
| **workflow_velocity** | UI/UX Polish | `conductor/tracks/workflow_velocity_20251223/` |

#### Key Tasks (from tracks)

**First Light (Priority)**:

- [ ] Asset selector PLR type filtering
- [ ] Resource binding in protocol wizard
- [ ] Backend asset resolution
- [ ] Simulation mode toggle

**Workflow Velocity**:

- [ ] Backend-driven filtering
- [ ] Property-based dynamic chips
- [ ] Skirted vs plate type separation
- [ ] Loading skeletons & polish

---

## 📋 Future Phases

### Phase 2.8: Machine Selection Enhancement

- Machine attribute parsing
- Dynamic machine filtering
- Protocol machine binding

### Phase 2.9: Browser Instrument Detection (Experimental)

- WebUSB/WebSerial APIs
- VID/PID matching
- One-click connection

### Phase 3: Deck Visualizer

- PLR visualizer integration
- Interactive deck configuration
- Real-time WebSocket updates

### Phase 4: Backend Infrastructure

- Keycloak JWT validation
- WebSocket reconnection
- Test coverage improvements

---

## 🚫 Deferred

- AI-Powered Search (2.7.3) - Until application is stable
- E2E Playwright Tests - Environment issues

---

## Quick Commands

```bash
# Start all services
make db-test
docker-compose up keycloak
PRAXIS_DB_DSN="..." uv run uvicorn main:app --reload --port 8000
cd praxis/web-client && npm start

# Sync definitions
curl -X POST http://localhost:8000/api/v1/discovery/sync-all
```

---

*For detailed task tracking, see `conductor/tracks/` directories.*
