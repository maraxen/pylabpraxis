# AUDIT-03: Implement PAUSE/CANCEL Execution Controls

## Problem

The UI provides no PAUSE, RESUME, or CANCEL controls for running protocols. This is a critical safety and usability gap.

## Target Files

- `praxis/web-client/src/app/features/execution-monitor/components/run-detail.component.ts`
- `praxis/web-client/src/app/features/execution-monitor/components/run-detail.component.html`
- `praxis/web-client/src/app/features/run-protocol/services/execution.service.ts`

## Requirements

### 1. Add Control Buttons to Template

In `run-detail.component.html`, add PAUSE and CANCEL buttons near the run status display:

```html
<div class="run-controls" *ngIf="run()?.status === 'RUNNING' || run()?.status === 'PAUSED'">
  <button mat-raised-button color="warn" (click)="cancelRun()" [disabled]="isCancelling()">
    <mat-icon>stop</mat-icon> Cancel
  </button>
  <button mat-raised-button (click)="togglePause()" [disabled]="isToggling()">
    <mat-icon>{{ run()?.status === 'PAUSED' ? 'play_arrow' : 'pause' }}</mat-icon>
    {{ run()?.status === 'PAUSED' ? 'Resume' : 'Pause' }}
  </button>
</div>
```

### 2. Add Component Methods

In `run-detail.component.ts`:

```typescript
isCancelling = signal(false);
isToggling = signal(false);

cancelRun() {
  this.isCancelling.set(true);
  this.executionService.cancel(this.runId()).subscribe({
    next: () => this.snackBar.open('Run cancelled', 'Close', { duration: 3000 }),
    error: (err) => this.snackBar.open('Failed to cancel: ' + err.message, 'Close'),
    complete: () => this.isCancelling.set(false)
  });
}

togglePause() {
  this.isToggling.set(true);
  const action = this.run()?.status === 'PAUSED' ? 'resume' : 'pause';
  this.executionService[action](this.runId()).subscribe({
    next: () => {},
    error: (err) => this.snackBar.open('Failed to ' + action + ': ' + err.message, 'Close'),
    complete: () => this.isToggling.set(false)
  });
}
```

### 3. Add Service Methods

In `execution.service.ts`, add:

```typescript
cancel(runId: string): Observable<void> {
  if (this.modeService.isBrowserMode()) {
    // Browser mode: stop Python runtime
    return this.pythonRuntimeService.stop();
  }
  return this.api.cancelRun(runId);
}

pause(runId: string): Observable<void> {
  return this.api.pauseRun(runId);
}

resume(runId: string): Observable<void> {
  return this.api.resumeRun(runId);
}
```

### 4. Update Visual State

Update the timeline step styling to handle PAUSED state distinctly from RUNNING.

## State Machine Reference

```
QUEUED -> RUNNING -> PAUSED -> RUNNING
                  -> COMPLETED
                  -> FAILED
       -> CANCELLED
```

## Reference

See `docs/audits/AUDIT-03-protocol-execution.md` for full gap analysis.

## Verification

```bash
npm run test --prefix praxis/web-client
npx playwright test e2e/specs/execution-monitor.spec.ts
```
