import { Component, Input, Output, EventEmitter, ChangeDetectionStrategy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatButtonToggleModule } from '@angular/material/button-toggle';
import { MatIconModule } from '@angular/material/icon';
import { MatTooltipModule } from '@angular/material/tooltip';
import { ViewType } from './view-controls.types';

@Component({
    selector: 'app-view-type-toggle',
    standalone: true,
    imports: [CommonModule, MatButtonToggleModule, MatIconModule, MatTooltipModule],
    template: `
    <mat-button-toggle-group [value]="viewType" (change)="onViewTypeChange($event.value)" aria-label="View Type">
      @if (availableTypes.includes('card')) {
        <mat-button-toggle value="card" matTooltip="Grid View">
          <mat-icon>grid_view</mat-icon>
        </mat-button-toggle>
      }
      @if (availableTypes.includes('list')) {
        <mat-button-toggle value="list" matTooltip="List View">
          <mat-icon>view_list</mat-icon>
        </mat-button-toggle>
      }
      @if (availableTypes.includes('table')) {
        <mat-button-toggle value="table" matTooltip="Table View">
          <mat-icon>table_chart</mat-icon>
        </mat-button-toggle>
      }
    </mat-button-toggle-group>
  `,
    styles: [`
    :host {
      display: block;
    }
    mat-button-toggle-group {
      height: 32px;
      align-items: center;
      border: 1px solid var(--theme-border);
      background-color: transparent;
    }
    mat-button-toggle {
      background-color: transparent;
      color: var(--theme-text-secondary);
      
      &.mat-button-toggle-checked {
        background-color: var(--theme-surface-elevated);
        color: var(--primary-color);
      }
      
      .mat-icon {
        font-size: 18px;
        width: 18px;
        height: 18px;
      }
    }
  `],
    changeDetection: ChangeDetectionStrategy.OnPush
})
export class ViewTypeToggleComponent {
    @Input() viewType: ViewType = 'card';
    @Input() availableTypes: ViewType[] = ['card', 'list', 'table'];
    @Output() viewTypeChange = new EventEmitter<ViewType>();

    onViewTypeChange(value: ViewType) {
        this.viewTypeChange.emit(value);
    }
}
