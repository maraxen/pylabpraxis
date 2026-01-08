import { Component, Inject, inject, signal, computed, OnInit, Input, Output, EventEmitter, booleanAttribute, Optional } from '@angular/core';

import { MatDialogModule, MAT_DIALOG_DATA, MatDialogRef } from '@angular/material/dialog';
import { MatButtonModule } from '@angular/material/button';
import { MatSelectModule } from '@angular/material/select';
import { MatIconModule } from '@angular/material/icon';
import { MatTooltipModule } from '@angular/material/tooltip';
import { MatChipsModule } from '@angular/material/chips';
import { FormsModule } from '@angular/forms';
import { AriaSelectComponent, SelectOption } from '@shared/components/aria-select/aria-select.component';
import { AriaAutocompleteComponent } from '@shared/components/aria-autocomplete/aria-autocomplete.component';
import { ProtocolDefinition, AssetRequirement } from '@features/protocols/models/protocol.models';
import { Resource } from '@features/assets/models/asset.models';
import { AssetService } from '@features/assets/services/asset.service';

export interface GuidedSetupData {
  protocol: ProtocolDefinition;
  deckResource?: any; // strict type would be better but avoiding import cycles
  assetMap?: Record<string, Resource>;
}

export interface GuidedSetupResult {
  assetMap: Record<string, Resource>; // Map requirement accession_id -> Inventory Resource
}

