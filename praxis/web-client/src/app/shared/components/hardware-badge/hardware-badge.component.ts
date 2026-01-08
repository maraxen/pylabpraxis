import { Component, ChangeDetectionStrategy, input } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatIconModule } from '@angular/material/icon';

@Component({
  selector: 'app-hardware-badge',
  standalone: true,
  imports: [CommonModule, MatIconModule],
  template: `
    <div 
      class="flex items-center gap-1.5 px-3 py-1.5 rounded-full border text-[11px] font-extrabold uppercase tracking-widest w-fit select-none backdrop-blur-md shadow-sm"
      [ngClass]="isSimulated() ? 'bg-blue-400/20 border-blue-400/40 text-blue-400' : 'bg-green-400/20 border-green-400/40 text-green-400'"
    >
      <mat-icon class="!w-3 !h-3 !text-[12px]">
        {{ isSimulated() ? 'vibration' : 'precision_manufacturing' }}
      </mat-icon>
      {{ isSimulated() ? 'Simulated' : 'Physical' }}
    </div>
  `,
  styles: [],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class HardwareBadgeComponent {
  isSimulated = input<boolean>(false);
}
