import { Component, ChangeDetectionStrategy, inject, ViewChild, signal, OnInit, OnDestroy, NgZone } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatTabsModule } from '@angular/material/tabs';
import { MatIconModule } from '@angular/material/icon';
import { MatButtonModule } from '@angular/material/button';
import { MatDialog, MatDialogModule } from '@angular/material/dialog';
import { MatTooltipModule } from '@angular/material/tooltip';
import { MachineListComponent } from './components/machine-list/machine-list.component';
import { ResourceAccordionComponent } from './components/resource-accordion/resource-accordion.component';
import { DefinitionsListComponent } from './components/definitions-list/definitions-list.component';
import { MachineDialogComponent } from './components/machine-dialog.component';
import { ResourceDialogComponent } from './components/resource-dialog.component';
import { HardwareDiscoveryDialogComponent } from '@shared/components/hardware-discovery-dialog/hardware-discovery-dialog.component';
import { HardwareDiscoveryButtonComponent } from '@shared/components/hardware-discovery-button/hardware-discovery-button.component';
import { AssetDashboardComponent } from './components/asset-dashboard/asset-dashboard.component';
import { AssetService } from './services/asset.service';
import { switchMap, filter, finalize } from 'rxjs/operators';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { ActivatedRoute, Router } from '@angular/router';
import { ModeService } from '@core/services/mode.service';
import { MatSnackBar, MatSnackBarModule } from '@angular/material/snack-bar';

