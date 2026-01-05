import { Component, Input, ChangeDetectionStrategy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatChipsModule } from '@angular/material/chips';
import { MatTooltipModule } from '@angular/material/tooltip';
import { ResourceDefinition } from '../../models/asset.models';
import { parseResourceInfo, formatVolume, formatItemCount, ParsedResourceInfo } from '../../utils/resource-name-parser';
import { getSubCategory } from '../../utils/resource-category-groups';

/**
 * Reusable component that displays resource attributes as chips.
 * Extracts info from ResourceDefinition metadata and parses name as fallback.
 */
@Component({
    selector: 'app-resource-chips',
    standalone: true,
    imports: [CommonModule, MatChipsModule, MatTooltipModule],
    template: `
    @if (parsed) {
      <div class="chip-row">
        <!-- Item Count (wells, tips, slots) -->
        @if (itemCountLabel) {
          <mat-chip class="info-chip count" [matTooltip]="itemCountTooltip">
            {{ itemCountLabel }}
          </mat-chip>
        }
        
        <!-- Volume -->
        @if (volumeLabel) {
          <mat-chip class="info-chip volume" [matTooltip]="volumeTooltip">
            {{ volumeLabel }}
          </mat-chip>
        }
        
        <!-- Bottom Type (plates) -->
        @if (parsed.bottomType) {
          <mat-chip class="info-chip bottom" matTooltip="Well bottom type">
            {{ parsed.bottomType }}
          </mat-chip>
        }
        
        <!-- Slot Type (carriers) -->
        @if (parsed.slotType) {
          <mat-chip class="info-chip slot" matTooltip="Slot type">
            {{ parsed.slotType }}
          </mat-chip>
        }
        
        <!-- Vendor -->
        @if (showVendor && parsed.vendor) {
          <mat-chip class="info-chip vendor" matTooltip="Vendor">
            {{ parsed.vendor }}
          </mat-chip>
        }
        
        <!-- Display Name (semantic type) -->
        @if (showDisplayName && parsed.displayName) {
          <mat-chip class="info-chip type" matTooltip="Type">
            {{ parsed.displayName }}
          </mat-chip>
        }
        
        <!-- PLR Name (optional toggle) -->
        @if (showPlrName) {
          <span class="plr-name" matTooltip="PyLabRobot identifier">
            [PLR: {{ parsed.rawName }}]
          </span>
        }
      </div>
    }
  `,
    styles: [`
    .chip-row {
      display: flex;
      flex-wrap: wrap;
      gap: 4px;
      align-items: center;
    }
    
    .info-chip {
      --mdc-chip-container-height: 22px;
      font-size: 0.7rem;
      font-weight: 500;
    }
    
    .info-chip.count {
      --mdc-chip-elevated-container-color: var(--mat-sys-primary-container);
      --mdc-chip-label-text-color: var(--mat-sys-on-primary-container);
    }
    
    .info-chip.volume {
      --mdc-chip-elevated-container-color: var(--mat-sys-secondary-container);
      --mdc-chip-label-text-color: var(--mat-sys-on-secondary-container);
    }
    
    .info-chip.vendor {
      --mdc-chip-elevated-container-color: var(--mat-sys-surface-container-high);
      --mdc-chip-label-text-color: var(--mat-sys-on-surface-variant);
    }
    
    .info-chip.type,
    .info-chip.bottom,
    .info-chip.slot {
      --mdc-chip-elevated-container-color: var(--mat-sys-tertiary-container);
      --mdc-chip-label-text-color: var(--mat-sys-on-tertiary-container);
    }
    
    .plr-name {
      font-size: 0.65rem;
      color: var(--mat-sys-on-surface-variant);
      font-family: monospace;
      opacity: 0.7;
    }
  `],
    changeDetection: ChangeDetectionStrategy.OnPush,
})
export class ResourceChipsComponent {
    @Input() definition!: ResourceDefinition;
    @Input() showVendor = true;
    @Input() showDisplayName = false;
    @Input() showPlrName = false;

    parsed: ParsedResourceInfo | null = null;
    itemCountLabel: string | null = null;
    volumeLabel: string | null = null;
    itemCountTooltip = '';
    volumeTooltip = '';

    ngOnChanges() {
        if (this.definition) {
            this.parsed = parseResourceInfo(this.definition);
            const category = getSubCategory(this.definition.plr_category);

            this.itemCountLabel = formatItemCount(this.parsed.itemCount, category);
            this.volumeLabel = formatVolume(this.parsed.volumeUl);

            // Tooltips
            if (category.includes('tip')) {
                this.itemCountTooltip = 'Number of tips';
                this.volumeTooltip = 'Maximum tip volume';
            } else if (category.includes('carrier')) {
                this.itemCountTooltip = 'Number of slots';
                this.volumeTooltip = '';
            } else {
                this.itemCountTooltip = 'Number of wells';
                this.volumeTooltip = 'Well volume';
            }
        }
    }
}
