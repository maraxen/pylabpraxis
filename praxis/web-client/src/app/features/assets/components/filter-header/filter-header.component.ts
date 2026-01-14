import { Component, ChangeDetectionStrategy, input, output, signal, effect } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatIconModule } from '@angular/material/icon';
import { MatButtonModule } from '@angular/material/button';
import { MatExpansionModule } from '@angular/material/expansion';
import { ReactiveFormsModule, FormControl } from '@angular/forms';
import { debounceTime, distinctUntilChanged } from 'rxjs/operators';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';

@Component({
  selector: 'app-filter-header',
  standalone: true,
  imports: [
    CommonModule,
    MatFormFieldModule,
    MatInputModule,
    MatIconModule,
    MatButtonModule,
    MatExpansionModule,
    ReactiveFormsModule
  ],
  template: `
    <div class="tab-header">
      <!-- Search Bar -->
      <mat-form-field appearance="outline" class="search-field praxis-search-field">
        <mat-icon matPrefix>search</mat-icon>
        <input matInput [placeholder]="searchPlaceholder()"
               [formControl]="searchControl">
        @if (searchControl.value) {
          <button mat-icon-button matSuffix (click)="searchControl.reset()">
            <mat-icon>close</mat-icon>
          </button>
        }
      </mat-form-field>

      <!-- Filter Accordion -->
      <mat-expansion-panel class="filter-panel" [expanded]="filterExpanded()">
        <mat-expansion-panel-header>
          <mat-panel-title>
            <mat-icon>filter_list</mat-icon>
            Filters
            @if (filterCount() > 0) {
              <span class="filter-badge">{{ filterCount() }}</span>
              <button mat-button class="clear-btn" (click)="$event.stopPropagation(); clearFilters.emit()">
                Clear
              </button>
            }
          </mat-panel-title>
        </mat-expansion-panel-header>

        <div class="filter-content">
          <ng-content select="[filterContent]"></ng-content>
        </div>
      </mat-expansion-panel>
    </div>
  `,
  styles: [`
    .tab-header {
      position: sticky;
      top: 0;
      z-index: 100;
      background: var(--mat-sys-surface);
      padding: 16px;
      display: flex;
      flex-direction: column;
      gap: 12px;
      border-bottom: 1px solid var(--mat-sys-outline-variant);
      box-shadow: 0 4px 12px rgba(0,0,0,0.05);
      border-bottom-left-radius: 12px;
      border-bottom-right-radius: 12px;
    }

    .search-field {
      width: 100%;
    }
    
    :host ::ng-deep .praxis-search-field .mat-mdc-text-field-wrapper {
        background-color: var(--mat-sys-surface) !important;
    }

    .filter-panel {
      background: var(--mat-sys-surface);
      border-radius: 12px !important;
      box-shadow: none !important;
      border: 1px solid var(--mat-sys-outline-variant);
    }
    
    ::ng-deep .filter-panel .mat-expansion-panel-header {
        height: 48px !important;
        padding: 0 16px !important;
    }
    
    mat-panel-title {
        display: flex;
        align-items: center;
        gap: 8px;
        font-size: 14px;
        font-weight: 500;
        color: var(--mat-sys-on-surface);
    }

    .filter-badge {
      background: var(--mat-sys-primary);
      color: var(--mat-sys-on-primary);
      border-radius: 12px;
      padding: 0 8px;
      height: 20px;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 11px;
      font-weight: 700;
      margin-left: auto;
    }

    .clear-btn {
      margin-left: 8px;
      height: 24px;
      line-height: 24px;
      font-size: 12px;
      padding: 0 8px;
      min-width: unset;
      color: var(--mat-sys-primary);
    }
    
    .filter-content {
        padding-top: 16px;
    }
  `],
  changeDetection: ChangeDetectionStrategy.OnPush
})
export class FilterHeaderComponent {
  searchPlaceholder = input<string>('Search...');
  filterCount = input<number>(0);
  searchValue = input<string>('');

  searchChange = output<string>();
  clearFilters = output<void>();

  searchControl = new FormControl('');
  filterExpanded = signal(false);

  constructor() {
    effect(() => {
      const val = this.searchValue();
      if (this.searchControl.value !== val) {
        this.searchControl.setValue(val, { emitEvent: false });
      }
    });

    this.searchControl.valueChanges.pipe(
      takeUntilDestroyed(),
      debounceTime(300),
      distinctUntilChanged()
    ).subscribe(value => {
      this.searchChange.emit(value || '');
    });
  }
}