@Component({
  selector: 'app-guided-setup',
  standalone: true,
  imports: [
    MatDialogModule,
    MatButtonModule,
    MatSelectModule,
    MatIconModule,
    MatTooltipModule,
    MatChipsModule,
    FormsModule,
    AriaSelectComponent,
    AriaAutocompleteComponent
  ],
  template: `
    @if (!isInline) {
      <h2 mat-dialog-title>Deck Setup: {{ data?.protocol?.name }}</h2>
    }
    <mat-dialog-content [class.inline-content]="isInline">
      @if (!isInline) {
        <p class="description">
          Please assign inventory items to the required assets for this protocol.
          We've auto-selected matches where possible.
        </p>
      }

      <!-- Loading state -->
      @if (isLoading()) {
        <div class="loading-state">
          <mat-icon class="animate-spin">sync</mat-icon>
          <span>Loading inventory...</span>
        </div>
      } @else if (inventory().length === 0) {
        <div class="empty-state">
          <mat-icon>inventory_2</mat-icon>
          <span>No resources in inventory. Add resources from the Assets page first.</span>
        </div>
      } @else {
        <div class="requirements-list">
          @for (req of requiredAssets; track req.accession_id) {
            <div class="requirement-item" [class.autofilled]="isAutofilled(req.accession_id)" [class.unassigned]="!selectedAssets()[req.accession_id]">
              <div class="req-info">
                <div class="req-header">
                  <span class="req-name">{{ req.name }}</span>
                  @if (isAutofilled(req.accession_id)) {
                    <span class="autofill-badge" matTooltip="Auto-matched based on resource type">
                      <mat-icon class="autofill-icon">auto_awesome</mat-icon>
                      Auto
                    </span>
                  }
                  @if (req.optional) {
                    <span class="optional-badge">Optional</span>
                  }
                </div>
                <span class="req-type">{{ req.type_hint_str || 'Generic Resource' }}</span>
                @if (req.fqn) {
                  <span class="req-fqn" matTooltip="{{ req.fqn }}">{{ getShortFqn(req.fqn) }}</span>
                }
              </div>

              <div class="resource-select">
                <label class="text-xs font-medium text-gray-500 mb-1 block">Select Inventory Item</label>
                <app-aria-autocomplete
                  label="Select Inventory Item"
                  [options]="requirementsOptions()[req.accession_id] || []"
                  [ngModel]="selectedAssets()[req.accession_id]"
                  (ngModelChange)="updateSelection(req.accession_id, $event)"
                  [placeholder]="'Search inventory...'"
                ></app-aria-autocomplete>
                @if (!req.optional && !selectedAssets()[req.accession_id]) {
                  <div class="text-xs text-red-500 mt-1">Required</div>
                }
              </div>
            </div>
          }
        </div>

        <!-- Summary -->
        <div class="summary">
          <div class="summary-item">
            <mat-icon [class.text-green]="autofilledCount() > 0">auto_awesome</mat-icon>
            <span>{{ autofilledCount() }} auto-filled</span>
          </div>
          <div class="summary-item">
            <mat-icon [class.text-amber]="unassignedCount() > 0" [class.text-green]="unassignedCount() === 0">
              {{ unassignedCount() === 0 ? 'check_circle' : 'warning' }}
            </mat-icon>
            <span>{{ unassignedCount() }} unassigned</span>
          </div>
        </div>
      }
    </mat-dialog-content>

    @if (!isInline) {
      <mat-dialog-actions align="end">
        <button mat-button mat-dialog-close>Cancel</button>
        <button
          mat-raised-button
          color="primary"
          [disabled]="!isValid()"
          (click)="confirm()">
          Confirm Setup
        </button>
      </mat-dialog-actions>
    }
  `,
  styles: [`
    .description {
      color: var(--sys-on-surface-variant);
      margin-bottom: 24px;
    }
    .loading-state, .empty-state {
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      padding: 48px 24px;
      gap: 16px;
      color: var(--sys-on-surface-variant);
    }
    .inline-content {
      padding: 0 !important;
      max-height: none !important;
      overflow: visible !important;
    }
    .loading-state mat-icon, .empty-state mat-icon {
      font-size: 48px;
      width: 48px;
      height: 48px;
      opacity: 0.5;
    }
    .animate-spin {
      animation: spin 1s linear infinite;
    }
    @keyframes spin {
      from { transform: rotate(0deg); }
      to { transform: rotate(360deg); }
    }
    .requirements-list {
      display: flex;
      flex-direction: column;
      gap: 16px;
    }
    .requirement-item {
      display: grid;
      grid-template-columns: 1fr 240px;
      gap: 16px;
      align-items: center;
      padding: 12px 16px;
      background: var(--sys-surface-container);
      border-radius: 12px;
      border: 2px solid transparent;
      transition: all 0.2s ease;
    }
    .requirement-item.autofilled {
      border-color: rgba(34, 197, 94, 0.3);
      background: rgba(34, 197, 94, 0.05);
    }
    .requirement-item.unassigned {
      border-color: rgba(251, 191, 36, 0.3);
      background: rgba(251, 191, 36, 0.05);
    }
    .req-info {
      display: flex;
      flex-direction: column;
      gap: 4px;
    }
    .req-header {
      display: flex;
      align-items: center;
      gap: 8px;
      flex-wrap: wrap;
    }
    .req-name {
      font-weight: 600;
      font-size: 1rem;
    }
    .autofill-badge {
      display: inline-flex;
      align-items: center;
      gap: 4px;
      font-size: 0.7rem;
      font-weight: 600;
      text-transform: uppercase;
      padding: 2px 8px;
      border-radius: 12px;
      background: rgba(34, 197, 94, 0.15);
      color: rgb(34, 197, 94);
    }
    .autofill-icon {
      font-size: 14px !important;
      width: 14px !important;
      height: 14px !important;
    }
    .optional-badge {
      font-size: 0.7rem;
      font-weight: 500;
      text-transform: uppercase;
      padding: 2px 8px;
      border-radius: 12px;
      background: var(--sys-surface-variant);
      color: var(--sys-on-surface-variant);
    }
    .req-type {
      font-size: 0.85em;
      color: var(--sys-on-surface-variant);
    }
    .req-fqn {
      font-size: 0.75em;
      color: var(--sys-outline);
      font-family: monospace;
    }
    .resource-select {
      min-width: 240px;
    }
    mat-form-field {
      margin-bottom: -1.25em;
    }
    .option-content {
      display: flex;
      align-items: center;
      gap: 8px;
    }
    .option-name {
      flex: 1;
    }
    .option-id {
      font-size: 0.8em;
      opacity: 0.6;
    }
    .match-icon {
      font-size: 16px !important;
      width: 16px !important;
      height: 16px !important;
      color: rgb(34, 197, 94);
    }
    .suggested-icon {
      font-size: 16px !important;
      width: 16px !important;
      height: 16px !important;
      color: rgb(251, 191, 36);
      margin-right: 4px;
    }
    ::ng-deep .suggested-group .mat-mdc-optgroup-label {
      color: rgb(34, 197, 94) !important;
      font-weight: 600;
    }
    ::ng-deep .suggested-option {
      background: rgba(34, 197, 94, 0.05) !important;
    }
    .summary {
      display: flex;
      gap: 24px;
      justify-content: center;
      margin-top: 24px;
      padding-top: 16px;
      border-top: 1px solid var(--sys-outline-variant);
    }
    .summary-item {
      display: flex;
      align-items: center;
      gap: 8px;
      font-size: 0.9rem;
      color: var(--sys-on-surface-variant);
    }
    .summary-item mat-icon {
      font-size: 20px;
      width: 20px;
      height: 20px;
    }
    .text-green {
      color: rgb(34, 197, 94) !important;
    }
    .text-amber {
      color: rgb(251, 191, 36) !important;
    }
  `]
})
export class GuidedSetupComponent implements OnInit {
  private assetService = inject(AssetService);
  private dialogRef = inject(MatDialogRef<GuidedSetupComponent>, { optional: true });

