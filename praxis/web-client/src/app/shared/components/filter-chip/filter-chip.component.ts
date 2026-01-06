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
    templateUrl: './filter-chip.component.html',
    styleUrls: ['./filter-chip.component.scss'],
    changeDetection: ChangeDetectionStrategy.OnPush
})
export class FilterChipComponent {
    @Input() label: string = '';
    @Input() options: FilterOption[] = [];
    @Input() selectedValue: any = null;
    @Input() disabled: boolean = false;
    @Input() resultCount: number | null = null;

    @Output() selectionChange = new EventEmitter<any>();

    @ViewChild(MatMenuTrigger) menuTrigger?: MatMenuTrigger;

    isShaking = false;

    get isActive(): boolean {
        return this.selectedValue !== null && this.selectedValue !== undefined && this.selectedValue !== '';
    }

    get displayLabel(): string {
        if (this.isActive) {
            const selected = this.options.find(o => o.value === this.selectedValue);
            if (selected) {
                return `${this.label}: ${selected.label}`;
            }
        }
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
        this.selectionChange.emit(value);
    }
}