@Component({
  selector: 'app-assets',
  standalone: true,
  imports: [
    CommonModule,
    MatTabsModule,
    MatIconModule,
    MatButtonModule,
    MatDialogModule,
    MatProgressSpinnerModule,
    MatTooltipModule,
    MatSnackBarModule,
    MachineListComponent,
    ResourceAccordionComponent,
    DefinitionsListComponent,
    AssetDashboardComponent,
    HardwareDiscoveryButtonComponent
  ],
  template: `
    <div class="p-6 max-w-screen-2xl mx-auto h-full flex flex-col">
      <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 mb-4">
        <div class="min-w-0 flex-1">
          <h1 class="text-3xl font-bold text-sys-text-primary mb-1 truncate">Asset Management</h1>
          <p class="text-sys-text-secondary truncate">Manage your laboratory hardware and inventory</p>
        </div>
        <div class="flex flex-wrap items-center gap-2 sm:gap-3 w-full sm:w-auto">
          <app-hardware-discovery-button class="sm:mr-2"></app-hardware-discovery-button>
          <span class="flex-1 sm:flex-initial" [matTooltip]="selectedIndex === 3 ? (modeService.isBrowserMode() ? 'Definitions are pre-synced in Browser Mode.' : 'Sync all hardware and protocol definitions from the backend.') : ''">
            <button 
              mat-flat-button 
              class="!bg-gradient-to-br !from-primary !to-primary-dark !text-white !rounded-xl !px-6 !py-3 !font-semibold shadow-lg shadow-primary/20 hover:shadow-primary/40 transition-all hover:-translate-y-0.5 disabled:opacity-50 disabled:cursor-not-allowed w-full sm:w-auto" 
              (click)="openAddAsset()" 
              [disabled]="isLoading() || isSyncing()"
              data-tour-id="add-asset-btn"
            >
              <mat-icon>{{ selectedIndex === 3 ? 'sync' : 'add' }}</mat-icon>
              {{ selectedIndex === 3 ? 'Sync Definitions' : 'Add ' + assetTypeLabel() }}
            </button>
          </span>
        </div>
      </div>

      <div class="bg-surface border border-[var(--theme-border)] rounded-3xl overflow-hidden backdrop-blur-xl flex flex-col flex-1 min-h-0 shadow-xl relative">
        <mat-tab-group 
          animationDuration="300ms" 
          class="assets-tabs flex-1 flex flex-col min-h-0 custom-tabs" 
          [(selectedIndex)]="selectedIndex" 
          (selectedIndexChange)="onTabChange($event)"
          mat-stretch-tabs="false" 
          mat-align-tabs="start"
        >
          <mat-tab>
            <ng-template mat-tab-label>
              <div class="flex items-center gap-2 px-2 py-1">
                <mat-icon class="!w-5 !h-5 !text-[20px]">dashboard</mat-icon>
                <span class="font-medium">Overview</span>
              </div>
            </ng-template>
            <div class="h-full overflow-hidden bg-[var(--mat-sys-surface-variant)] relative p-4">
              <app-asset-dashboard></app-asset-dashboard>
            </div>
          </mat-tab>

          <mat-tab>
            <ng-template mat-tab-label>
              <div class="flex items-center gap-2 px-2 py-1">
                <mat-icon class="!w-5 !h-5 !text-[20px]">precision_manufacturing</mat-icon>
                <span class="font-medium">Machines</span>
              </div>
            </ng-template>
            <div class="h-full overflow-y-auto bg-[var(--mat-sys-surface-variant)] relative">
              @if (isLoading()) {
                <div class="absolute inset-0 bg-[var(--mat-sys-surface-variant)] backdrop-blur-sm z-10 flex items-center justify-center">
                  <mat-spinner diameter="40"></mat-spinner>
                </div>
              }
              <app-machine-list #machineList data-tour-id="machine-list"></app-machine-list>
            </div>
          </mat-tab>

          <mat-tab>
            <ng-template mat-tab-label>
              <div class="flex items-center gap-2 px-2 py-1">
                <mat-icon class="!w-5 !h-5 !text-[20px]">science</mat-icon>
                <span class="font-medium">Resources</span>
              </div>
            </ng-template>
            <div class="h-full overflow-y-auto bg-[var(--mat-sys-surface-variant)] relative">
              @if (isLoading()) {
                <div class="absolute inset-0 bg-[var(--mat-sys-surface-variant)] backdrop-blur-sm z-10 flex items-center justify-center">
                  <mat-spinner diameter="40"></mat-spinner>
                </div>
              }
              <app-resource-accordion #resourceAccordion data-tour-id="resource-list"></app-resource-accordion>
            </div>
          </mat-tab>

          <mat-tab>
            <ng-template mat-tab-label>
              <div class="flex items-center gap-2 px-2 py-1">
                <mat-icon class="!w-5 !h-5 !text-[20px]">inventory_2</mat-icon>
                <span class="font-medium">Registry</span>
              </div>
            </ng-template>
            <div class="h-full overflow-y-auto bg-[var(--mat-sys-surface-variant)] relative">
              @if (isSyncing()) {
                <div class="absolute inset-0 bg-[var(--mat-sys-surface-variant)] backdrop-blur-sm z-10 flex items-center justify-center">
                  <mat-spinner diameter="40"></mat-spinner>
                </div>
              }
              <app-definitions-list></app-definitions-list>
            </div>
          </mat-tab>
        </mat-tab-group>
      </div>
    </div>
  `,
  styles: [`
    :host {
      display: block;
      height: 100%;
    }

    /* Custom Mat Tab Styling */
    ::ng-deep .custom-tabs .mat-mdc-tab-header {
      border-bottom: 1px solid var(--theme-border);
      background: var(--mat-sys-surface-variant); /* Slightly lighter header */
    }

    ::ng-deep .custom-tabs .mat-mdc-tab-label-container {
      padding: 0 16px;
    }

    ::ng-deep .custom-tabs .mdc-tab {
      color: var(--theme-text-secondary) !important;
      font-family: inherit !important;
      letter-spacing: normal !important;
      min-width: 120px !important;
      height: 56px !important;
      opacity: 1 !important;
    }

    ::ng-deep .custom-tabs .mdc-tab--active {
      color: var(--theme-text-primary) !important;
    }

    ::ng-deep .custom-tabs .mdc-tab--active .mdc-tab__text-label {
      color: var(--primary-color) !important;
    }

    ::ng-deep .custom-tabs .mdc-tab--active .mat-icon {
      color: var(--primary-color) !important;
    }

    ::ng-deep .custom-tabs .mat-mdc-tab-group-indicator {
      border-bottom-color: var(--primary-color) !important;
      height: 3px !important;
      border-radius: 3px 3px 0 0;
    }

    ::ng-deep .custom-tabs .mat-mdc-tab-body-wrapper {
      flex: 1;
      height: 100%;
    }
  `],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class AssetsComponent implements OnInit, OnDestroy {
  private dialog = inject(MatDialog);
  private assetService = inject(AssetService);
  private route = inject(ActivatedRoute);
  private router = inject(Router);
  private ngZone = inject(NgZone);
  public modeService = inject(ModeService);
  private snackBar = inject(MatSnackBar);

  @ViewChild('machineList') machineList!: MachineListComponent;
  @ViewChild('resourceAccordion') resourceAccordion!: ResourceAccordionComponent;

  selectedIndex = 0;
  assetTypeLabel = signal('Machine');
  isLoading = signal(false);
  isSyncing = signal(false);

  private hardwareDiscoveryListener = () => {
    this.ngZone.run(() => this.openHardwareDiscovery());
  };

  ngOnInit() {
    // Listen for command palette hardware discovery event
    window.addEventListener('open-hardware-discovery', this.hardwareDiscoveryListener);
    window.addEventListener('asset-dashboard-action', this.dashboardActionListener);

    // Listen to query params to switch tabs
    this.route.queryParams.subscribe(params => {
      const type = params['type'];
      if (type === 'machine') {
        this.selectedIndex = 1;
        this.assetTypeLabel.set('Machine');
      } else if (type === 'resource') {
        this.selectedIndex = 2;
        this.assetTypeLabel.set('Resource');
      } else if (type === 'registry' || type === 'definition') {
        this.selectedIndex = 3;
        this.assetTypeLabel.set('Registry Item');
      } else {
        this.selectedIndex = 0;
        this.assetTypeLabel.set('Asset');
      }
    });
  }

  ngOnDestroy() {
    window.removeEventListener('open-hardware-discovery', this.hardwareDiscoveryListener);
    window.removeEventListener('asset-dashboard-action', this.dashboardActionListener);
  }

  onTabChange(index: number) {
    this.selectedIndex = index;
    let type = 'overview';

    switch (index) {
      case 0:
        this.assetTypeLabel.set('Asset');
        type = 'overview';
        break;
      case 1:
        this.assetTypeLabel.set('Machine');
        type = 'machine';
        break;
      case 2:
        this.assetTypeLabel.set('Resource');
        type = 'resource';
        break;
      case 3:
        this.assetTypeLabel.set('Registry Item');
        type = 'registry';
        break;
    }

    // Update URL without reloading
    this.router.navigate([], {
      relativeTo: this.route,
      queryParams: { type },
      queryParamsHandling: 'merge', // merge with other existing query params
      replaceUrl: true // prevent pushing a new history state for every tab click
    });
  }

  private dashboardActionListener = (event: Event) => {
    const action = (event as CustomEvent).detail;
    this.ngZone.run(() => {
      if (action === 'add-machine') this.openAddMachine();
      if (action === 'add-resource') this.openAddResource();
      if (action === 'discover') this.openHardwareDiscovery();
    });
  };

  openAddAsset() {
    if (this.isLoading()) return; // Prevent multiple clicks

    if (this.selectedIndex === 1) { // Machine tab
      this.openAddMachine();
    } else if (this.selectedIndex === 2) { // Resource tab
      this.openAddResource();
    } else if (this.selectedIndex === 0) {
      // If on dashboard, ask what to add? Or default to machine?
      // For now let's open machine dialog as default
      this.openAddMachine();
    } else {
      // Registry tab
      if (this.modeService.isBrowserMode()) {
        this.snackBar.open('Definitions are pre-synced in Browser Mode.', 'Close', { duration: 3000 });
        return;
      }
      this.triggerSyncDefinitions();
    }
  }

  private triggerSyncDefinitions() {
    this.isSyncing.set(true);
    this.assetService.syncDefinitions().pipe(
      finalize(() => this.isSyncing.set(false))
    ).subscribe({
      next: (resp) => {
        this.snackBar.open(resp.message || 'Synchronization started successfully.', 'Close', { duration: 3000 });
      },
      error: (err) => {
        console.error('Error during synchronization', err);
        this.snackBar.open('Failed to initiate synchronization. See console for details.', 'Close', { duration: 5000 });
      }
    });
  }

  private openAddMachine() {
    console.debug('[ASSET-DEBUG] openAddMachine: Opening dialog');
    const dialogRef = this.dialog.open(MachineDialogComponent, {
      width: '700px'
    });

    dialogRef.afterClosed().pipe(
      filter(result => {
        console.debug('[ASSET-DEBUG] openAddMachine: Dialog closed with result:', result);
        return !!result;
      }),
      switchMap(result => {
        console.debug('[ASSET-DEBUG] openAddMachine: Calling assetService.createMachine');
        this.isLoading.set(true); // Set loading true before API call
        return this.assetService.createMachine(result).pipe(
          finalize(() => this.isLoading.set(false)) // Set loading false after API call completes
        );
      })
    ).subscribe({
      next: (createdMachine) => {
        console.debug('[ASSET-DEBUG] openAddMachine: Machine created, reloading list', createdMachine);
        this.machineList.loadMachines();
      },
      error: (err) => console.error('[ASSET-DEBUG] openAddMachine: Error', err)
    });
  }

  private openAddResource() {
    console.debug('[ASSET-DEBUG] openAddResource: Opening dialog');
    const dialogRef = this.dialog.open(ResourceDialogComponent, {
      width: '700px'
    });

    dialogRef.afterClosed().pipe(
      filter(result => {
        console.debug('[ASSET-DEBUG] openAddResource: Dialog closed with result:', result);
        return !!result;
      }),
      switchMap(result => {
        console.debug('[ASSET-DEBUG] openAddResource: Calling assetService.createResource');
        this.isLoading.set(true); // Set loading true before API call
        return this.assetService.createResource(result).pipe(
          finalize(() => this.isLoading.set(false)) // Set loading false after API call completes
        );
      })
    ).subscribe({
      next: (createdResource) => {
        console.debug('[ASSET-DEBUG] openAddResource: Resource created, reloading list', createdResource);
        this.resourceAccordion.loadData();
      },
      error: (err) => console.error('[ASSET-DEBUG] openAddResource: Error', err)
    });
  }

  openHardwareDiscovery() {
    this.dialog.open(HardwareDiscoveryDialogComponent, {
      width: '800px',
      maxHeight: '90vh'
    });
  }
}