  // Inline Inputs
  @Input() protocol: ProtocolDefinition | null = null;
  @Input({ transform: booleanAttribute }) isInline = false;
  @Output() selectionChange = new EventEmitter<Record<string, Resource>>();

  inventory = signal<Resource[]>([]);
  selectedAssets = signal<Record<string, Resource | null>>({});
  autofilledIds = signal<Set<string>>(new Set());
  isLoading = signal(true);

  constructor(@Inject(MAT_DIALOG_DATA) @Optional() public data: GuidedSetupData) { }

  get requiredAssets(): AssetRequirement[] {
    return (this.protocol || this.data?.protocol)?.assets || [];
  }

  // Pre-compute options to ensure stable references
  requirementsOptions = computed(() => {
    const map: Record<string, SelectOption[]> = {};
    const inventory = this.inventory();

    this.requiredAssets.forEach(req => {
      map[req.accession_id] = this.generateOptionsForReq(req, inventory);
    });
    return map;
  });

  // Computed signals for summary
  autofilledCount = computed(() => {
    let count = 0;
    const autofilled = this.autofilledIds();
    const selected = this.selectedAssets();
    for (const id of autofilled) {
      if (selected[id]) count++;
    }
    return count;
  });

  unassignedCount = computed(() => {
    return this.requiredAssets.filter(req =>
      !req.optional && !this.selectedAssets()[req.accession_id]
    ).length;
  });

  ngOnInit() {
    this.assetService.getResources().subscribe({
      next: (resources) => {
        this.inventory.set(resources);
        this.autoSelect();
        this.isLoading.set(false);
      },
      error: (err) => {
        console.error('Failed to load inventory:', err);
        this.isLoading.set(false);
      }
    });
  }

  autoSelect() {
    const map: Record<string, Resource | null> = {};
    const autofilled = new Set<string>();
    const usedResourceIds = new Set<string>();

    this.requiredAssets.forEach(req => {
      // Find compatible resources sorted by match quality
      const candidates = this.getCompatibleResources(req);

      // Prioritize exact FQN matches
      const exactMatches = candidates.filter(res => this.isExactMatch(req, res));
      const sortedCandidates = [...exactMatches, ...candidates.filter(res => !this.isExactMatch(req, res))];

      // Find first unused candidate
      const match = sortedCandidates.find(res => !usedResourceIds.has(res.accession_id));

      if (match) {
        map[req.accession_id] = match;
        usedResourceIds.add(match.accession_id);
        autofilled.add(req.accession_id);
      } else {
        map[req.accession_id] = null;
      }
    });

    this.selectedAssets.set(map);
    this.autofilledIds.set(autofilled);

    // Emit if valid so the stepper can proceed
    if (this.isInline && this.isValid()) {
      this.selectionChange.emit(map as Record<string, Resource>);
    }
  }

