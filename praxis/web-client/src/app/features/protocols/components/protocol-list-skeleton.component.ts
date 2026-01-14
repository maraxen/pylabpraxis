import { Component, Input } from '@angular/core';


@Component({
  selector: 'app-protocol-list-skeleton',
  standalone: true,
  imports: [],
  template: `
    <div class="skeleton-table w-full">
      @for (i of [].constructor(rows); track i) {
        <div class="skeleton-row">
          @for (j of [].constructor(cols); track j) {
            <div class="skeleton-cell">
              <div class="skeleton-bar"></div>
            </div>
          }
        </div>
      }
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
      border-bottom: 1px solid var(--mat-sys-outline-variant);
    }

    .skeleton-bar {
      width: 100%;
      height: 20px;
      background: linear-gradient(
        to right,
        var(--mat-sys-surface-container) 0%,
        var(--mat-sys-surface-container-high) 20%,
        var(--mat-sys-surface-container) 40%,
        var(--mat-sys-surface-container) 100%
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
