import { Component, ChangeDetectionStrategy, input, output } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatIconModule } from '@angular/material/icon';
import { MatButtonModule } from '@angular/material/button';
import { MatTooltipModule } from '@angular/material/tooltip';
import { Machine } from '../../../features/assets/models/asset.models';
import { MachineCompatibility } from '../../../features/run-protocol/components/machine-selection/machine-selection.component';
import { SimulatedChipComponent } from '../simulated-chip/simulated-chip.component';

@Component({
    selector: 'app-machine-card',
    standalone: true,
    imports: [
        CommonModule,
        MatIconModule,
        MatButtonModule,
        MatTooltipModule,
        SimulatedChipComponent
    ],
    template: `
    <div
      class="relative bg-surface-elevated border rounded-2xl p-6 cursor-pointer transition-all duration-200 group hover:-translate-y-1 hover:shadow-lg h-full"
      [class.border-white-10]="!selected()"
      [class.border-primary]="selected()"
      [class.bg-primary-05]="selected()"
      [class.opacity-60]="machineCompatibility() && !machineCompatibility()?.compatibility?.is_compatible"
      [class.opacity-40]="isPhysicalMode() && isSimulated()"
      [class.grayscale]="isPhysicalMode() && isSimulated()"
      (click)="onClick()"
    >
      <!-- Simulated Chip -->
      @if (isSimulated()) {
         <div class="mb-2">
           <app-simulated-chip />
         </div>
      }

      <h3 class="text-lg font-bold text-sys-text-primary">{{ getMachine().name }}</h3>
      <span class="text-xs uppercase tracking-wider text-sys-text-tertiary">{{ getMachine().machine_type }}</span>

      <!-- Compatibility Info -->
      @if (machineCompatibility()) {
        @if (!machineCompatibility()?.compatibility?.is_compatible) {
          <div class="mt-4 p-3 bg-red-400/10 rounded-lg border border-red-400/20">
            <p class="text-sm text-red-400 font-medium mb-1">Incompatible</p>
            <ul class="text-xs text-red-400/70 list-disc pl-4 space-y-1">
              @for (missing of machineCompatibility()!.compatibility.missing_capabilities; track missing.capability_name) {
                 <li>Missing: {{ missing.capability_name }}</li>
              }
            </ul>
          </div>
        } @else if (machineCompatibility()!.compatibility.warnings.length > 0) {
           <div class="mt-4 p-3 bg-amber-400/10 rounded-lg border border-amber-400/20">
            <p class="text-sm text-amber-500 font-medium mb-1">Warnings</p>
            <ul class="text-xs text-amber-600/70 list-disc pl-4 space-y-1">
              @for (warn of machineCompatibility()!.compatibility.warnings; track warn) {
                 <li>{{ warn }}</li>
              }
            </ul>
          </div>
        }
      }

      <!-- Physical Mode Warning -->
      @if (isPhysicalMode() && isSimulated()) {
        <div class="mt-4 p-3 bg-red-400/10 rounded-lg border border-red-400/20">
          <p class="text-sm text-red-400 font-medium">Not available for Physical mode</p>
        </div>
      }
    </div>
  `,
    styles: [`
    .border-white-10 { border-color: var(--theme-border, rgba(255,255,255,0.1)); }
    .bg-primary-05 { background-color: rgba(var(--primary-color-rgb, 99, 102, 241), 0.05); }
    .border-primary { border-color: var(--sys-primary, #6366f1); }
  `],
    changeDetection: ChangeDetectionStrategy.OnPush,
})
export class MachineCardComponent {
    // Inputs can be either a straight Machine or the Compatibility wrapper
    machine = input<Machine | null>(null);
    machineCompatibility = input<MachineCompatibility | null>(null);

    selected = input<boolean>(false);
    isPhysicalMode = input<boolean>(false);

    cardClick = output<void>();

    getMachine(): Machine {
        if (this.machine()) return this.machine()!;
        if (this.machineCompatibility()) return this.machineCompatibility()!.machine;
        throw new Error('MachineCard must provide either machine or machineCompatibility input');
    }

    isSimulated(): boolean {
        const m = this.getMachine();
        if (!m) return false;

        const connectionInfo = m.connection_info || {};
        const backend = (connectionInfo['backend'] || '').toString();

        return m.is_simulation_override === true ||
            (m as any).is_simulated === true ||
            backend.includes('Simulator');
    }

    onClick() {
        this.cardClick.emit();
    }
}
