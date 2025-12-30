import { Component, Input, computed } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatIconModule } from '@angular/material/icon';

@Component({
    selector: 'app-location-breadcrumb',
    standalone: true,
    imports: [CommonModule, MatIconModule],
    template: `
    <div class="breadcrumb-container" *ngIf="parts().length > 0; else noLocation">
      <div *ngFor="let part of parts(); let last = last" class="breadcrumb-item">
        <span class="part-text" [class.last]="last" [title]="part">{{ part }}</span>
        <mat-icon *ngIf="!last" class="separator">chevron_right</mat-icon>
      </div>
    </div>
    <ng-template #noLocation>
      <span class="no-location">Unassigned</span>
    </ng-template>
  `,
    styles: [`
    .breadcrumb-container {
      display: flex;
      align-items: center;
      flex-wrap: wrap;
      gap: 2px;
      font-size: 0.85rem;
      color: var(--mat-sys-on-surface-variant);
    }

    .breadcrumb-item {
      display: flex;
      align-items: center;
    }

    .part-text {
      white-space: nowrap;
      max-width: 150px;
      overflow: hidden;
      text-overflow: ellipsis;
      cursor: default;
    }

    .part-text:hover {
      color: var(--mat-sys-primary);
    }

    .part-text.last {
      font-weight: 500;
      color: var(--mat-sys-on-surface);
    }

    .separator {
      font-size: 16px;
      height: 16px;
      width: 16px;
      color: var(--mat-sys-outline);
      margin: 0 1px;
    }

    .no-location {
      font-style: italic;
      color: var(--mat-sys-outline);
      font-size: 0.8rem;
    }
  `]
})
export class LocationBreadcrumbComponent {
    @Input() location: string | undefined;

    parts = computed(() => {
        if (!this.location) return [];
        // Split by common delimiters: /, >, ->, or just space-around-slash
        return this.location.split(/\/| > | -> |>|->/g).map(s => s.trim()).filter(Boolean);
    });
}
