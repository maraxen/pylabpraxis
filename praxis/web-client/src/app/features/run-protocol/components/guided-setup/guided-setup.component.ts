import { Component, Inject, inject, signal, computed, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatDialogModule, MAT_DIALOG_DATA, MatDialogRef } from '@angular/material/dialog';
import { MatButtonModule } from '@angular/material/button';
import { MatSelectModule } from '@angular/material/select';
import { MatIconModule } from '@angular/material/icon';
import { FormsModule } from '@angular/forms';
import { ProtocolDefinition, AssetRequirement } from '@features/protocols/models/protocol.models';
import { Resource } from '@features/assets/models/asset.models';
import { AssetService } from '@features/assets/services/asset.service';

export interface GuidedSetupData {
  protocol: ProtocolDefinition;
}

export interface GuidedSetupResult {
  assetMap: Record<string, Resource>; // Map requirement accession_id -> Inventory Resource
}

@Component({
  selector: 'app-guided-setup',
  standalone: true,
  imports: [
    CommonModule,
    MatDialogModule,
    MatButtonModule,
    MatSelectModule,
    MatIconModule,
    FormsModule
  ],
  template: `
    <h2 mat-dialog-title>Deck Setup: {{ data.protocol.name }}</h2>
    <mat-dialog-content>
      <p class="description">
        Please assign inventory items to the required assets for this protocol.
        We've auto-selected matches where possible.
      </p>

      <div class="requirements-list">
        @for (req of requiredAssets; track req.accession_id) {
          <div class="requirement-item">
            <div class="req-info">
              <span class="req-name">{{ req.name }}</span>
              <span class="req-type">{{ req.type_hint_str || 'Generic Resource' }}</span>
            </div>
            
            <mat-form-field appearance="outline">
              <mat-label>Select Inventory Item</mat-label>
              <mat-select
                [value]="selectedAssets()[req.accession_id]"
                (selectionChange)="updateSelection(req.accession_id, $event.value)"
                [compareWith]="compareResources"
              >
                 <mat-option [value]="null">-- Select --</mat-option>
                 @for (res of getCompatibleResources(req); track res.accession_id) {
                   <mat-option [value]="res">
                     {{ res.name }} <span class="res-id">({{ res.accession_id.substring(0,6) }})</span>
                   </mat-option>
                 }
              </mat-select>
              <mat-error *ngIf="!selectedAssets()[req.accession_id]">Required</mat-error>
            </mat-form-field>
          </div>
        }
      </div>
    </mat-dialog-content>
    <mat-dialog-actions align="end">
      <button mat-button mat-dialog-close>Cancel</button>
      <button 
        mat-raised-button 
        color="primary" 
        [disabled]="!isValid()" 
        (click)="confirm()">
        Confirm & Run
      </button>
    </mat-dialog-actions>
  `,
  styles: [`
    .description {
      color: var(--sys-on-surface-variant);
      margin-bottom: 24px;
    }
    .requirements-list {
      display: flex;
      flex-direction: column;
      gap: 16px;
    }
    .requirement-item {
      display: grid;
      grid-template-columns: 1fr 200px;
      gap: 16px;
      align-items: center;
      padding: 12px;
      background: var(--sys-surface-container);
      border-radius: 8px;
    }
    .req-info {
      display: flex;
      flex-direction: column;
    }
    .req-name {
      font-weight: 500;
    }
    .req-type {
      font-size: 0.8em;
      color: var(--sys-on-surface-variant);
    }
    .res-id {
      font-size: 0.8em;
      opacity: 0.7;
    }
    mat-form-field {
      margin-bottom: -1.25em; /* Tighten up spacing */
    }
  `]
})
export class GuidedSetupComponent implements OnInit {
  private assetService = inject(AssetService);
  private dialogRef = inject(MatDialogRef<GuidedSetupComponent>);

  inventory = signal<Resource[]>([]);
  selectedAssets = signal<Record<string, Resource | null>>({});

  constructor(@Inject(MAT_DIALOG_DATA) public data: GuidedSetupData) { }

  get requiredAssets(): AssetRequirement[] {
    return this.data.protocol.assets || [];
  }

  ngOnInit() {
    this.assetService.getResources().subscribe(resources => {
      this.inventory.set(resources);
      this.autoSelect();
    });
  }

  autoSelect() {
    const map: Record<string, Resource | null> = {};
    const usedResourceIds = new Set<string>();

    this.requiredAssets.forEach(req => {
      // Find first compatible resource not already used
      const candidates = this.getCompatibleResources(req);
      const match = candidates.find(res => !usedResourceIds.has(res.accession_id));

      if (match) {
        map[req.accession_id] = match;
        usedResourceIds.add(match.accession_id);
      } else {
        map[req.accession_id] = null;
      }
    });

    this.selectedAssets.set(map);
  }

  getCompatibleResources(req: AssetRequirement): Resource[] {
    // Simple filter logic: check if resource type hint matches or name contains keywords
    // In a real app, strict type checking against ResourceDefinition is needed.
    const reqType = (req.type_hint_str || req.fqn || '').toLowerCase();
    const reqName = req.name.toLowerCase();

    return this.inventory().filter(res => {
      // Logic from DeckGeneratorService kind of logic
      // We rely on name matching for demo if type is missing.
      // BUT `mock-data/resources` seems to populate or we rely on some fields.
      // Wait, Resource model has limited fields.
      // Let's rely on name matching for demo if type is missing.

      const resName = res.name.toLowerCase();

      if (reqType.includes('plate') && (resName.includes('plate') || resName.includes('reservoir'))) return true;
      if (reqType.includes('tip') && resName.includes('tip')) return true;
      if (reqType.includes('trough') && (resName.includes('trough') || resName.includes('reservoir'))) return true;

      // Fallback: name contains name
      if (resName.includes(reqName)) return true;

      return false;
    });
  }

  updateSelection(reqId: string, resource: Resource | null) {
    this.selectedAssets.update(current => ({
      ...current,
      [reqId]: resource
    }));
  }

  isValid(): boolean {
    // Check if all required assets have a selection
    return this.requiredAssets.every(req =>
      !req.optional ? !!this.selectedAssets()[req.accession_id] : true
    );
  }

  confirm() {
    const result: GuidedSetupResult = {
      assetMap: this.selectedAssets() as Record<string, Resource>
    };
    this.dialogRef.close(result);
  }

  compareResources(o1: Resource, o2: Resource): boolean {
    return o1 && o2 ? o1.accession_id === o2.accession_id : o1 === o2;
  }
}
