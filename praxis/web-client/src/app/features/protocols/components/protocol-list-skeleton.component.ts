import { Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
    selector: 'app-protocol-list-skeleton',
    standalone: true,
    imports: [CommonModule],
    template: `
    <div class="skeleton-table w-full">
      <div class="skeleton-row" *ngFor="let i of [].constructor(rows)">
        <div class="skeleton-cell" *ngFor="let j of [].constructor(cols)">
          <div class="skeleton-bar"></div>
        </div>
      </div>
    </div>
  `,
    styles: [`
    @keyframes shimmer {
      0% { background-position: -200px 0; }
      100% { background-position: calc(200px + 100%) 0; }
    }

    .skeleton-table {
      display: table;
      border-collapse: collapse;
    }

    .skeleton-row {
      display: table-row;
    }

    .skeleton-cell {
      display: table-cell;
      padding: 1rem;
      border-bottom: 1px solid var(--mat-sys-outline-variant, #e0e0e0);
    }

    .skeleton-bar {
      width: 100%;
      height: 20px;
      background: linear-gradient(
        to right,
        var(--mat-sys-surface-container, #f6f7f8) 0%,
        var(--mat-sys-surface-container-high, #edeef1) 20%,
        var(--mat-sys-surface-container, #f6f7f8) 40%,
        var(--mat-sys-surface-container, #f6f7f8) 100%
      );
      background-size: 200px 100%;
      animation: shimmer 1.5s infinite;
      border-radius: 4px;
    }
  `]
})
export class ProtocolListSkeletonComponent {
    @Input() rows = 5;
    @Input() cols = 4;
}
