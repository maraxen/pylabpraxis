import { Component, EventEmitter, Output } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatDividerModule } from '@angular/material/divider';
import { QuickAddAutocompleteComponent, QuickAddResult } from '../../../components/quick-add-autocomplete/quick-add-autocomplete.component';

@Component({
  selector: 'app-type-selection-step',
  standalone: true,
  imports: [
    CommonModule,
    MatButtonModule,
    MatIconModule,
    MatDividerModule,
    QuickAddAutocompleteComponent
  ],
  template: `
    <div class="flex flex-col gap-5 py-4">
      <div>
        <h3 class="text-lg font-medium mb-3">What would you like to add?</h3>
        
        <div class="mb-8">
          <app-quick-add-autocomplete
            (definitionSelected)="onQuickSelect($event)"
          ></app-quick-add-autocomplete>
        </div>

        <div class="relative flex items-center mb-8">
          <div class="flex-grow border-t sys-border"></div>
          <span class="flex-shrink mx-4 text-xs font-bold uppercase tracking-widest text-sys-text-primary">or browse by category</span>
          <div class="flex-grow border-t sys-border"></div>
        </div>
        
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <button
            type="button"
            class="selection-card h-auto !p-6 flex flex-col items-center gap-3 text-center transition-all"
            (click)="onSelect('machine')"
          >
            <div class="icon-chip large">
              <mat-icon class="!w-10 !h-10 !text-[40px]">precision_manufacturing</mat-icon>
            </div>
            <div class="flex flex-col items-center">
              <span class="font-bold text-lg">Machine</span>
              <span class="text-xs sys-text-secondary">Robots, liquid handlers, plate readers, etc.</span>
            </div>
          </button>
Index-based paging - skipping lines...
          <button
            type="button"
            class="selection-card h-auto !p-6 flex flex-col items-center gap-3 text-center transition-all"
            (click)="onSelect('resource')"
          >
            <div class="icon-chip large">
              <mat-icon class="!w-10 !h-10 !text-[40px]">science</mat-icon>
            </div>
            <div class="flex flex-col items-center">
              <span class="font-bold text-lg">Resource</span>
              <span class="text-xs sys-text-secondary">Plates, tips, labware, consumables</span>
            </div>
          </button>
        </div>
      </div>
    </div>
  `,
  styles: [`
    .selection-card {
      border: 1px solid var(--mat-sys-outline-variant);
      border-radius: 16px;
      background: linear-gradient(135deg, var(--mat-sys-surface) 0%, var(--mat-sys-surface-container-low) 100%);
      cursor: pointer;
    }
    .selection-card:hover {
      border-color: var(--mat-sys-primary);
      box-shadow: 0 8px 24px -12px var(--mat-sys-primary);
      transform: translateY(-2px);
    }
    .icon-chip.large {
      width: 64px;
      height: 64px;
      border-radius: 16px;
      background: var(--mat-sys-surface-container-high);
      display: grid;
      place-items: center;
      color: var(--mat-sys-primary);
    }
    .sys-text-secondary {
      color: var(--mat-sys-on-surface-variant) !important;
    }
    .sys-text-primary {
      color: var(--mat-sys-on-surface) !important;
    }
    .sys-border {
      border-color: var(--mat-sys-outline-variant);
    }
  `]
})
export class TypeSelectionStepComponent {
  @Output() typeSelected = new EventEmitter<'machine' | 'resource'>();
  @Output() quickSelect = new EventEmitter<QuickAddResult>();

  onSelect(type: 'machine' | 'resource') {
    this.typeSelected.emit(type);
  }

  onQuickSelect(result: QuickAddResult) {
    this.quickSelect.emit(result);
  }
}
