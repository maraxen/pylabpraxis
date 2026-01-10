# Agent Prompt: Migrate Angular Services to Generated Client

Examine `.agents/README.md` for development context.

**Status:** 🟢 Not Started
**Priority:** P2
**Batch:** [260110](./README.md)
**Backlog Reference:** [sqlmodel_codegen_refactor.md](../../backlog/sqlmodel_codegen_refactor.md)
**Phase:** 6.2 — Frontend Migration: Angular Services
**Parallelizable:** ❌ Sequential — Requires P2_14 (TypeScript client generated)

---

## 1. The Task

Replace manual HTTP calls in Angular services with the generated API client methods. Update signal stores to use generated types.

**User Value:** Type-safe API calls with automatic request/response serialization matching backend exactly.

---

## 2. Technical Implementation Strategy

### Current Architecture

Manual HTTP services:
```typescript
// src/app/features/assets/services/asset.service.ts
@Injectable({ providedIn: 'root' })
export class AssetService {
  private http = inject(HttpClient);
  
  getAssets(): Observable<Asset[]> {
    return this.http.get<Asset[]>('/api/v1/assets');
  }
  
  createAsset(asset: AssetCreate): Observable<Asset> {
    return this.http.post<Asset>('/api/v1/assets', asset);
  }
}
```

### Target Architecture

Using generated client:
```typescript
// Option A: Use generated service directly
import { DefaultService } from '@api/services/DefaultService';

// Option B: Wrap generated service for Angular patterns
@Injectable({ providedIn: 'root' })
export class AssetService {
  private apiService = inject(DefaultService);
  
  getAssets(): Observable<AssetRead[]> {
    return from(this.apiService.getAssets());
  }
}
```

### Generated Client Patterns

The `openapi-typescript-codegen` generates Promise-based methods:
```typescript
// api-generated/services/DefaultService.ts
export class DefaultService {
  static getAssets(): CancelablePromise<AssetRead[]> { ... }
  static createAsset(requestBody: AssetCreate): CancelablePromise<AssetRead> { ... }
}
```

For Angular's Observable pattern, wrap with `from()`:
```typescript
import { from } from 'rxjs';

getAssets(): Observable<AssetRead[]> {
  return from(DefaultService.getAssets());
}
```

### Signal Store Updates

Update stores to use generated types:
```typescript
// Before
interface AssetState {
  assets: Asset[];  // Manual type
}

// After
import { AssetRead } from '@api';

interface AssetState {
  assets: AssetRead[];  // Generated type
}
```

---

## 3. Context & References

**Primary Files to Modify:**

| Path | Description |
|:-----|:------------|
| `src/app/features/assets/services/asset.service.ts` | Asset API service |
| `src/app/features/protocols/services/protocol.service.ts` | Protocol API service |
| `src/app/features/assets/stores/asset.store.ts` | Asset signal store (if exists) |
| `src/app/features/protocols/stores/protocol.store.ts` | Protocol signal store (if exists) |
| Other service files | As identified |

**Reference Files:**

| Path | Pattern Source |
|:-----|:---------------|
| `src/app/core/api-generated/services/` | Generated API methods |
| `src/app/core/api-generated/models/` | Generated types |

---

## 4. Constraints & Conventions

- **Commands**: Use `npm` for Angular operations.
- **Frontend Path**: `praxis/web-client`
- **State Management**: Use Signals where available (Angular 17+)
- **RxJS**: Convert Promises to Observables with `from()`

### Sharp Bits / Technical Debt

1. **Promise vs Observable**: Generated client uses Promises; wrap for RxJS
2. **Error handling**: Generated client may throw differently; update error handling
3. **Request interceptors**: Existing HttpClient interceptors won't apply to generated client
4. **Base URL configuration**: May need to configure generated client's base URL

---

## 5. Verification Plan

**Definition of Done:**

1. Angular build succeeds:
   ```bash
   cd praxis/web-client
   npm run build
   ```

2. All unit tests pass:
   ```bash
   cd praxis/web-client
   npm test
   ```

3. E2E tests pass (if available):
   ```bash
   cd praxis/web-client
   npm run e2e
   ```

4. Manual smoke test:
   - Start dev server: `npm start`
   - Navigate to assets page
   - Verify data loads
   - Verify CRUD operations work

---

## 6. Implementation Steps

1. **Audit current services**:
   ```bash
   find src/app/features -name "*.service.ts" -type f
   ```
   List all services that make HTTP calls.

2. **Configure generated client base URL**:
   - Find where base URL is configured in generated client
   - Set to match existing API base URL
   - Handle environment-specific URLs

3. **Create service wrapper pattern**:
   ```typescript
   // src/app/core/services/api-wrapper.service.ts
   @Injectable({ providedIn: 'root' })
   export class ApiWrapperService {
     // Utility methods for Promise→Observable conversion
     protected asObservable<T>(promise: CancelablePromise<T>): Observable<T> {
       return from(promise);
     }
   }
   ```

4. **Migrate AssetService**:
   - Update imports to generated types
   - Replace HttpClient calls with generated methods
   - Wrap Promises in Observables
   - Test asset list, create, update, delete

5. **Migrate ProtocolService**:
   - Similar pattern to AssetService

6. **Migrate remaining services**:
   - MachineService, ResourceService, etc.

7. **Update signal stores**:
   - Replace manual types with generated types
   - Update any type assertions

8. **Update components**:
   - Any components with inline API calls
   - Template type bindings

9. **Run full test suite**:
   ```bash
   npm run build && npm test
   ```

10. **Manual verification**:
    - Test each feature in browser
    - Verify network requests are correct

---

## 7. Service Migration Checklist

| Service | HTTP Methods | Generated Service | Status |
|:--------|:-------------|:------------------|:-------|
| `AssetService` | GET, POST, PUT, DELETE | `DefaultService` | ⬜ |
| `MachineService` | GET, POST, PUT, DELETE | `DefaultService` | ⬜ |
| `ResourceService` | GET, POST, PUT, DELETE | `DefaultService` | ⬜ |
| `ProtocolService` | GET, POST, PUT, DELETE | `DefaultService` | ⬜ |
| `DeckService` | GET, POST, PUT, DELETE | `DefaultService` | ⬜ |
| `SchedulerService` | GET, POST, DELETE | `DefaultService` | ⬜ |
| `WorkcellService` | GET, POST, PUT, DELETE | `DefaultService` | ⬜ |

---

## On Completion

- [ ] Commit changes with message: `refactor(frontend): migrate Angular services to generated API client`
- [ ] Update backlog item status in `sqlmodel_codegen_refactor.md` (Phase 6.2 → Done)
- [ ] Mark this prompt complete in batch README

---

## References

- `.agents/README.md` - Environment overview
- `.agents/backlog/sqlmodel_codegen_refactor.md` - Full migration plan
- `P2_14_generate_typescript_client.md` - TypeScript client generation (prerequisite)