  /**
   * Get compatible resources for a requirement.
   * Uses multiple matching strategies with priority:
   * 1. Exact FQN match (resource.fqn === req.fqn)
   * 2. FQN class name match (last part of FQN matches)
   * 3. Type hint string match
   * 4. Category/keyword matching
   */
  getCompatibleResources(req: AssetRequirement): Resource[] {
    const reqFqn = (req.fqn || '').toLowerCase();
    const reqType = (req.type_hint_str || '').toLowerCase();
    const reqClassName = this.getClassName(reqFqn);

    return this.inventory().filter(res => {
      const resFqn = (res.fqn || '').toLowerCase();
      const resName = res.name.toLowerCase();
      const resClassName = this.getClassName(resFqn);

      // 1. Exact FQN match
      if (resFqn && reqFqn && resFqn === reqFqn) {
        return true;
      }

      // 2. FQN class name match (e.g., both end with "Plate")
      if (resClassName && reqClassName && resClassName === reqClassName) {
        return true;
      }

      // 3. Type hint match against FQN class name
      if (reqType && resClassName && resClassName.includes(reqType)) {
        return true;
      }

      // 4. Category/keyword matching for common resource types
      if (this.matchesByCategory(reqType, reqClassName, resName, resFqn)) {
        return true;
      }

      return false;
    });
  }

  /**
   * Extract class name from FQN (last part after dot)
   */
  private getClassName(fqn: string): string {
    if (!fqn) return '';
    const parts = fqn.split('.');
    return parts[parts.length - 1] || '';
  }

  /**
   * Category-based matching for common PLR resource types
   */
  private matchesByCategory(reqType: string, reqClassName: string, resName: string, resFqn: string): boolean {
    const combined = `${reqType} ${reqClassName}`.toLowerCase();
    const resNameLower = resName.toLowerCase();
    const resFqnLower = resFqn.toLowerCase();

    // Plate matching
    if ((combined.includes('plate') || combined.includes('microplate')) &&
      (resNameLower.includes('plate') || resFqnLower.includes('plate'))) {
      return true;
    }

    // Tip rack matching
    if ((combined.includes('tip') || combined.includes('tiprack')) &&
      (resNameLower.includes('tip') || resFqnLower.includes('tip'))) {
      return true;
    }

    // Trough/reservoir matching
    if ((combined.includes('trough') || combined.includes('reservoir')) &&
      (resNameLower.includes('trough') || resNameLower.includes('reservoir') || resFqnLower.includes('trough'))) {
      return true;
    }

    // Tube/vial matching
    if ((combined.includes('tube') || combined.includes('vial')) &&
      (resNameLower.includes('tube') || resNameLower.includes('vial') || resFqnLower.includes('tube'))) {
      return true;
    }

    // Well plate matching
    if (combined.includes('wellplate') &&
      (resNameLower.includes('plate') || resFqnLower.includes('plate'))) {
      return true;
    }

    return false;
  }

  /**
   * Check if a resource is an exact match for a requirement (by FQN or class name)
   */
  isExactMatch(req: AssetRequirement, res: Resource): boolean {
    const reqFqn = (req.fqn || '').toLowerCase();
    const resFqn = (res.fqn || '').toLowerCase();

    if (resFqn && reqFqn && resFqn === reqFqn) {
      return true;
    }

    const reqClassName = this.getClassName(reqFqn);
    const resClassName = this.getClassName(resFqn);

    return !!(resClassName && reqClassName && resClassName === reqClassName);
  }

