import { Component, EventEmitter, Input, OnInit, Output, inject, signal, computed } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormControl, ReactiveFormsModule, FormsModule } from '@angular/forms';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatInputModule } from '@angular/material/input';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatTooltipModule } from '@angular/material/tooltip';
import { MachineDefinition, ResourceDefinition } from '../../../../features/assets/models/asset.models';
import { AssetService } from '../../../../features/assets/services/asset.service';
import { getUiGroup, shouldHideCategory, ResourceUiGroup } from '../../../../features/assets/utils/resource-category-groups';
import { PraxisSelectComponent } from '@shared/components/praxis-select/praxis-select.component';
import { PraxisMultiselectComponent } from '@shared/components/praxis-multiselect/praxis-multiselect.component';

interface FrontendType {
    fqn: string;
    label: string;
    icon: string;
    backendCount: number;
}

@Component({
    selector: 'app-definition-selection-step',
    standalone: true,
    imports: [
        CommonModule,
        ReactiveFormsModule,
        FormsModule,
        MatButtonModule,
        MatIconModule,
        MatInputModule,
        MatFormFieldModule,
        MatTooltipModule,
        PraxisSelectComponent,
        PraxisMultiselectComponent
    ],
    template: `
    <div class="flex flex-col gap-4 py-2 h-full">
      
      <!-- MACHINE SELECTION FLOW -->
      @if (assetType === 'machine') {
        <div class="fade-in flex flex-col gap-4 h-full">
          @if (!selectedMachineFrontend) {
            <div>
              <h3 class="text-sm font-bold uppercase tracking-wider text-sys-text-secondary mb-3">Choose Machine Type</h3>
              <div class="grid grid-cols-2 md:grid-cols-3 gap-3">
                @for (ft of machineFrontendTypes(); track ft.fqn) {
                  <button type="button"
                    class="selection-card !p-3 flex items-center gap-3 text-left transition-all"
                    (click)="selectMachineFrontend(ft)">
                    <div class="icon-chip"><mat-icon>{{ ft.icon }}</mat-icon></div>
                    <div class="flex flex-col min-w-0">
                      <span class="font-medium truncate">{{ ft.label }}</span>
                      <span class="text-[10px] sys-text-secondary">{{ ft.backendCount }} backend(s)</span>
                    </div>
                  </button>
                }
              </div>
            </div>
          } @else {
            <div class="flex flex-col gap-3 h-full">
              <div class="flex items-center gap-2">
                <button mat-icon-button (click)="selectedMachineFrontend = null" class="!w-8 !h-8 !leading-8">
                  <mat-icon class="!text-lg">arrow_back</mat-icon>
                </button>
                <div class="flex flex-col">
                  <h3 class="text-sm font-bold uppercase tracking-wider">{{ selectedMachineFrontend.label }} Backends</h3>
                  <span class="text-xs sys-text-secondary">Select the hardware driver</span>
                </div>
              </div>

              <div class="grid grid-cols-1 md:grid-cols-2 gap-3 overflow-y-auto pr-1 flex-grow">
                @for (def of filteredMachineBackends(); track def.accession_id) {
                  <button type="button"
                    class="selection-card !p-3 flex items-start gap-3 text-left transition-all"
                    [class.card-selected]="selectedDefinition?.accession_id === def.accession_id"
                    (click)="selectDefinition(def)">
                    <div class="icon-chip subtle">
                      <mat-icon>memory</mat-icon>
                    </div>
                    <div class="flex flex-col min-w-0">
                      <div class="flex items-center gap-2">
                        <span class="font-medium truncate" [matTooltip]="def.name">{{ def.name }}</span>
                        @if (isSimulated(def)) {
                          <span class="simulated-pill">Simulated</span>
                        }
                      </div>
                      <span class="text-xs sys-text-secondary">{{ def.manufacturer || 'Unknown vendor' }}</span>
                      <span class="text-[10px] sys-text-secondary truncate">{{ def.fqn }}</span>
                    </div>
                  </button>
                }
              </div>
            </div>
          }
        </div>
      }

      <!-- RESOURCE SELECTION FLOW -->
      @if (assetType === 'resource') {
        <div class="fade-in flex flex-col gap-4 h-full">
          <div class="flex flex-col gap-3">
            <mat-form-field appearance="outline" class="w-full praxis-search-field no-label">
              <mat-icon matPrefix>search</mat-icon>
              <input matInput [formControl]="searchControl" placeholder="Search resources...">
            </mat-form-field>

            <div class="flex flex-wrap gap-2">
              @for (group of resourceGroups; track group) {
                <button type="button"
                  class="filter-chip"
                  [class.active-chip]="resourceCategoryFilters().includes(group)"
                  (click)="toggleResourceCategory(group)">
                  <span>{{ group }}</span>
                </button>
              }
            </div>
          </div>

          <div class="grid grid-cols-1 md:grid-cols-2 gap-3 overflow-y-auto pr-1 flex-grow">
            @for (def of filteredResourceDefinitions(); track def.accession_id) {
              <button type="button"
                class="selection-card !p-3 flex items-start gap-3 text-left transition-all"
                [class.card-selected]="selectedDefinition?.accession_id === def.accession_id"
                (click)="selectDefinition(def)">
                <div class="icon-chip">
                  <mat-icon>science</mat-icon>
                </div>
                <div class="flex flex-col min-w-0">
                  <span class="font-medium truncate" [matTooltip]="def.name">{{ def.name }}</span>
                  <span class="text-xs sys-text-secondary truncate">{{ def.vendor || 'Unknown vendor' }} • {{ def.plr_category }}</span>
                  <span class="text-[10px] sys-text-secondary truncate">{{ def.fqn }}</span>
                </div>
              </button>
            }
            @if (filteredResourceDefinitions().length === 0) {
              <div class="col-span-2 py-12 text-center text-sys-text-secondary">
                <mat-icon class="!text-4xl opacity-20 mb-2">filter_list_off</mat-icon>
                <p>No resources match your search</p>
              </div>
            }
          </div>
        </div>
      }
    </div>
  `,
    styles: [`
    .fade-in { animation: fadeIn 0.25s ease-in-out; }
    @keyframes fadeIn { from { opacity: 0; transform: translateY(4px); } to { opacity: 1; transform: translateY(0); } }

    .selection-card {
      border: 1px solid var(--mat-sys-outline-variant);
      border-radius: 12px;
      background: linear-gradient(135deg, var(--mat-sys-surface) 0%, var(--mat-sys-surface-container-low) 100%);
      cursor: pointer;
    }
    .selection-card:hover {
      border-color: var(--mat-sys-primary);
      box-shadow: 0 4px 12px -8px var(--mat-sys-primary);
    }
    .card-selected {
      border-color: var(--mat-sys-primary);
      background: var(--mat-sys-primary-container);
    }

    .icon-chip {
      width: 36px;
      height: 36px;
      border-radius: 10px;
      background: var(--mat-sys-surface-container-high);
      display: grid;
      place-items: center;
      flex-shrink: 0;
    }
    .icon-chip.subtle { background: var(--mat-sys-surface-container-low); }
    .icon-chip mat-icon { font-size: 20px; width: 20px; height: 20px; }

    .simulated-pill {
      font-size: 9px;
      padding: 1px 6px;
      border-radius: 99px;
      background: var(--mat-sys-tertiary-container);
      color: var(--mat-sys-on-tertiary-container);
      font-weight: 600;
      text-transform: uppercase;
    }

    .filter-chip {
      padding: 6px 12px;
      border-radius: 99px;
      border: 1px solid var(--mat-sys-outline-variant);
      background: var(--mat-sys-surface);
      font-size: 12px;
      cursor: pointer;
      transition: all 0.2s;
    }
    .filter-chip:hover { border-color: var(--mat-sys-primary); }
    .active-chip {
      background: var(--mat-sys-primary-container);
      color: var(--mat-sys-on-primary-container);
      border-color: var(--mat-sys-primary);
    }

    .sys-text-secondary { color: var(--mat-sys-on-surface-variant); }
    .praxis-search-field.no-label ::ng-deep .mat-mdc-form-field-subscript-wrapper { display: none; }
  `]
})
export class DefinitionSelectionStepComponent implements OnInit {
    @Input() assetType: 'machine' | 'resource' | null = null;
    @Output() definitionSelected = new EventEmitter<MachineDefinition | ResourceDefinition>();

