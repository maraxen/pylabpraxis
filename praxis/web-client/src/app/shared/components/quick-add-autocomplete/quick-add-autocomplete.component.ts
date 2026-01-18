import { Component, EventEmitter, Output, inject, signal, computed } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormControl, ReactiveFormsModule } from '@angular/forms';
import { MatAutocompleteModule } from '@angular/material/autocomplete';
import { MatInputModule } from '@angular/material/input';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatIconModule } from '@angular/material/icon';
import { MatButtonModule } from '@angular/material/button';
import { MatTooltipModule } from '@angular/material/tooltip';
import { AssetService } from '../../../features/assets/services/asset.service';
import { MachineDefinition, ResourceDefinition } from '../../../features/assets/models/asset.models';

export interface QuickAddResult {
    type: 'machine' | 'resource';
    definition: MachineDefinition | ResourceDefinition;
}

@Component({
    selector: 'app-quick-add-autocomplete',
    standalone: true,
    imports: [
        CommonModule,
        ReactiveFormsModule,
        MatAutocompleteModule,
        MatInputModule,
        MatFormFieldModule,
        MatIconModule,
        MatButtonModule,
        MatTooltipModule
    ],
    template: `
    <mat-form-field appearance="outline" class="w-full no-label" subscriptSizing="dynamic">
      <mat-icon matPrefix>search</mat-icon>
      <input
        matInput
        [formControl]="searchControl"
        [matAutocomplete]="auto"
        placeholder="Quickly find a machine or resource..."
      />
      @if (searchControl.value) {
        <button mat-icon-button matSuffix (click)="clearSearch($event)">
          <mat-icon>close</mat-icon>
        </button>
      }
      <mat-autocomplete #auto="matAutocomplete" (optionSelected)="onSelect($event.option.value)">
        @for (item of filteredDefinitions(); track item.definition.accession_id) {
          <mat-option [value]="item">
            <div class="flex items-center gap-3">
              <div class="type-icon-chip" [class.machine]="item.type === 'machine'">
                <mat-icon>{{ item.type === 'machine' ? 'precision_manufacturing' : 'science' }}</mat-icon>
              </div>
              <div class="flex flex-col min-w-0">
                <span class="font-medium truncate">{{ item.definition.name }}</span>
                <span class="text-[10px] sys-text-secondary truncate font-mono" [matTooltip]="item.definition.fqn">
                  {{ item.type | titlecase }} • {{ getShortFqn(item.definition.fqn) || 'Unknown' }}
                </span>
              </div>
            </div>
          </mat-option>
        }
        @if (searchControl.value && filteredDefinitions().length === 0) {
          <mat-option disabled>No matches found</mat-option>
        }
      </mat-autocomplete>
    </mat-form-field>
  `,
    styles: [`
    .no-label ::ng-deep .mat-mdc-form-field-subscript-wrapper { display: none; }
    
    .type-icon-chip {
      width: 32px;
      height: 32px;
      border-radius: 8px;
      background: var(--mat-sys-surface-container-high);
      display: grid;
      place-items: center;
      color: var(--mat-sys-on-surface-variant);
      flex-shrink: 0;
    }
    
    .type-icon-chip.machine {
      background: var(--mat-sys-primary-container);
      color: var(--mat-sys-on-primary-container);
    }
    
    .type-icon-chip mat-icon {
      font-size: 18px;
      width: 18px;
      height: 18px;
    }
    
    .sys-text-secondary { color: var(--mat-sys-on-surface-variant); }
  `]
})
export class QuickAddAutocompleteComponent {
    @Output() definitionSelected = new EventEmitter<QuickAddResult>();

    private assetService = inject(AssetService);
    searchControl = new FormControl('');

    private machineDefinitions = signal<MachineDefinition[]>([]);
    private resourceDefinitions = signal<ResourceDefinition[]>([]);

    private allDefinitions = computed(() => [
        ...this.machineDefinitions().map(d => ({ type: 'machine' as const, definition: d })),
        ...this.resourceDefinitions().map(d => ({ type: 'resource' as const, definition: d }))
    ]);

    filteredDefinitions = computed(() => {
        const term = (this.searchControl.value || '').toLowerCase();
        if (term.length < 2) return [];

        return this.allDefinitions()
            .filter(item => {
                const def = item.definition as unknown as Record<string, unknown>;
                const matchText = [
                    item.definition.name,
                    item.definition.fqn,
                    item.type,
                    def['vendor'] || '',
                    def['plr_category'] || '',
                    def['machine_category'] || ''
                ].join(' ').toLowerCase();
                return matchText.includes(term);
            })
            .slice(0, 10);
    });

    constructor() {
        this.assetService.getMachineDefinitions().subscribe(defs => {
            this.machineDefinitions.set(defs.filter(d => d.frontend_fqn));
        });
        this.assetService.getResourceDefinitions().subscribe(defs => {
            this.resourceDefinitions.set(defs);
        });
    }

    onSelect(result: QuickAddResult) {
        this.definitionSelected.emit(result);
        // Do not clear search yet, let the parent handle the jump first if needed, 
        // or clear it if we stay on same step (but here we jump).
    }

    /**
     * Returns the last segment of a Python fully-qualified name.
     * e.g. "pylabrobot.fans.Fan" -> "Fan"
     */
    getShortFqn(fqn: string | undefined): string {
        if (!fqn) return '';
        const parts = fqn.split('.');
        return parts[parts.length - 1] || fqn;
    }

    clearSearch(event: Event) {
        event.stopPropagation();
        this.searchControl.setValue('');
    }
}
