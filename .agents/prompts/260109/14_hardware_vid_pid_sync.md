# Agent Prompt: 14_hardware_vid_pid_sync

Examine `.agents/README.md` for development context.

**Status:** 🟢 Not Started  
**Batch:** [260109](./README.md)  
**Backlog:** [hardware_connectivity.md](../../backlog/hardware_connectivity.md)  

---

## Task

Replace hardcoded `KNOWN_DEVICES` VID/PID map with dynamic hardware definitions synced from PLR backend classes.

---

## Context Files

| File | Purpose |
|:-----|:--------|
| [hardware_connectivity.md](../../backlog/hardware_connectivity.md) | Work item tracking (Section 5) |
| `praxis/web-client/src/app/core/services/hardware-discovery.service.ts` | Frontend discovery service |
| `praxis/backend/services/machine_type_definition.py` | Backend type definitions |

---

## Implementation

### Backend

1. **Enhance `MachineTypeDefinitionService`**:
   - Extract `USB_VENDOR_ID` and `USB_PRODUCT_ID` from backend classes
   - Add to machine type definition model

2. **Create API Endpoint**:

   ```python
   @router.get("/api/v1/hardware/definitions")
   async def get_hardware_definitions():
       """Return supported VID/PID pairs for WebSerial filtering."""
       return service.get_usb_device_definitions()
   ```

### Frontend

1. **Update `HardwareDiscoveryService`**:
   - Fetch definitions from API on init
   - Build WebSerial filter list dynamically
   - Fallback to static `KNOWN_DEVICES` if API unavailable

---

## Expected Outcome

- VID/PID list auto-updates when new backends are added
- No manual maintenance of `KNOWN_DEVICES` map
- WebSerial picker shows all supported devices

---

## Project Conventions

- **Commands**: Use `uv run` for all Python commands
- **Backend Tests**: `uv run pytest tests/ -v`
- **Frontend Tests**: `cd praxis/web-client && npm test`

---

## On Completion

- [ ] Commit changes with descriptive message
- [ ] Update backlog item status
- [ ] Mark this prompt complete in batch README

---

## References

- [.agents/README.md](../../README.md) - Environment overview
