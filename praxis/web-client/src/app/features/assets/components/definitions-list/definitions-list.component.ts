import { Component, ChangeDetectionStrategy, inject, signal, computed } from '@angular/core';

import { MatTableModule } from '@angular/material/table';
import { MatIconModule } from '@angular/material/icon';
import { MatButtonModule } from '@angular/material/button';
import { MatTooltipModule } from '@angular/material/tooltip';
import { MatInputModule } from '@angular/material/input';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatTabsModule } from '@angular/material/tabs';
import { AssetService } from '../../services/asset.service';
import { ResourceDefinition } from '../../models/asset.models';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { debounceTime, distinctUntilChanged, startWith } from 'rxjs/operators';
import { FormControl, ReactiveFormsModule } from '@angular/forms';
import { getPropertyTooltip } from '@shared/constants/resource-tooltips';
import { MachineDefinitionAccordionComponent } from '../machine-definition-accordion/machine-definition-accordion.component';
import { FilterHeaderComponent } from '../filter-header/filter-header.component';
import { ModeService } from '@core/services/mode.service';

@Component({
  selector: 'app-definitions-list',
  standalone: true,
  imports: [
    MatTableModule,
    MatIconModule,
    MatButtonModule,
    MatTooltipModule,
    MatInputModule,
    MatFormFieldModule,
    MatTabsModule,
    ReactiveFormsModule,
    MachineDefinitionAccordionComponent,
    FilterHeaderComponent
  ],
  template: `
    <div class="definitions-list-container">
      @if (modeService.isBrowserMode()) {
        <div class="browser-mode-banner">
          <mat-icon>info</mat-icon>
          <span>
            Registry is read-only in browser mode.
            Definitions are loaded from bundled PyLabRobot data.
          </span>
        </div>
      }
      <mat-tab-group animationDuration="0ms">
        <mat-tab>
          <ng-template mat-tab-label>
            <div class="flex items-center gap-2">
              <mat-icon class="!w-5 !h-5 !text-[18px]">precision_manufacturing</mat-icon>
              <span>Machine Types</span>
            </div>
          </ng-template>
          <div class="tab-content">
            <app-filter-header
              searchPlaceholder="Search machine types..."
              [searchValue]="machineSearch()"
              (searchChange)="machineSearch.set($event)">
              <!-- No additional filters yet -->
            </app-filter-header>
            <app-machine-definition-accordion [search]="machineSearch()"></app-machine-definition-accordion>
          </div>
        </mat-tab>

        <mat-tab>
          <ng-template mat-tab-label>
            <div class="flex items-center gap-2">
              <mat-icon class="!w-5 !h-5 !text-[18px]">science</mat-icon>
              <span>Resource Types</span>
            </div>
          </ng-template>
          <div class="resource-tab-content">
            <app-filter-header
              searchPlaceholder="Filter Resource Definitions..."
              [searchValue]="resourceSearch()"
              (searchChange)="resourceSearch.set($event)">
              <!-- No additional filters yet -->
            </app-filter-header>

            <table mat-table [dataSource]="filteredResourceDefinitions()" class="mat-elevation-z2 mt-4">
              <ng-container matColumnDef="name">
                <th mat-header-cell *matHeaderCellDef> Name </th>
                <td mat-cell *matCellDef="let def"> {{ def.name }} </td>
              </ng-container>

              <ng-container matColumnDef="type">
                <th mat-header-cell *matHeaderCellDef> Type </th>
                <td mat-cell *matCellDef="let def"> {{ def.resource_type || 'N/A' }} </td>
              </ng-container>

              <ng-container matColumnDef="manufacturer">
                <th mat-header-cell *matHeaderCellDef> Manufacturer </th>
                <td mat-cell *matCellDef="let def"> {{ def.manufacturer || 'N/A' }} </td>
              </ng-container>

              <ng-container matColumnDef="model">
                <th mat-header-cell *matHeaderCellDef> Model </th>
                <td mat-cell *matCellDef="let def"> {{ def.model || 'N/A' }} </td>
              </ng-container>

              <ng-container matColumnDef="consumable">
                <th mat-header-cell *matHeaderCellDef class="!text-center"> Consumable </th>
                <td mat-cell *matCellDef="let def" class="!text-center">
                  <mat-icon
                    [color]="def.is_consumable ? 'primary' : 'warn'"
                    [matTooltip]="def.is_consumable ? getPropertyTooltip('consumable') : 'Non-consumable: can be reused across protocols'"
                  >
                    {{ def.is_consumable ? 'check_circle' : 'cancel' }}
                  </mat-icon>
                </td>
              </ng-container>

              <ng-container matColumnDef="actions">
                <th mat-header-cell *matHeaderCellDef class="!text-center"> Actions </th>
                <td mat-cell *matCellDef="let def" class="!text-center">
                  <button mat-icon-button color="primary" matTooltip="View Details">
                    <mat-icon>info</mat-icon>
                  </button>
                </td>
              </ng-container>

              <tr mat-header-row *matHeaderRowDef="displayedResourceColumns"></tr>
              <tr mat-row *matRowDef="let row; columns: displayedResourceColumns;"></tr>

              <tr class="mat-row" *matNoDataRow>
                <td class="mat-cell" colspan="6">
                  <div class="empty-state">
                    <mat-icon>search_off</mat-icon>
                    <span>No resource definitions matching the filter "{{ resourceSearch() }}"</span>
                  </div>
                </td>
              </tr>
            </table>
          </div>
        </mat-tab>
      </mat-tab-group>
    </div>
  `,
  styles: [`
    .definitions-list-container {
      /* Remove padding to allow tabs to be full width */
      height: 100%;
      display: flex;
      flex-direction: column;
    }

    .browser-mode-banner {
      display: flex;
      align-items: center;
      gap: 12px;
      background: var(--mat-sys-secondary-container);
      color: var(--mat-sys-on-secondary-container);
      padding: 12px 16px;
      margin: 16px 16px 0 16px;
      border-radius: 8px;
    }

    .filter-field {
      width: 100%;
      margin-bottom: 16px;
    }

    .mat-elevation-z2 {
      width: 100%;
    }

    .empty-state {
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      padding: 48px 0;
      color: var(--mat-sys-on-surface-variant);
      gap: 12px;
    }

    .empty-state mat-icon {
      font-size: 48px;
      width: 48px;
      height: 48px;
      opacity: 0.5;
    }

    mat-tab-group {
      /* Remove auto margin */
      margin-top: 0;
    }

    .resource-tab-content {
      padding: 0 16px 16px 16px;
    }
  `],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class DefinitionsListComponent {
  private assetService = inject(AssetService);
  public modeService = inject(ModeService);

  resourceDefinitions = signal<ResourceDefinition[]>([]);
  machineSearch = signal('');
  resourceSearch = signal('');
  
  filteredResourceDefinitions = computed(() => {
    const filterValue = this.resourceSearch().toLowerCase();
    return this.resourceDefinitions().filter(def =>
      def.name.toLowerCase().includes(filterValue) ||
      def.resource_type?.toLowerCase().includes(filterValue) ||
      def.manufacturer?.toLowerCase().includes(filterValue) ||
      def.model?.toLowerCase().includes(filterValue)
    );
  });

  displayedResourceColumns: string[] = ['name', 'type', 'manufacturer', 'model', 'consumable', 'actions'];

  constructor() {
    this.loadResourceDefinitions();
  }

  private loadResourceDefinitions(): void {
    this.assetService.getResourceDefinitions().subscribe(
      (data) => {
        this.resourceDefinitions.set(data);
      },
      (error) => {
        console.error('Error fetching resource definitions:', error);
      }
    );
  }

  getPropertyTooltip(property: string): string {
    return getPropertyTooltip(property);
  }
}