    private assetService = inject(AssetService);

    // State
    searchControl = new FormControl('');
    selectedDefinition: MachineDefinition | ResourceDefinition | null = null;
    selectedMachineFrontend: FrontendType | null = null;

    // Data containers
    private allMachineDefinitions = signal<MachineDefinition[]>([]);
    private allResourceDefinitions = signal<ResourceDefinition[]>([]);

    // Machine Selection logic
    machineFrontendTypes = computed(() => {
        const counts = new Map<string, number>();
        this.allMachineDefinitions().forEach(d => {
            if (d.frontend_fqn) counts.set(d.frontend_fqn, (counts.get(d.frontend_fqn) || 0) + 1);
        });

        return Object.entries(this.frontendFqnToLabel).map(([fqn, mapping]) => ({
            fqn,
            label: mapping.label,
            icon: mapping.icon,
            backendCount: counts.get(fqn) || 0
        })).filter(ft => ft.backendCount > 0).sort((a, b) => a.label.localeCompare(b.label));
    });

    filteredMachineBackends = computed(() => {
        if (!this.selectedMachineFrontend) return [];
        return this.allMachineDefinitions().filter(d => d.frontend_fqn === this.selectedMachineFrontend?.fqn);
    });

    // Resource Selection logic
    resourceGroups: ResourceUiGroup[] = ['Carriers', 'Holders', 'Plates', 'TipRacks', 'Containers', 'Other'];
    resourceCategoryFilters = signal<ResourceUiGroup[]>([]);

