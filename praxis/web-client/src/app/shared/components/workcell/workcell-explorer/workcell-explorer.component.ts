import { Component, output, signal, computed, ChangeDetectionStrategy, Input } from '@angular/core';
import { CommonModule } from '@angular/common';
import { WorkcellGroup, MachineWithRuntime } from '@features/workcell/models/workcell-view.models';
import { WorkcellGroupComponent } from './workcell-group/workcell-group.component';

@Component({
  selector: 'app-workcell-explorer',
  imports: [CommonModule, WorkcellGroupComponent],
  template: `
    <div class="flex flex-col h-full glass-panel border-r border-[var(--theme-border)]">
      <!-- Search Header -->
      <div class="p-4 border-b border-[var(--theme-border)]">
        <div class="relative">
          <input
            type="text"
            placeholder="Search machines..."
            class="w-full rounded-md border border-[var(--theme-border)] bg-[var(--mat-sys-surface-container)] py-2 pl-9 pr-4 text-sm text-sys-text-primary placeholder-sys-text-tertiary focus:border-primary focus:outline-none focus:ring-1 focus:ring-primary"
            [value]="searchQuery()"
            (input)="updateSearch($event)"
          />
          <div class="absolute inset-y-0 left-0 flex items-center pl-3 pointer-events-none">
            <svg class="h-4 w-4 text-sys-text-tertiary" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
          </div>
        </div>
      </div>

      <!-- Content -->
      <div class="flex-grow overflow-y-auto p-2">
        @if (filteredGroups().length === 0) {
          <div class="p-4 text-center text-sm text-sys-text-tertiary">
            No machines found matching "{{ searchQuery() }}"
          </div>
        } @else {
          @for (group of filteredGroups(); track group.workcell?.accession_id || 'unassigned') {
            <app-workcell-group
              [group]="group"
              (machineSelect)="onMachineSelect($event)"
            />
          }
        }
      </div>

      <!-- Footer Actions (Optional/Future) -->
      <!-- 
      <div class="p-4 border-t border-slate-200 dark:border-slate-800">
        <button class="w-full flex items-center justify-center gap-2 rounded-md border border-slate-300 bg-white px-4 py-2 text-sm font-medium text-slate-700 shadow-sm hover:bg-slate-50 dark:border-slate-700 dark:bg-slate-800 dark:text-slate-200 dark:hover:bg-slate-700">
          Add Machine
        </button>
      </div> 
      -->
    </div>
  `,
  styles: [`
    :host { display: block; height: 100%; }
    .glass-panel {
      background: color-mix(in srgb, var(--mat-sys-surface-container-low) 85%, transparent);
      backdrop-filter: blur(12px);
      -webkit-backdrop-filter: blur(12px);
    }
  `],
  changeDetection: ChangeDetectionStrategy.OnPush
})
export class WorkcellExplorerComponent {
  @Input({ required: true }) set groups(value: WorkcellGroup[]) {
    this.groupsSignal.set(value);
  }
  get groups() {
    return this.groupsSignal();
  }
  private groupsSignal = signal<WorkcellGroup[]>([]);
  
  machineSelect = output<MachineWithRuntime>();
  
  searchQuery = signal('');

  filteredGroups = computed(() => {
    const query = this.searchQuery().toLowerCase().trim();
    const allGroups = this.groupsSignal();

    if (!query) {
      return allGroups;
    }

    // Filter logic
    return allGroups.map(group => {
      // Check if group name matches
      const groupName = group.workcell?.name?.toLowerCase() || 'unassigned';
      const hasGroupMatch = groupName.includes(query);

      // Check if any machines match
      const matchingMachines = group.machines.filter(m => 
        m.name.toLowerCase().includes(query) || 
        m.machine_type?.toLowerCase().includes(query)
      );

      if (hasGroupMatch) {
        // If group matches, return group with ALL machines, fully expanded
        return { ...group, isExpanded: true };
      } else if (matchingMachines.length > 0) {
        // If machines match, return group with ONLY matching machines, expanded
        return { ...group, machines: matchingMachines, isExpanded: true };
      }

      return null;
    }).filter((g): g is WorkcellGroup => g !== null);
  });

  updateSearch(event: Event) {
    const input = event.target as HTMLInputElement;
    this.searchQuery.set(input.value);
  }

  onMachineSelect(machine: MachineWithRuntime) {
    this.machineSelect.emit(machine);
  }
}
