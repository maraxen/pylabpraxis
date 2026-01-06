
import { Component, ChangeDetectionStrategy, input, output, computed } from '@angular/core';
import { MachineCardComponent } from '@shared/components/machine-card/machine-card.component';

import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatTooltipModule } from '@angular/material/tooltip';
import { MatCardModule } from '@angular/material/card';

import { Machine } from '../../../assets/models/asset.models';

export interface MachineCompatibility {
  machine: Machine;
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
    MatButtonModule,
    MatIconModule,
    MatTooltipModule,
    MatCardModule,
    MachineCardComponent
],
  template: `
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      @for (item of machines(); track item.machine.accession_id) {
        <app-machine-card
          [machineCompatibility]="item"
          [selected]="selected()?.machine?.accession_id === item.machine.accession_id"
          [isPhysicalMode]="isPhysicalMode()"
          (cardClick)="selectMachine(item)"
        />
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
  `],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class MachineSelectionComponent {
  machines = input<MachineCompatibility[]>([]);
  selected = input<MachineCompatibility | null>(null);
  isPhysicalMode = input<boolean>(false);

  select = output<MachineCompatibility>();

  selectMachine(item: MachineCompatibility) {
    // Check compatibility before selecting
    // If physical mode, check if not simulated (validation logic usually here or parental)
    // Here we let the parent handle strict blocking or check 'compatible' flag
    if (item.compatibility.is_compatible) {
      // Also block if physical mode and machine is simulated?
      // The previous UI logic blocked clicks or showed disabled states.
      // The card itself shows visual disabled state but emits click.
      // We enforce the check here:
      if (this.isPhysicalMode() && this.isSimulated(item.machine)) {
        return;
      }
      this.select.emit(item);
    }
  }

  // Helper also used internally for logic check
  private isSimulated(machine: Machine): boolean {
    const connectionInfo = machine.connection_info || {};
    const backend = (connectionInfo['backend'] || '').toString();

    return machine.is_simulation_override === true ||
      (machine as any).is_simulated === true ||
      backend.includes('Simulator');
  }
}
