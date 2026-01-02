# Praxis Development Matrix

**Last Updated**: 2026-01-02 (Asset Management Planning)
**Purpose**: Consolidated view of all remaining work items with priority and difficulty ratings.

---

## Priority Legend

| Priority | Description |
|----------|-------------|
| **P1** | Critical - Must fix before merge |
| **P2** | High - MVP → Full implementation |
| **P3** | Medium - Post-merge enhancements |
| **P4** | Low - Future features |

## Difficulty Legend

| Difficulty | Estimated Effort |
|------------|------------------|
| **S** | Small (< 2 hours) |
| **M** | Medium (2-8 hours) |
| **L** | Large (1-3 days) |
| **XL** | Extra Large (3+ days) |

---

## Asset Management (Active Sprint)

| Item | Priority | Difficulty | Backlog | Description |
|------|----------|------------|---------|-------------|
| **Spatial View Filters** | P3 | M | [asset_management::Spatial View](./backlog/asset_management.md) | Sort/Filter by location, workcell, maintenance |
| **Maintenance Schema** | P3 | M | [asset_management::Maintenance](./backlog/asset_management.md) | Pydantic models & db fields |
| **Global/Asset Maintenance Toggle** | P3 | S | [asset_management::Maintenance](./backlog/asset_management.md) | Settings & Asset Details UI |
| **Maintenance Badges** | P3 | S | [asset_management::Maintenance](./backlog/asset_management.md) | Visual status indicators |
| **Registry vs Inventory API** | P4 | L | [TECHNICAL_DEBT](./TECHNICAL_DEBT.md) | Split API routes (Deferred) |

---

## Pre-Merge Finalization

| Item | Priority | Difficulty | Backlog | Description |
|------|----------|------------|---------|-------------|
| **Pre-Merge Finalization & Cleanup** | P1 | M | [pre_merge_finalization.md](./backlog/pre_merge_finalization.md) | Archive docs, cleanup files, reusable prompts |

---

## UI/UX

[... existing completed items ...]

---

## Backend

[... existing items ...]

---

## Summary by Priority

| Priority | Count | Description |
|----------|-------|-------------|
| **P1** | 1 | Critical items blocking merge |
| **P2** | 31 | High priority MVP completions |
| **P3** | 51 | Post-merge enhancements (+4 Asset Mgmt) |
| **P4** | 15 | Future feature considerations |
