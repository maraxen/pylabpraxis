# Prompt 9: Execution Monitor Phase 8.4 Tests

**Priority**: P2
**Difficulty**: Small
**Type**: Easy Win (Tests)

> **IMPORTANT**: Do NOT use the browser agent. Verify with automated tests only.

---

## Context

Phase 8.4 (State Delta Display) needs unit tests for integration with the Execution Monitor.

---

## Tasks

### 1. Create Integration Test File

Create `praxis/web-client/src/app/features/execution-monitor/execution-monitor.integration.spec.ts`:

```typescript
import { describe, it, expect, vi } from 'vitest';
import { TestBed } from '@angular/core/testing';
import { ExecutionMonitorComponent } from './execution-monitor.component';
import { NoopAnimationsModule } from '@angular/platform-browser/animations';
import { provideHttpClient } from '@angular/common/http';
import { provideRouter } from '@angular/router';

describe('ExecutionMonitor Integration', () => {
  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [
        ExecutionMonitorComponent,
        NoopAnimationsModule,
      ],
      providers: [
        provideHttpClient(),
        provideRouter([]),
      ]
    }).compileComponents();
  });

  it('should render without errors', () => {
    const fixture = TestBed.createComponent(ExecutionMonitorComponent);
    fixture.detectChanges();
    expect(fixture.componentInstance).toBeTruthy();
  });

  // Add more integration tests as needed
});
```

### 2. Test State Delta Component Integration

```typescript
import { StateDeltaComponent } from './components/state-delta/state-delta.component';

describe('StateDelta in ExecutionMonitor', () => {
  it('should display state deltas for operations with state changes', () => {
    const fixture = TestBed.createComponent(StateDeltaComponent);
    const component = fixture.componentInstance;
    
    // Set input
    fixture.componentRef.setInput('deltas', [
      { key: 'volume', before: 100, after: 50, change: -50 }
    ]);
    fixture.detectChanges();
    
    const compiled = fixture.nativeElement;
    expect(compiled.querySelector('.delta-row')).toBeTruthy();
    expect(compiled.textContent).toContain('-50');
  });

  it('should show "No state changes" when deltas is empty', () => {
    const fixture = TestBed.createComponent(StateDeltaComponent);
    fixture.componentRef.setInput('deltas', []);
    fixture.detectChanges();
    
    const compiled = fixture.nativeElement;
    expect(compiled.textContent).toContain('No state changes');
  });
});
```

---

## Verification

```bash
cd praxis/web-client && npm test -- --include='**/execution-monitor*'
```

---

## Success Criteria

- [ ] Integration test file created
- [ ] StateDelta component tests pass
- [ ] All execution-monitor tests pass
