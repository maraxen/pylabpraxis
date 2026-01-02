# Praxis Development Roadmap

**Last Updated**: 2026-01-02 (Core Backend Enhancements Completed)
**Current Phase**: Post-MVP Polish & Asset Management

---

## Executive Summary

The `angular_refactor` branch has achieved MVP status. Current focus is on **Asset Management Enhancements** (Maintenance & Spatial Views) and final pre-merge cleanup. **Core Backend Enhancements** (Protocol Decorator, Deck Config, PLR Caching, Consumables) completed 2026-01-02.

---

## Priority 1: Critical (Must Fix Before Merge)

| Item | Description | Backlog |
|------|-------------|---------|
| **Finalization & Cleanup** | Archive docs, cleanup files, reusable prompts | [pre_merge_finalization.md](./backlog/pre_merge_finalization.md) |

---

## Priority 2: High (MVP → Full Implementation)

[... existing P2 items ...]

---

## Priority 3: Asset Management (Active)

| Item | Status | Description | Backlog |
|------|--------|-------------|---------|
| **Spatial View Filters** | ⏳ In Progress | Sort/Filter assets by location, status, etc. | [asset_management.md](./backlog/asset_management.md) |
| **Maintenance Tracking** | ⏳ In Progress | Schema, Scheduling, Alerts, Global Toggle | [asset_management.md](./backlog/asset_management.md) |
| **Groupings & Organization** | ✅ Done | Accordions for Resources/Machines | [asset_management.md](./backlog/asset_management.md) |
| **Registry/Inventory UI** | ✅ Done | Separate tabs for definitions/instances | [asset_management.md](./backlog/asset_management.md) |

---

## Priority 3: Core Backend Enhancements ✅ COMPLETE

| Item | Status | Description | Backlog |
|------|--------|-------------|---------|
| **Protocol Decorator Data Views** | ✅ Complete | Schema-based input data definitions | [backend.md](./backlog/backend.md) |
| **User-Specified Deck Config** | ✅ Complete | JSON/function-based deck layouts | [backend.md](./backlog/backend.md) |
| **Cached PLR Definitions** | ✅ Complete | Frontend uses cached dimensions | [backend.md](./backlog/backend.md) |
| **Consumables Auto-Assignment** | ✅ Complete | Smart assignment with scoring | [backend.md](./backlog/backend.md) |

---

## Priority 3: Hardware Infrastructure ✅ COMPLETE (2026-01-02)

| Item | Status | Description | Backlog |
|------|--------|-------------|---------|
| **mDNS Device Discovery** | ✅ Complete | Zeroconf scanning for Opentrons/Tecan/Hamilton/etc. | [backend.md](./backlog/backend.md) |
| **Connection State Persistence** | ✅ Complete | Redis/SQLite KV store for connection tracking | [backend.md](./backlog/backend.md) |
| **SqliteKeyValueStore** | ✅ Complete | Lite mode persistent KV store | [modes_and_deployment.md](./backlog/modes_and_deployment.md) |
| **Hardware UI Polish** | ✅ Complete | Connecting/error states with animations | [backend.md](./backlog/backend.md) |
| **Production Tunneling UI** | ✅ Complete | Settings help for remote hardware access | [modes_and_deployment.md](./backlog/modes_and_deployment.md) |

---

## Priority 3: Medium (Post-Merge Enhancements)

| Item | Status | Description | Tests Needed |
|------|--------|-------------|--------------|
| Unit Tests for Deck Config | Pending | Test `deck_config.py` module | Yes |
| Unit Tests for Data Views | Pending | Test data view processing | Yes |
| Unit Tests for Consumable Assignment | Pending | Test scoring and matching | Yes |
| Frontend Consumable Auto-Assignment | Pending | Browser-mode equivalent | Yes |

---

## Priority 4: Low (Future)

| Item | Description |
|------|-------------|
| Cost Optimization for Consumables | Optimize consumable selection by cost |
| Advanced Scheduling DES | Discrete event simulation engine |
| Multi-workcell Scheduling | Cross-workcell resource sharing |
