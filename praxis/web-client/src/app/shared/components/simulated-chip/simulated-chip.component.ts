import { Component, ChangeDetectionStrategy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatIconModule } from '@angular/material/icon';

@Component({
    selector: 'app-simulated-chip',
    standalone: true,
    imports: [CommonModule, MatIconModule],
    template: `
    <div class="flex items-center gap-1.5 px-2 py-1 rounded bg-blue-500/10 border border-blue-500/20 text-[10px] font-bold text-blue-400 uppercase tracking-wider w-fit select-none">
      <mat-icon class="!w-3 !h-3 !text-[12px]">vibration</mat-icon>
      Simulated
    </div>
  `,
    styles: [],
    changeDetection: ChangeDetectionStrategy.OnPush,
})
export class SimulatedChipComponent { }
