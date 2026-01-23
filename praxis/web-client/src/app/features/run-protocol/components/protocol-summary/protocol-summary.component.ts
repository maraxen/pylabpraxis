import { ChangeDetectionStrategy, Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatIconModule } from '@angular/material/icon';
import { MatDividerModule } from '@angular/material/divider';
import { ProtocolDefinition } from '@features/protocols/models/protocol.models';

@Component({
  selector: 'app-protocol-summary',
  standalone: true,
  imports: [CommonModule, MatIconModule, MatDividerModule],
  template: `
    <div class="summary-container space-y-6">
      <!-- Protocol Header -->
      @if (protocol) {
        <div class="p-4 bg-primary/5 rounded-2xl border border-primary/20 flex items-center justify-between">
          <div class="flex items-center gap-4">
            <div class="w-10 h-10 rounded-xl bg-primary/10 flex items-center justify-center">
              <mat-icon class="text-primary">description</mat-icon>
            </div>
            <div class="flex flex-col">
              <h3 class="text-lg font-bold text-sys-text-primary leading-none mb-1">{{ protocol.name }}</h3>
              <span class="text-xs text-sys-text-tertiary">Version {{ protocol.version || '1.0.0' }}</span>
            </div>
          </div>
          <div class="px-3 py-1 bg-surface-variant rounded-lg border border-[var(--theme-border)]">
             <span class="text-[10px] font-bold text-sys-text-tertiary uppercase tracking-widest">Read Only Review</span>
          </div>
        </div>
      }

      <div class="grid grid-cols-1 gap-6">
        <!-- Parameters Summary -->
        <section class="summary-section">
          <h4 class="text-sm font-bold text-sys-text-tertiary uppercase tracking-wider mb-3 flex items-center gap-2">
            <mat-icon class="!w-4 !h-4 !text-[16px]">tune</mat-icon> Parameters
          </h4>
          <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
            @for (item of displayParameters; track item.key) {
              <div class="flex flex-col p-3 bg-surface-variant/50 rounded-xl border border-[var(--theme-border)]">
                <span class="text-xs text-sys-text-tertiary mb-1">{{ formatLabel(item.key) }}</span>
                <span class="text-sm font-medium text-sys-text-primary">{{ formatValue(item.value) }}</span>
              </div>
            } @empty {
              <p class="text-sm text-sys-text-tertiary italic">No parameters configured</p>
            }
          </div>
        </section>

        <!-- Asset Summary -->
        <section class="summary-section">
          <h4 class="text-sm font-bold text-sys-text-tertiary uppercase tracking-wider mb-3 flex items-center gap-2">
            <mat-icon class="!w-4 !h-4 !text-[16px]">inventory_2</mat-icon> Required Assets
          </h4>
          <div class="space-y-2">
            @for (item of displayAssets; track item.id) {
              <div class="flex items-center justify-between p-3 bg-surface-variant/50 rounded-xl border border-[var(--theme-border)]">
                <div class="flex items-center gap-3">
                  <mat-icon class="text-primary/70">inventory</mat-icon>
                  <div class="flex flex-col">
                    <span class="text-sm font-medium text-sys-text-primary">{{ item.name }}</span>
                    <span class="text-xs text-sys-text-tertiary">{{ item.id }}</span>
                  </div>
                </div>
                <span class="px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-tighter"
                      [style]="{
                        'background-color': 'var(--theme-status-success-muted)',
                        'color': 'var(--theme-status-success)',
                        'border': '1px solid var(--theme-status-success-border)'
                      }">Allocated</span>
              </div>
            } @empty {
              <p class="text-sm text-sys-text-tertiary italic">No specific assets required</p>
            }
          </div>
        </section>

        <!-- Well Selections Summary -->
        <section class="summary-section">
          <h4 class="text-sm font-bold text-sys-text-tertiary uppercase tracking-wider mb-3 flex items-center gap-2">
            <mat-icon class="!w-4 !h-4 !text-[16px]">grid_on</mat-icon> Well Selections
          </h4>
          <div class="space-y-3">
            @for (item of displayWellSelections; track item.key) {
              <div class="p-3 bg-surface-variant/50 rounded-xl border border-[var(--theme-border)]">
                <div class="flex items-center justify-between mb-2">
                  <span class="text-xs text-sys-text-tertiary">{{ formatLabel(item.key) }}</span>
                  <span class="text-xs font-bold text-primary">{{ item.wells.length }} Wells</span>
                </div>
                <div class="flex flex-wrap gap-1">
                  @for (well of item.wells.slice(0, 12); track well) {
                    <span class="px-1.5 py-0.5 bg-primary/10 text-primary text-[10px] rounded border border-primary/20">{{ well }}</span>
                  }
                  @if (item.wells.length > 12) {
                    <span class="text-[10px] text-sys-text-tertiary px-1">...and {{ item.wells.length - 12 }} more</span>
                  }
                </div>
              </div>
            } @empty {
               @if (wellSelectionRequired) {
                  <p class="text-sm italic" [style.color]="'var(--status-error)'">No wells selected (required)</p>
               } @else {
                  <p class="text-sm text-sys-text-tertiary italic">No well selection required</p>
               }
            }
          </div>
        </section>
      </div>
    </div>
  `,
  styles: [`
    :host {
      display: block;
      width: 100%;
    }
  `],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class ProtocolSummaryComponent {
  @Input() protocol: ProtocolDefinition | null = null;
  @Input() parameters: Record<string, any> = {};
  @Input() assets: Record<string, any> = {};
  @Input() wellSelections: Record<string, string[]> = {};
  @Input() wellSelectionRequired = false;

  get displayParameters() {
    return Object.entries(this.parameters)
      .filter(([key]) => !this.isWellParameterName(key) && !this.isAssetKey(key))
      .map(([key, value]) => ({ key, value }));
  }

  get displayAssets() {
    return Object.entries(this.assets).map(([id, asset]) => ({
      id,
      name: (asset as any)?.name || id
    }));
  }

  get displayWellSelections() {
    return Object.entries(this.wellSelections).map(([key, wells]) => ({ key, wells }));
  }

  formatLabel(name: string): string {
    return name
      .replace(/_/g, ' ')
      .replace(/\b\w/g, c => c.toUpperCase());
  }

  formatValue(value: any): string {
    if (value === null || value === undefined) return 'None';
    if (typeof value === 'boolean') return value ? 'Yes' : 'No';
    return String(value);
  }

  private isWellParameterName(key: string): boolean {
    const name = key.toLowerCase();
    return ['well', 'wells', 'source_wells', 'target_wells', 'well_ids'].some(p => name.includes(p));
  }

  private isAssetKey(key: string): boolean {
    // Check if key is in assets record (which uses accession_ids)
    return !!this.assets[key];
  }
}
