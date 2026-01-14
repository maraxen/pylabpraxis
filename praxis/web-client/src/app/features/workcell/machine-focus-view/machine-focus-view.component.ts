import { Component, ChangeDetectionStrategy, Input, output, signal, HostListener } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatIconModule } from '@angular/material/icon';
import { MachineWithRuntime } from '../models/workcell-view.models';
import { DeckViewComponent } from '../../../shared/components/deck-view/deck-view.component';
import { ProtocolProgressPanelComponent } from './protocol-progress-panel.component';
import { ResourceInspectorPanelComponent } from './resource-inspector-panel.component';
import { PlrResourceDetails } from '@core/models/plr.models';
import { DeckStateIndicatorComponent } from '../../../shared/components/workcell/deck-state-indicator/deck-state-indicator.component';

@Component({
  selector: 'app-machine-focus-view',
  standalone: true,
  imports: [
    CommonModule,
    MatIconModule,
    DeckViewComponent,
    ProtocolProgressPanelComponent,
    ResourceInspectorPanelComponent,
    DeckStateIndicatorComponent
  ],
  template: `
    <div class="flex flex-col h-full w-full glass-container overflow-hidden animate-in fade-in duration-300">
      <!-- Header -->
      <header class="flex items-center justify-between px-6 py-4 glass-header border-b border-[var(--mat-sys-outline-variant)] shrink-0 z-10">
        <div class="flex items-center gap-4">
          <button
            (click)="back.emit()"
            class="p-2 -ml-2 rounded-full hover:bg-[var(--mat-sys-surface-variant)] transition-colors text-[var(--mat-sys-on-surface-variant)]"
            title="Back to Dashboard (Esc)"
          >
            <mat-icon>arrow_back</mat-icon>
          </button>

          <div class="flex flex-col">
            <h1 class="text-xl font-bold text-[var(--mat-sys-on-surface)] leading-tight">
              {{ machine.name }}
            </h1>
            <div class="flex items-center gap-2">
              <span class="text-xs font-medium text-[var(--mat-sys-on-surface-variant)] uppercase tracking-wider">
                {{ machine.model || machine.manufacturer || 'Machine' }}
              </span>
              <span class="w-1 h-1 rounded-full bg-[var(--mat-sys-outline-variant)]"></span>
              <span class="text-xs font-medium" [class]="statusClass()">
                {{ machine.status | uppercase }}
              </span>
            </div>
          </div>
        </div>

        <div class="flex items-center gap-3">
          <!-- Deck State Source -->
          <app-deck-state-indicator [source]="machine.stateSource"></app-deck-state-indicator>

          <!-- Connection State Badge -->
          <div class="flex items-center gap-2 px-3 py-1.5 rounded-full bg-[var(--mat-sys-surface-container-high)] border border-[var(--mat-sys-outline-variant)]">
            <div
              class="w-2 h-2 rounded-full"
              [class.bg-emerald-500]="machine.connectionState === 'connected'"
              [class.bg-amber-500]="machine.connectionState === 'connecting'"
              [class.bg-rose-500]="machine.connectionState === 'disconnected'"
            ></div>
            <span class="text-xs font-semibold text-[var(--mat-sys-on-surface)] capitalize">
              {{ machine.connectionState }}
            </span>
          </div>
        </div>
      </header>

      <!-- Main Content Area (Deck View) -->
      <div class="flex-grow relative bg-[#1a1a2e] overflow-hidden">
        @if (machine.plr_definition) {
          <div class="absolute inset-0 flex items-center justify-center p-8 overflow-auto">
            <app-deck-view
              [resource]="machine.plr_definition"
              [state]="machine.plr_state"
              (resourceSelected)="onResourceSelected($event)"
              class="max-w-full max-h-full"
            ></app-deck-view>
          </div>
        } @else {
          <div class="flex flex-col items-center justify-center h-full text-[var(--mat-sys-on-surface-variant)] gap-4">
            <mat-icon class="text-6xl">grid_off</mat-icon>
            <p class="text-lg">No deck definition available for this machine</p>
          </div>
        }

        <!-- Floating Alerts (Optional) -->
        @if (machine.alerts.length > 0) {
          <div class="absolute top-6 right-6 flex flex-col gap-2 max-w-sm pointer-events-none z-20">
            @for (alert of machine.alerts; track alert.message) {
              <div
                class="pointer-events-auto px-4 py-3 rounded-lg border shadow-lg flex gap-3 animate-in slide-in-from-right-4"
                [class.bg-amber-50]="alert.severity === 'warning'"
                [class.border-amber-200]="alert.severity === 'warning'"
                [class.text-amber-900]="alert.severity === 'warning'"
                [class.bg-rose-50]="alert.severity === 'error'"
                [class.border-rose-200]="alert.severity === 'error'"
                [class.text-rose-900]="alert.severity === 'error'"
                [class.bg-blue-50]="alert.severity === 'info'"
                [class.border-blue-200]="alert.severity === 'info'"
                [class.text-blue-900]="alert.severity === 'info'"
              >
                <mat-icon class="text-xl">
                  {{ alert.severity === 'error' ? 'error' : alert.severity === 'warning' ? 'warning' : 'info' }}
                </mat-icon>
                <span class="text-sm font-medium">{{ alert.message }}</span>
              </div>
            }
          </div>
        }
      </div>

      <!-- Footer Panels -->
      <footer class="h-64 shrink-0 glass-footer border-t border-[var(--mat-sys-outline-variant)] grid grid-cols-12 overflow-hidden shadow-[0_-4px_20px_rgba(0,0,0,0.05)] z-10">
        <div class="col-span-12 md:col-span-5 lg:col-span-4 border-r border-[var(--mat-sys-outline-variant)]">
          <app-protocol-progress-panel [run]="machine.currentRun"></app-protocol-progress-panel>
        </div>
        <div class="col-span-12 md:col-span-7 lg:col-span-8">
          <app-resource-inspector-panel [resource]="selectedResource()"></app-resource-inspector-panel>
        </div>
      </footer>
    </div>
  `,
  styles: [`
    :host {
      display: block;
      height: 100%;
    }
    
    /* Ensure the deck view can be centered and scaled if needed */
    app-deck-view {
      transform-origin: center center;
    }

    .glass-container {
      background: var(--mat-sys-surface-container-low);
    }
    
    .glass-header {
      background: color-mix(in srgb, var(--mat-sys-surface-container) 85%, transparent);
      backdrop-filter: blur(12px);
      -webkit-backdrop-filter: blur(12px);
    }

    .glass-footer {
      background: color-mix(in srgb, var(--mat-sys-surface-container) 90%, transparent);
      backdrop-filter: blur(12px);
      -webkit-backdrop-filter: blur(12px);
    }
  `],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class MachineFocusViewComponent {
  @Input({ required: true }) machine!: MachineWithRuntime;
  back = output<void>();

  selectedResource = signal<PlrResourceDetails | undefined>(undefined);

  statusClass(): string {
    const status = this.machine.status.toLowerCase();
    switch (status) {
      case 'idle': return 'text-emerald-600 dark:text-emerald-400';
      case 'running': return 'text-primary';
      case 'error': return 'text-rose-600 dark:text-rose-400';
      default: return 'text-slate-500';
    }
  }

  onResourceSelected(details: PlrResourceDetails) {
    this.selectedResource.set(details);
  }

  @HostListener('window:keydown.escape')
  onEscapePressed() {
    this.back.emit();
  }
}