  /**
   * Get exact matches (suggested resources) for a requirement
   */
  getExactMatches(req: AssetRequirement): Resource[] {
    return this.getCompatibleResources(req).filter(res => this.isExactMatch(req, res));
  }

  /**
   * Get other compatible resources (non-exact matches)
   */
  getOtherCompatible(req: AssetRequirement): Resource[] {
    return this.getCompatibleResources(req).filter(res => !this.isExactMatch(req, res));
  }

  /**
   * Check if a requirement was auto-filled
   */
  isAutofilled(reqId: string): boolean {
    return this.autofilledIds().has(reqId) && !!this.selectedAssets()[reqId];
  }

  /**
   * Get short FQN for display (last 2-3 parts)
   */
  getShortFqn(fqn: string): string {
    if (!fqn) return '';
    const parts = fqn.split('.');
    return parts.slice(-2).join('.');
  }



  private generateOptionsForReq(req: AssetRequirement, inventory: Resource[]): SelectOption[] {
    // Helper to get compatible resources since we can't call methods easily inside computed
    const compatible = this.getCompatibleResourcesForInventory(req, inventory);

    const exact: Resource[] = [];
    const other: Resource[] = [];

    compatible.forEach(res => {
      if (this.isExactMatch(req, res)) {
        exact.push(res);
      } else {
        other.push(res);
      }
    });

    const options: SelectOption[] = [];

    exact.forEach(res => options.push({
      label: `${res.name} (${res.accession_id.substring(0, 6)})`,
      value: res, // Resource object reference is stable
      icon: 'recommend'
    }));

    other.forEach(res => options.push({
      label: `${res.name} (${res.accession_id.substring(0, 6)})`,
      value: res
    }));

    return options;
  }

  // Refactored to take inventory as arg for computed purity
  private getCompatibleResourcesForInventory(req: AssetRequirement, inventory: Resource[]): Resource[] {
    const reqFqn = (req.fqn || '').toLowerCase();
    const reqType = (req.type_hint_str || '').toLowerCase();
    const reqClassName = this.getClassName(reqFqn);

    return inventory.filter(res => {
      const resFqn = (res.fqn || '').toLowerCase();
      const resName = res.name.toLowerCase();
      const resClassName = this.getClassName(resFqn);

      if (resFqn && reqFqn && resFqn === reqFqn) return true;
      if (resClassName && reqClassName && resClassName === reqClassName) return true;
      if (reqType && resClassName && resClassName.includes(reqType)) return true;
      if (this.matchesByCategory(reqType, reqClassName, resName, resFqn)) return true;

      return false;
    });
  }

  updateSelection(reqId: string, resource: Resource | null) {
    this.selectedAssets.update(current => ({
      ...current,
      [reqId]: resource
    }));

    // Emit change if inline
    if (this.isInline) {
      if (this.isValid()) {
        this.selectionChange.emit(this.selectedAssets() as Record<string, Resource>);
      } else {
        // Optionally emit partial or handle invalid state
      }
    }

    // If manually changed, remove from autofilled set
    if (this.autofilledIds().has(reqId)) {
      this.autofilledIds.update(set => {
        const newSet = new Set(set);
        newSet.delete(reqId);
        return newSet;
      });
    }
  }

  isValid(): boolean {
    // Check if all required assets have a selection
    return this.requiredAssets.every(req =>
      req.optional ? true : !!this.selectedAssets()[req.accession_id]
    );
  }

  confirm() {
    const result: GuidedSetupResult = {
      assetMap: this.selectedAssets() as Record<string, Resource>
    };
    this.selectionChange.emit(result.assetMap);
    if (this.dialogRef) {
      this.dialogRef.close(result);
    }
  }

  compareResources(o1: Resource, o2: Resource): boolean {
    return o1 && o2 ? o1.accession_id === o2.accession_id : o1 === o2;
  }
}
