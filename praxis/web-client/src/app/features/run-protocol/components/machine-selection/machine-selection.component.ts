
import { Component, ChangeDetectionStrategy, input, output, computed } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatTooltipModule } from '@angular/material/tooltip';
import { MatCardModule } from '@angular/material/card';

export interface MachineCompatibility {
    machine: {
        accession_id: string;
        name: string;
        machine_type: string;
    };
    compatibility: {
        is_compatible: boolean;
        missing_capabilities: any[];
        matched_capabilities: string[];
        warnings: string[];
    };
}

@Component({
    selector: 'app-machine-selection',
    standalone: true,
    imports: [
        CommonModule,
        MatButtonModule,
        MatIconModule,
        MatTooltipModule,
        MatCardModule
    ],
    template: `
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      @for (item of machines(); track item.machine.accession_id) {
        <div
          class="relative bg-surface-elevated border rounded-2xl p-6 cursor-pointer transition-all duration-200 group hover:-translate-y-1 hover:shadow-lg"
          [class.border-white-10]="!selected() || selected()?.machine?.accession_id !== item.machine.accession_id"
          [class.border-primary]="selected()?.machine?.accession_id === item.machine.accession_id"
          [class.bg-primary-05]="selected()?.machine?.accession_id === item.machine.accession_id"
          [class.opacity-60]="!item.compatibility.is_compatible"
          (click)="selectMachine(item)"
        >
          <!-- Status Icon -->
          <div class="absolute top-4 right-4">
            @if (item.compatibility.is_compatible) {
              @if (item.compatibility.warnings.length > 0) {
                 <mat-icon class="text-amber-400" matTooltip="Compatible with warnings">warning</mat-icon>
              } @else {
                 <mat-icon class="text-green-400">check_circle</mat-icon>
              }
            } @else {
              <mat-icon class="text-red-400" [matTooltip]="getIncompatibleReason(item)">error</mat-icon>
            }
          </div>

          <div class="flex flex-col gap-2">
            <h3 class="text-lg font-bold text-sys-text-primary">{{ item.machine.name }}</h3>
            <span class="text-xs uppercase tracking-wider text-sys-text-tertiary">{{ item.machine.machine_type }}</span>

            @if (!item.compatibility.is_compatible) {
              <div class="mt-4 p-3 bg-red-400/10 rounded-lg border border-red-400/20">
                <p class="text-sm text-red-400 font-medium mb-1">Incompatible</p>
                <ul class="text-xs text-red-400/70 list-disc pl-4 space-y-1">
                  @for (missing of item.compatibility.missing_capabilities; track missing.capability_name) {
                     <li>Missing: {{ missing.capability_name }}</li>
                  }
                </ul>
              </div>
            } @else if (item.compatibility.warnings.length > 0) {
               <div class="mt-4 p-3 bg-amber-400/10 rounded-lg border border-amber-400/20">
                <p class="text-sm text-amber-500 font-medium mb-1">Warnings</p>
                <ul class="text-xs text-amber-600/70 list-disc pl-4 space-y-1">
                  @for (warn of item.compatibility.warnings; track warn) {
                     <li>{{ warn }}</li>
                  }
                </ul>
              </div>
            }
          </div>
        </div>
      }
    </div>
    
    @if (machines().length === 0) {
      <div class="flex flex-col items-center justify-center py-12 opacity-50 text-sys-text-tertiary">
        <mat-icon class="!w-12 !h-12 !text-[48px] mb-4">desktop_access_disabled</mat-icon>
        <p>No machines found.</p>
      </div>
    }
  `,
    styles: [`
    .border-white-10 { border-color: var(--theme-border); }
    .bg-primary-05 { background-color: rgba(var(--primary-color-rgb), 0.05); }
  `],
    changeDetection: ChangeDetectionStrategy.OnPush,
})
export class MachineSelectionComponent {
    machines = input<MachineCompatibility[]>([]);
    selected = input<MachineCompatibility | null>(null);

    select = output<MachineCompatibility>();

    selectMachine(item: MachineCompatibility) {
        if (item.compatibility.is_compatible) {
            this.select.emit(item);
        }
    }

    getIncompatibleReason(item: MachineCompatibility): string {
        return item.compatibility.missing_capabilities
            .map(m => `Missing ${m.capability_name}`)
            .join(', ');
    }
}