    filteredResourceDefinitions = computed(() => {
        const term = (this.searchControl.value || '').toLowerCase();
        const categories = this.resourceCategoryFilters();

        return this.allResourceDefinitions().filter(def => {
            const matchText = [def.name, def.vendor, def.plr_category, def.fqn].join(' ').toLowerCase();
            if (term && !matchText.includes(term)) return false;

            if (categories.length > 0) {
                const group = getUiGroup(def.plr_category);
                if (!categories.includes(group)) return false;
            }
            return true;
        });
    });

    private frontendFqnToLabel: Record<string, { label: string, icon: string }> = {
        'pylabrobot.liquid_handling.LiquidHandler': { label: 'Liquid Handler', icon: 'water_drop' },
        'pylabrobot.plate_reading.PlateReader': { label: 'Plate Reader', icon: 'visibility' },
        'pylabrobot.heating_shaking.HeaterShaker': { label: 'Heater Shaker', icon: 'vibration' },
        'pylabrobot.shaking.Shaker': { label: 'Shaker', icon: 'vibration' },
        'pylabrobot.temperature_controlling.TemperatureController': { label: 'Temperature Controller', icon: 'thermostat' },
        'pylabrobot.centrifuging.Centrifuge': { label: 'Centrifuge', icon: 'rotate_right' },
        'pylabrobot.thermocycling.Thermocycler': { label: 'Thermocycler', icon: 'thermostat' },
        'pylabrobot.pumping.Pump': { label: 'Pump', icon: 'air' },
        'pylabrobot.plate_sealing.Sealer': { label: 'Plate Sealer', icon: 'check_box' },
        'pylabrobot.plate_peeling.Peeler': { label: 'Plate Peeler', icon: 'layers_clear' },
        'pylabrobot.powder_dispensing.PowderDispenser': { label: 'Powder Dispenser', icon: 'grain' },
        'pylabrobot.incubating.Incubator': { label: 'Incubator', icon: 'ac_unit' },
        'pylabrobot.scara.SCARA': { label: 'SCARA Robot', icon: 'smart_toy' }
    };

    ngOnInit() {
        this.assetService.getMachineDefinitions().subscribe((defs: MachineDefinition[]) => {
            this.allMachineDefinitions.set(defs.filter((d: MachineDefinition) => d.frontend_fqn));
        });
        this.assetService.getResourceDefinitions().subscribe((defs: ResourceDefinition[]) => {
            this.allResourceDefinitions.set(defs.filter((d: ResourceDefinition) => !shouldHideCategory(d.plr_category)));
        });
    }

    selectMachineFrontend(ft: FrontendType) {
        this.selectedMachineFrontend = ft;
    }

    selectDefinition(def: MachineDefinition | ResourceDefinition) {
        this.selectedDefinition = def;
        this.definitionSelected.emit(def);
    }

    toggleResourceCategory(group: ResourceUiGroup) {
        const current = this.resourceCategoryFilters();
        if (current.includes(group)) {
            this.resourceCategoryFilters.set(current.filter(g => g !== group));
        } else {
            this.resourceCategoryFilters.set([...current, group]);
        }
    }

    isSimulated(def: MachineDefinition): boolean {
        const fqnLower = (def.fqn || '').toLowerCase();
        const nameLower = (def.name || '').toLowerCase();
        return fqnLower.includes('chatterbox') || fqnLower.includes('simulator') || nameLower.includes('simulated');
    }
}
