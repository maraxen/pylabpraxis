import { Component, ChangeDetectionStrategy, inject, ViewChild, signal, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatTabsModule } from '@angular/material/tabs';
import { MatIconModule } from '@angular/material/icon';
import { MatButtonModule } from '@angular/material/button';
import { MatDialog, MatDialogModule } from '@angular/material/dialog';
import { MachineListComponent } from './components/machine-list/machine-list.component';
import { ResourceAccordionComponent } from './components/resource-accordion/resource-accordion.component';
import { DefinitionsListComponent } from './components/definitions-list/definitions-list.component';
import { MachineDialogComponent } from './components/machine-dialog.component';
import { ResourceDialogComponent } from './components/resource-dialog.component';
import { AssetService } from './services/asset.service';
import { switchMap, filter, finalize } from 'rxjs/operators';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { ActivatedRoute, Router } from '@angular/router';

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
    MachineListComponent,
    ResourceAccordionComponent,  // Changed from ResourceListComponent
    DefinitionsListComponent
  ],
  template: `
    <div class="assets-container">
      <div class="header">
        <h1>Asset Management</h1>
        <button mat-flat-button color="primary" (click)="openAddAsset()" [disabled]="isLoading()">
          <mat-icon>add</mat-icon>
          Add {{ assetTypeLabel() }}
        </button>
      </div>

      <mat-tab-group animationDuration="0ms" class="assets-tabs" [(selectedIndex)]="selectedIndex" (selectedIndexChange)="onTabChange($event)">
        <mat-tab>
          <ng-template mat-tab-label>
            <mat-icon class="tab-icon">precision_manufacturing</mat-icon>
            Machines
          </ng-template>
          <div *ngIf="isLoading()" class="spinner-overlay"><mat-spinner diameter="40"></mat-spinner></div>
          <app-machine-list #machineList></app-machine-list>
        </mat-tab>

        <mat-tab>
          <ng-template mat-tab-label>
            <mat-icon class="tab-icon">science</mat-icon>
            Resources
          </ng-template>
          <div *ngIf="isLoading()" class="spinner-overlay"><mat-spinner diameter="40"></mat-spinner></div>
          <app-resource-accordion #resourceAccordion></app-resource-accordion>
        </mat-tab>

        <mat-tab>
          <ng-template mat-tab-label>
            <mat-icon class="tab-icon">library_books</mat-icon>
            Definitions
          </ng-template>
          <app-definitions-list></app-definitions-list>
        </mat-tab>
      </mat-tab-group>
    </div>
  `,
  styles: [`
    .assets-container {
      height: 100%;
      display: flex;
      flex-direction: column;
      position: relative; /* Needed for spinner-overlay positioning */
    }

    .header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 16px;
    }

    h1 {
      margin: 0;
      font-size: 1.5rem;
      font-weight: 500;
    }

    .assets-tabs {
      flex: 1;
    }

    .tab-icon {
      margin-right: 8px;
    }

    .spinner-overlay {
      position: absolute;
      top: 0;
      left: 0;
      right: 0;
      bottom: 0;
      background: rgba(255, 255, 255, 0.8);
      display: flex;
      justify-content: center;
      align-items: center;
      z-index: 10;
    }
  `],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class AssetsComponent implements OnInit {
  private dialog = inject(MatDialog);
  private assetService = inject(AssetService);
  private route = inject(ActivatedRoute);
  private router = inject(Router);

  @ViewChild('machineList') machineList!: MachineListComponent;
  @ViewChild('resourceAccordion') resourceAccordion!: ResourceAccordionComponent;

  selectedIndex = 0;
  assetTypeLabel = signal('Machine');
  isLoading = signal(false);

  ngOnInit() {
    // Listen to query params to switch tabs
    this.route.queryParams.subscribe(params => {
      const type = params['type'];
      if (type === 'resource') {
        this.selectedIndex = 1;
        this.assetTypeLabel.set('Resource');
      } else if (type === 'definition') {
        this.selectedIndex = 2;
        this.assetTypeLabel.set('Definition');
      } else {
        this.selectedIndex = 0;
        this.assetTypeLabel.set('Machine');
      }
    });
  }

  onTabChange(index: number) {
    this.selectedIndex = index;
    let type = 'machine';

    switch (index) {
      case 0:
        this.assetTypeLabel.set('Machine');
        type = 'machine';
        break;
      case 1:
        this.assetTypeLabel.set('Resource');
        type = 'resource';
        break;
      case 2:
        this.assetTypeLabel.set('Definition');
        type = 'definition';
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

  openAddAsset() {
    if (this.isLoading()) return; // Prevent multiple clicks

    if (this.selectedIndex === 0) {
      this.openAddMachine();
    } else if (this.selectedIndex === 1) {
      this.openAddResource();
    } else {
      alert('Adding definitions manually is not supported yet. Please sync from backend.');
    }
  }

  private openAddMachine() {
    const dialogRef = this.dialog.open(MachineDialogComponent, {
      width: '700px'
    });

    dialogRef.afterClosed().pipe(
      filter(result => !!result),
      switchMap(result => {
        this.isLoading.set(true); // Set loading true before API call
        return this.assetService.createMachine(result).pipe(
          finalize(() => this.isLoading.set(false)) // Set loading false after API call completes
        );
      })
    ).subscribe({
      next: () => {
        this.machineList.loadMachines();
      },
      error: (err) => console.error('Error creating machine', err)
    });
  }

  private openAddResource() {
    const dialogRef = this.dialog.open(ResourceDialogComponent, {
      width: '700px'
    });

    dialogRef.afterClosed().pipe(
      filter(result => !!result),
      switchMap(result => {
        this.isLoading.set(true); // Set loading true before API call
        return this.assetService.createResource(result).pipe(
          finalize(() => this.isLoading.set(false)) // Set loading false after API call completes
        );
      })
    ).subscribe({
      next: () => {
        this.resourceAccordion.loadData();
      },
      error: (err) => console.error('Error creating resource', err)
    });
  }
}
