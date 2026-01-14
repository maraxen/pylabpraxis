import { Component, ChangeDetectionStrategy, Input } from '@angular/core';
import { CommonModule } from '@angular/common';
import { PlrResourceDetails } from '@core/models/plr.models';

@Component({
  selector: 'app-resource-inspector-panel',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div class="h-full flex flex-col p-4 bg-[var(--mat-sys-surface-container)]">
      <h3 class="text-sm font-semibold text-[var(--mat-sys-on-surface-variant)] uppercase tracking-wider mb-4">
        Resource Inspector
      </h3>

      @if (resource) {
        <div class="flex-grow flex flex-col overflow-auto">
          <div class="flex items-start justify-between mb-4">
            <div class="flex flex-col">
              <span class="text-lg font-bold text-[var(--mat-sys-on-surface)] leading-tight">
                {{ resource.name }}
              </span>
              <span class="text-xs font-medium text-[var(--mat-sys-on-surface-variant)] uppercase tracking-wide">
                {{ resource.type }}
              </span>
            </div>
          </div>

          <div class="space-y-4">
            <!-- Location & Slot -->
            <div class="grid grid-cols-2 gap-4">
              <div class="flex flex-col">
                <span class="text-xs text-[var(--mat-sys-on-surface-variant)]">Slot / Location</span>
                <span class="text-sm font-medium text-[var(--mat-sys-on-surface)]">
                  {{ resource.slotId || 'None' }}
                </span>
              </div>
              @if (resource.parentName) {
                <div class="flex flex-col">
                  <span class="text-xs text-[var(--mat-sys-on-surface-variant)]">Parent</span>
                  <span class="text-sm font-medium text-[var(--mat-sys-on-surface)] truncate">
                    {{ resource.parentName }}
                  </span>
                </div>
              }
            </div>

            <!-- Dimensions -->
            <div class="flex flex-col">
              <span class="text-xs text-[var(--mat-sys-on-surface-variant)]">Dimensions (mm)</span>
              <span class="text-sm font-medium text-[var(--mat-sys-on-surface)]">
                {{ resource.dimensions.x | number:'1.1-1' }} × {{ resource.dimensions.y | number:'1.1-1' }} × {{ resource.dimensions.z | number:'1.1-1' }}
              </span>
            </div>

            <!-- Liquid/Tips -->
            @if (resource.volume !== undefined || resource.hasTip !== undefined) {
              <div class="pt-4 border-t border-[var(--mat-sys-outline-variant)]">
                <div class="grid grid-cols-2 gap-4">
                  @if (resource.volume !== undefined) {
                    <div class="flex flex-col">
                      <span class="text-xs text-[var(--mat-sys-on-surface-variant)]">Volume</span>
                      <div class="flex items-baseline gap-1">
                        <span class="text-sm font-bold text-primary">
                          {{ resource.volume | number:'1.0-1' }}
                        </span>
                        <span class="text-[10px] text-[var(--mat-sys-on-surface-variant)]">/ {{ resource.maxVolume || '?' }} µL</span>
                      </div>
                    </div>
                  }
                  @if (resource.hasTip !== undefined) {
                    <div class="flex flex-col">
                      <span class="text-xs text-[var(--mat-sys-on-surface-variant)]">Tip Status</span>
                      <span
                        class="text-sm font-bold"
                        [class.text-amber-500]="resource.hasTip"
                        [class.text-[var(--mat-sys-on-surface-variant)]]="!resource.hasTip"
                      >
                        {{ resource.hasTip ? 'PRESENT' : 'EMPTY' }}
                      </span>
                    </div>
                  }
                </div>
              </div>
            }
          </div>
        </div>
      } @else {
        <div class="flex-grow flex flex-col items-center justify-center text-[var(--mat-sys-on-surface-variant)] italic text-sm">
          <p>Click a resource on the deck to inspect</p>
        </div>
      }
    </div>
  `,
  styles: [`
    :host {
      display: block;
      height: 100%;
    }
  `],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class ResourceInspectorPanelComponent {
  @Input() resource: PlrResourceDetails | undefined;
}