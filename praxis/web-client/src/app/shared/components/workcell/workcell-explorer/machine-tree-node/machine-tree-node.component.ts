import { Component, output, ChangeDetectionStrategy, Input, signal, input } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MachineWithRuntime } from '@features/workcell/models/workcell-view.models';

@Component({
  selector: 'app-machine-tree-node',
  imports: [CommonModule],
  template: `
    <div 
      class="group flex items-center gap-3 rounded-md px-2 py-2 text-sm font-medium text-sys-text-secondary hover:bg-[var(--mat-sys-surface-variant)] hover:text-sys-text-primary cursor-pointer transition-colors"
      (click)="onSelect()"
      [class.bg-[var(--mat-sys-primary-container)]]="isSelected()"
      [class.text-primary]="isSelected()"
    >
      <!-- Status Dot (Placeholder for P1.3 Badge) -->
      <span class="relative flex h-2.5 w-2.5">
        @if (machine().connectionState === 'connected') {
          <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-[var(--mat-sys-success)] opacity-75"></span>
          <span class="relative inline-flex rounded-full h-2.5 w-2.5 bg-[var(--mat-sys-success)]"></span>
        } @else {
          <span class="relative inline-flex rounded-full h-2.5 w-2.5 bg-sys-text-tertiary"></span>
        }
      </span>

      <!-- Name -->
      <span class="truncate flex-grow">{{ machine().name }}</span>

      <!-- Type/Icon (Optional) -->
      <span class="text-xs text-sys-text-tertiary opacity-0 group-hover:opacity-100 transition-opacity">
        {{ machine().machine_type }}
      </span>
    </div>
  `,
  styles: [`:host { display: block; }`],
  changeDetection: ChangeDetectionStrategy.OnPush
})
export class MachineTreeNodeComponent {
  machine = input.required<MachineWithRuntime>();
  isSelected = input<boolean>(false);
  
  machineSelect = output<MachineWithRuntime>();

  onSelect() {
    this.machineSelect.emit(this.machine());
  }
}
