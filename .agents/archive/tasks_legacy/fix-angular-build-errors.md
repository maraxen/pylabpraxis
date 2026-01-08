# Angular Build Error Fixes

**Created**: 2026-01-02
**Status**: Completed

## Summary

7 TypeScript errors blocking `npm run build`. All are simple fixes.

---

## Error 1: Missing `from` keyword

**File**: `praxis/web-client/src/app/features/assets/components/machine-list/machine-list.component.ts:19`

**Error**: `TS1005: 'from' expected`

**Fix**:
```typescript
// Before (line 19)
import { MachineDetailsDialogComponent } './machine-details-dialog.component';

// After
import { MachineDetailsDialogComponent } from './machine-details-dialog.component';
```

---

## Error 2 & 3: Wrong import paths

**Files**:
- `src/app/features/assets/components/asset-filters/asset-filters.component.ts:11`
- `src/app/features/assets/components/maintenance-badge/maintenance-badge.component.ts:5`

**Error**: `TS2307: Cannot find module '../../../models/asset.models'`

**Fix**: Change path from 3 levels up to 2 levels up:
```typescript
// Before
import { Machine } from '../../../models/asset.models';

// After
import { Machine } from '../../models/asset.models';
```

---

## Error 4: Getter called as function

**File**: `src/app/features/assets/services/asset.service.ts:89`

**Error**: `TS6234: This expression is not callable because it is a 'get' accessor`

**Fix**: Remove parentheses from getter:
```typescript
// Before (line 89)
const repo = await firstValueFrom(this.sqliteService.resourceDefinitions());

// After
const repo = await firstValueFrom(this.sqliteService.resourceDefinitions);
```

---

## Error 5: Missing type fields

**File**: `src/app/features/assets/components/machine-list/machine-details-dialog.component.ts:433`

**Error**: `TS2353: 'maintenance_enabled' does not exist in type 'Partial<MachineCreate>'`

**Fix**: Add maintenance fields to `MachineCreate` interface in `asset.models.ts`:
```typescript
// In src/app/features/assets/models/asset.models.ts
// Add to MachineCreate interface (around line 70-81):

export interface MachineCreate {
  name: string;
  status?: MachineStatus;
  description?: string;
  manufacturer?: string;
  model?: string;
  serial_number?: string;
  connection_info?: Record<string, any>;
  is_simulation_override?: boolean;
  user_configured_capabilities?: Record<string, any>;
  machine_definition_accession_id?: string;
  // ADD THESE:
  maintenance_enabled?: boolean;
  maintenance_schedule_json?: MaintenanceSchedule;
  last_maintenance_json?: Record<string, MaintenanceRecord>;
}
```

---

## Error 6: Invalid status comparison

**File**: `src/app/features/run-protocol/services/consumable-assignment.service.ts:39`

**Error**: `TS2367: comparison appears unintentional because types have no overlap`

**Cause**: `ResourceStatus` enum doesn't include `'maintenance'` (that's in `MachineStatus`)

**Fix**: Remove the invalid comparison:
```typescript
// Before (lines 35-40)
const available = allResources.filter(r =>
    r.status !== 'reserved' &&
    r.status !== 'in_use' &&
    r.status !== 'expired' &&
    r.status !== 'maintenance'  // REMOVE THIS LINE
);

// After
const available = allResources.filter(r =>
    r.status !== 'reserved' &&
    r.status !== 'in_use' &&
    r.status !== 'expired'
);
```

---

## Quick Commands

After fixes, run:
```bash
cd praxis/web-client
npm run build
npm start
```

Browser mode URL: `http://localhost:4200`