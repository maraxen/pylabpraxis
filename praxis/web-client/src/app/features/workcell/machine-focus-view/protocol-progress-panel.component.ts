import { Component, ChangeDetectionStrategy, Input } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ProtocolRunSummary } from '../models/workcell-view.models';

@Component({
  selector: 'app-protocol-progress-panel',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div class="h-full flex flex-col p-4 bg-[var(--mat-sys-surface-container)] border-r border-[var(--mat-sys-outline-variant)]">
      <h3 class="text-sm font-semibold text-[var(--mat-sys-on-surface-variant)] uppercase tracking-wider mb-4">
        Protocol Progress
      </h3>

      @if (run) {
        <div class="flex-grow flex flex-col justify-center">
          <div class="flex items-center justify-between mb-2">
            <span class="text-base font-bold text-[var(--mat-sys-on-surface)] truncate">
              {{ run.protocolName }}
            </span>
            <span class="text-sm font-medium text-primary">
              {{ run.progress }}%
            </span>
          </div>

          <!-- Progress Bar -->
          <div class="w-full bg-[var(--mat-sys-surface-variant)] rounded-full h-2.5 mb-4 overflow-hidden">
            <div
              class="bg-primary h-full transition-all duration-500 ease-out"
              [style.width.%]="run.progress"
            ></div>
          </div>

          <div class="grid grid-cols-2 gap-4">
            <div class="flex flex-col">
              <span class="text-xs text-[var(--mat-sys-on-surface-variant)]">Step</span>
              <span class="text-sm font-medium text-[var(--mat-sys-on-surface)]">
                {{ run.currentStep }} / {{ run.totalSteps }}
              </span>
            </div>
            @if (run.estimatedRemaining) {
              <div class="flex flex-col">
                <span class="text-xs text-[var(--mat-sys-on-surface-variant)]">Est. Remaining</span>
                <span class="text-sm font-medium text-[var(--mat-sys-on-surface)]">
                  {{ formatDuration(run.estimatedRemaining) }}
                </span>
              </div>
            }
          </div>
        </div>
      } @else {
        <div class="flex-grow flex flex-col items-center justify-center text-[var(--mat-sys-on-surface-variant)] italic text-sm">
          <p>No active protocol</p>
        </div>
      }
    </div>
  `,
  styles: [`
    :host {
      display: block;
      height: 100%;
    }
  `],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class ProtocolProgressPanelComponent {
  @Input() run: ProtocolRunSummary | undefined;

  formatDuration(seconds: number): string {
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = seconds % 60;
    
    if (minutes > 0) {
      return `${minutes}m ${remainingSeconds}s`;
    }
    return `${remainingSeconds}s`;
  }
}