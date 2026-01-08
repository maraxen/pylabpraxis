import { Component, Input, Output, EventEmitter, ChangeDetectionStrategy, ViewChild } from '@angular/core';

import { MatMenuModule, MatMenuTrigger } from '@angular/material/menu';
import { MatIconModule } from '@angular/material/icon';
import { MatTooltipModule } from '@angular/material/tooltip';
import { FilterOption } from '../../services/filter-result.service';

@Component({
    selector: 'app-filter-chip',
    standalone: true,
    imports: [
        MatMenuModule,
        MatIconModule,
        MatTooltipModule
    ],
    template: `
<div class="filter-chip" [class.active]="isActive" [class.disabled]="disabled" [class.shake]="isShaking"
  [matTooltip]="disabled ? 'No results match this filter combination' : ''" [matMenuTriggerFor]="disabled ? null : menu"
  (click)="onChipClick($event)" tabindex="0" role="button" [attr.aria-disabled]="disabled" [attr.aria-label]="label">

  <span class="chip-text">{{ displayLabel }}</span>
  <mat-icon class="chip-chevron">expand_more</mat-icon>
</div>

<mat-menu #menu="matMenu" class="filter-chip-menu">
  <div class="menu-options-container" (click)="$event.stopPropagation()">
    <button mat-menu-item (click)="selectOption(null)" class="filter-option" [class.selected]="!isActive">
      <div class="option-content">
        <div class="option-label-wrapper">
          @if (multiple) {
          <mat-icon>{{ !isActive ? 'check_box' : 'check_box_outline_blank' }}</mat-icon>
          }
          <span [class.font-bold]="!isActive">All</span>
        </div>
      </div>
    </button>

    @for (option of options; track option.value) {
    <button mat-menu-item [disabled]="option.disabled" (click)="!option.disabled && selectOption(option.value)"
      class="filter-option" [class.selected]="isSelected(option.value)">
      <div class="option-content">
        <div class="option-label-wrapper">
          @if (multiple) {
          <mat-icon>{{ isSelected(option.value) ? 'check_box' : 'check_box_outline_blank' }}</mat-icon>
          }
          <span [class.font-bold]="isSelected(option.value)">{{ option.label }}</span>
        </div>

        @if (option.disabled) {
        <span class="option-count">(0)</span>
        } @else if (option.count !== undefined) {
        <span class="option-count">({{ option.count }})</span>
        }
      </div>
    </button>
    }
  </div>
</mat-menu>
    `,
    styles: [`
:host {
    display: inline-block;
    outline: none;
}

.filter-chip {
    display: flex;
    align-items: center;
    justify-content: space-between;
    height: 32px;
    padding: 0 12px;
    border-radius: 16px;
    border: 1px solid var(--theme-border);
    background-color: transparent;
    color: var(--theme-text-primary);
    cursor: pointer;
    transition: all 0.2s ease;
    user-select: none;
    font-size: 13px;
    font-weight: 500;
    max-width: 250px;

    /* Text handling */
    .chip-text {
        margin-right: 4px;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }

    .chip-chevron {
        font-size: 18px;
        width: 18px;
        height: 18px;
        display: flex;
        align-items: center;
        justify-content: center;
        opacity: 0.7;
        flex-shrink: 0;
    }

    /* Hover State (Inactive) */
    &:hover:not(.disabled):not(.active) {
        background-color: var(--theme-surface-elevated);
        border-color: var(--theme-text-secondary);
    }

    /* Active State (Filled) */
    &.active {
        background-color: var(--primary-color);
        border-color: var(--primary-color);
        color: #2b151a;
        /* Dark text for contrast against Rose Pompadour */

        .chip-chevron {
            opacity: 1;
        }

        &:hover:not(.disabled) {
            filter: brightness(1.1);
        }
    }

    /* Disabled State */
    &.disabled {
        cursor: not-allowed;
        border: 1px dashed var(--theme-border);
        background-color: var(--theme-surface);
        opacity: 0.5;

        /* We handle the shake separately via class */
    }

    /* Shake Animation Class */
    &.shake {
        animation: shake 0.3s cubic-bezier(.36, .07, .19, .97) both;
    }
}

/* Animation Keyframes */
@keyframes shake {

    10%,
    90% {
        transform: translate3d(-1px, 0, 0);
    }

    20%,
    80% {
        transform: translate3d(2px, 0, 0);
    }

    30%,
    50%,
    70% {
        transform: translate3d(-4px, 0, 0);
    }

    40%,
    60% {
        transform: translate3d(4px, 0, 0);
    }
}

/* Menu Customization helpers */
::ng-deep .filter-chip-menu {
    max-height: 400px;
    overflow-y: auto;

    .menu-options-container {
        display: flex;
        flex-direction: column;
        min-width: 180px;
    }

    .option-content {
        display: flex;
        justify-content: space-between;
        align-items: center;
        width: 100%;
        gap: 16px;
    }

    .option-label-wrapper {
        display: flex;
        align-items: center;
        gap: 8px;
        flex: 1;

        .mat-icon {
            font-size: 18px;
            width: 18px;
            height: 18px;
        }
    }

    .option-count {
        font-size: 0.85em;
        opacity: 0.6;
    }

    .filter-option.selected {
        background-color: var(--theme-surface-elevated);
        color: var(--primary-color);

        .option-count {
            color: var(--theme-text-primary);
        }
    }
}
    `],
    changeDetection: ChangeDetectionStrategy.OnPush
})
export class FilterChipComponent {
    @Input() label: string = '';
    @Input() options: FilterOption[] = [];
    @Input() selectedValue: any | any[] = null;
    @Input() disabled: boolean = false;
    @Input() resultCount: number | null = null;
    @Input() multiple: boolean = false;

    @Output() selectionChange = new EventEmitter<any>();

    @ViewChild(MatMenuTrigger) menuTrigger?: MatMenuTrigger;

    isShaking = false;

    get isActive(): boolean {
        if (this.multiple) {
            return Array.isArray(this.selectedValue) && this.selectedValue.length > 0;
        }
        return this.selectedValue !== null && this.selectedValue !== undefined && this.selectedValue !== '';
    }

    get displayLabel(): string {
        // PER USER FEEDBACK: Keep base label, but the presence of .active class 
        // (handled in template) will show it is filtered.
        return this.label;
    }

    onChipClick(event: MouseEvent) {
        if (this.disabled) {
            event.stopPropagation();
            this.triggerShake();
        }
    }

    triggerShake() {
        this.isShaking = true;
        setTimeout(() => this.isShaking = false, 300); // 300ms matches CSS animation
    }

    selectOption(value: any) {
        if (this.multiple) {
            const CURRENT = Array.isArray(this.selectedValue) ? [...this.selectedValue] : [];
            if (value === null) {
                // "All" selected -> clear selection
                this.selectionChange.emit([]);
            } else {
                const INDEX = CURRENT.indexOf(value);
                if (INDEX > -1) {
                    CURRENT.splice(INDEX, 1);
                } else {
                    CURRENT.push(value);
                }
                this.selectionChange.emit(CURRENT);
            }
        } else {
            this.selectionChange.emit(value);
        }
    }

    isSelected(value: any): boolean {
        if (this.multiple) {
            return Array.isArray(this.selectedValue) && this.selectedValue.includes(value);
        }
        return this.selectedValue === value;
    }
}
