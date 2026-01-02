import { Component, Input, computed, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { MatIconModule } from '@angular/material/icon';
import { toSignal } from '@angular/core/rxjs-interop';
import { BreadcrumbService, Breadcrumb } from '../../services/breadcrumb.service';

@Component({
    selector: 'app-breadcrumb',
    standalone: true,
    imports: [CommonModule, RouterModule, MatIconModule],
    template: `
    <nav aria-label="Breadcrumb" class="flex items-center text-sm text-sys-text-tertiary">
      <ng-container *ngFor="let item of breadcrumbs(); let last = last">
        <div class="flex items-center">
          <ng-container *ngIf="!last && item.url">
            <a [routerLink]="item.url" class="hover:text-primary transition-colors hover:underline decoration-1 underline-offset-4">
              {{ item.label }}
            </a>
          </ng-container>
          <span *ngIf="last || !item.url" [class.font-semibold]="last" [class.text-sys-text-primary]="last">
            {{ item.label }}
          </span>
          <mat-icon *ngIf="!last" class="mx-2 !w-4 !h-4 !text-[16px] overflow-visible text-sys-text-tertiary">chevron_right</mat-icon>
        </div>
      </ng-container>
    </nav>
  `,
    styles: [`
    :host {
      display: block;
    }
  `]
})
export class BreadcrumbComponent {
    private breadcrumbService = inject(BreadcrumbService);

    /** Manually provided items (overrides service) */
    @Input() items: Breadcrumb[] | null = null;

    /** Location string mode (e.g. "Room > Shelf") */
    @Input() locationString: string | null = null;

    readonly serviceBreadcrumbs = toSignal(this.breadcrumbService.breadcrumbs$);

    readonly breadcrumbs = computed(() => {
        if (this.items) return this.items;
        if (this.locationString) {
            return this.locationString.split(/\/| > | -> |>|->/g)
                .map(s => s.trim())
                .filter(Boolean)
                .map(label => ({ label, url: '' }));
        }
        return this.serviceBreadcrumbs() || [];
    });
}
