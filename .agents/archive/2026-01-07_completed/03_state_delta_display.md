# Prompt 3: State Delta Display (Phase 8.4)

**Priority**: P2
**Difficulty**: Medium
**Type**: Well-Specified Feature

> **IMPORTANT**: Do NOT use the browser agent. Verify with automated tests only.

---

## Context

Phase 8.4 of Simulation UI Integration requires showing state changes at each operation in the Execution Monitor. The backend simulation data includes state deltas per operation.

**Related backlog**: `.agents/backlog/simulation_ui_integration.md`

---

## Background: Available Data

The simulation cache provides per-operation state:

```json
{
  "operations": [
    {
      "index": 0,
      "operation": "lh.aspirate(source['A1'], 50)",
      "state_before": { "source['A1'].volume": 500 },
      "state_after": { "source['A1'].volume": 450 },
      "state_delta": { "source['A1'].volume": -50 }
    }
  ]
}
```

---

## Tasks

### 1. Create StateDeltaComponent

Create `praxis/web-client/src/app/features/execution-monitor/components/state-delta/state-delta.component.ts`:

```typescript
import { Component, input, ChangeDetectionStrategy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatIconModule } from '@angular/material/icon';
import { MatTooltipModule } from '@angular/material/tooltip';

interface StateDelta {
  key: string;
  before: number | string;
  after: number | string;
  change: number | string;
}

@Component({
  selector: 'app-state-delta',
  standalone: true,
  imports: [CommonModule, MatIconModule, MatTooltipModule],
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    <div class="state-delta-container">
      @for (delta of deltas(); track delta.key) {
        <div class="delta-row" [class.positive]="isPositive(delta)" [class.negative]="isNegative(delta)">
          <span class="delta-key">{{ formatKey(delta.key) }}</span>
          <span class="delta-change">
            @if (isPositive(delta)) {
              <mat-icon class="icon-sm">arrow_upward</mat-icon>
            } @else if (isNegative(delta)) {
              <mat-icon class="icon-sm">arrow_downward</mat-icon>
            }
            {{ formatChange(delta.change) }}
          </span>
          <span class="delta-values">
            {{ delta.before }} → {{ delta.after }}
          </span>
        </div>
      }
      @if (deltas().length === 0) {
        <div class="no-changes">No state changes</div>
      }
    </div>
  `,
  styles: [`
    .state-delta-container {
      font-size: 0.875rem;
      padding: 8px;
    }
    .delta-row {
      display: flex;
      align-items: center;
      gap: 8px;
      padding: 4px 0;
      border-bottom: 1px solid var(--mat-sys-outline-variant);
    }
    .delta-key {
      flex: 1;
      font-family: monospace;
      color: var(--mat-sys-on-surface);
    }
    .delta-change {
      display: flex;
      align-items: center;
      gap: 2px;
      font-weight: 600;
    }
    .delta-values {
      color: var(--mat-sys-on-surface-variant);
      font-size: 0.75rem;
    }
    .positive .delta-change { color: #22c55e; }
    .negative .delta-change { color: #ef4444; }
    .icon-sm { font-size: 14px; width: 14px; height: 14px; }
    .no-changes { 
      color: var(--mat-sys-on-surface-variant); 
      font-style: italic;
    }
  `]
})
export class StateDeltaComponent {
  deltas = input<StateDelta[]>([]);

  isPositive(delta: StateDelta): boolean {
    return typeof delta.change === 'number' && delta.change > 0;
  }

  isNegative(delta: StateDelta): boolean {
    return typeof delta.change === 'number' && delta.change < 0;
  }

  formatKey(key: string): string {
    // source['A1'].volume → A1.volume
    return key.replace(/.*\['?([^']+)'?\]\./, '$1.');
  }

  formatChange(change: number | string): string {
    if (typeof change === 'number') {
      return change > 0 ? `+${change}` : `${change}`;
    }
    return String(change);
  }
}
```

### 2. Create Unit Tests

Create `praxis/web-client/src/app/features/execution-monitor/components/state-delta/state-delta.component.spec.ts`:

```typescript
import { ComponentFixture, TestBed } from '@angular/core/testing';
import { StateDeltaComponent } from './state-delta.component';
import { NoopAnimationsModule } from '@angular/platform-browser/animations';

describe('StateDeltaComponent', () => {
  let component: StateDeltaComponent;
  let fixture: ComponentFixture<StateDeltaComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [StateDeltaComponent, NoopAnimationsModule]
    }).compileComponents();

    fixture = TestBed.createComponent(StateDeltaComponent);
    component = fixture.componentInstance;
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('should detect positive changes', () => {
    expect(component.isPositive({ key: 'test', before: 0, after: 10, change: 10 })).toBe(true);
    expect(component.isPositive({ key: 'test', before: 10, after: 0, change: -10 })).toBe(false);
  });

  it('should detect negative changes', () => {
    expect(component.isNegative({ key: 'test', before: 10, after: 0, change: -10 })).toBe(true);
    expect(component.isNegative({ key: 'test', before: 0, after: 10, change: 10 })).toBe(false);
  });

  it('should format keys correctly', () => {
    expect(component.formatKey("source['A1'].volume")).toBe('A1.volume');
    expect(component.formatKey("tips.available")).toBe('tips.available');
  });

  it('should format positive changes with plus sign', () => {
    expect(component.formatChange(50)).toBe('+50');
    expect(component.formatChange(-50)).toBe('-50');
  });
});
```

### 3. Integrate into Operation Timeline

Update `praxis/web-client/src/app/features/execution-monitor/components/run-detail/run-detail.component.ts`:

Find the operation list rendering and add state delta display:

```typescript
import { StateDeltaComponent } from '../state-delta/state-delta.component';

// In imports array:
imports: [
  // ...existing
  StateDeltaComponent,
],

// In template, within each operation item:
// After operation name/description, add:
`
@if (operation.state_delta && Object.keys(operation.state_delta).length > 0) {
  <app-state-delta [deltas]="formatDeltas(operation.state_delta)" />
}
`
```

Add helper method:

```typescript
formatDeltas(stateDelta: Record<string, number>): Array<{key: string, before: number, after: number, change: number}> {
  return Object.entries(stateDelta).map(([key, change]) => ({
    key,
    before: 0, // Would need state_before data
    after: 0,  // Would need state_after data
    change
  }));
}
```

---

## Verification

```bash
cd praxis/web-client && npm test -- --include='**/state-delta*'
```

---

## Success Criteria

- [ ] `StateDeltaComponent` created
- [ ] Positive/negative styling works
- [ ] Key formatting works (e.g., `source['A1'].volume` → `A1.volume`)
- [ ] Unit tests pass
- [ ] Component integrated into run-detail view
