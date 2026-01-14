import { Component, OnInit, inject, signal, ChangeDetectionStrategy, computed } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatIconModule } from '@angular/material/icon';
import { WorkcellViewService } from '../services/workcell-view.service';
import { WorkcellExplorerComponent } from '../../../shared/components/workcell/workcell-explorer/workcell-explorer.component';
import { MachineCardComponent } from '../../../shared/components/workcell/machine-card/machine-card.component';
import { MachineCardMiniComponent } from '../../../shared/components/workcell/machine-card/machine-card-mini.component';
import { MachineFocusViewComponent } from '../machine-focus-view/machine-focus-view.component';
import { MachineWithRuntime } from '../models/workcell-view.models';

@Component({
  selector: 'app-workcell-dashboard',
  imports: [
    CommonModule, 
    MatIconModule,
    WorkcellExplorerComponent, 
    MachineCardComponent, 
    MachineCardMiniComponent,
    MachineFocusViewComponent
  ],
  template: `
    <div class="flex h-full w-full overflow-hidden bg-slate-50 dark:bg-slate-900">
      <!-- Sidebar -->
      <aside class="w-[280px] flex-shrink-0 border-r border-slate-200 bg-white dark:border-slate-800 dark:bg-slate-950">
        <div class="flex h-full flex-col">
          <div class="flex-grow p-0 overflow-hidden">
             <app-workcell-explorer 
                [groups]="workcellGroups()"
                (machineSelect)="onMachineSelected($event)"
             />
          </div>
        </div>
      </aside>

      <!-- Main Canvas -->
      <main class="flex flex-col flex-grow relative overflow-hidden">
        <!-- Header/Controls - Hidden in Focus Mode -->
        @if (viewMode() !== 'focus') {
          <header class="flex items-center justify-between px-6 py-4 bg-white border-b border-slate-200 dark:bg-slate-950 dark:border-slate-800">
            <div class="flex items-center gap-4">
              <h1 class="text-xl font-bold text-slate-900 dark:text-white">Workcell Dashboard</h1>
              @if (isLoading()) {
                <span class="text-xs text-slate-400 animate-pulse">Loading...</span>
              }
            </div>

            <div class="flex items-center bg-slate-100 dark:bg-slate-800 p-1 rounded-lg">
              <button
                (click)="setViewMode('grid')"
                [class.bg-white]="viewMode() === 'grid'"
                [class.shadow-sm]="viewMode() === 'grid'"
                [class.dark:bg-slate-700]="viewMode() === 'grid'"
                class="px-3 py-1 text-sm rounded-md transition-all"
              >
                Grid
              </button>
              <button
                (click)="setViewMode('list')"
                [class.bg-white]="viewMode() === 'list'"
                [class.shadow-sm]="viewMode() === 'list'"
                [class.dark:bg-slate-700]="viewMode() === 'list'"
                class="px-3 py-1 text-sm rounded-md transition-all"
              >
                List
              </button>
            </div>
          </header>
        }

        <!-- Canvas Content -->
        <div class="flex-grow overflow-auto" [class.p-6]="viewMode() !== 'focus'">
          @if (isLoading()) {
            <div class="flex items-center justify-center h-full">
               <div class="w-8 h-8 border-4 border-primary border-t-transparent rounded-full animate-spin"></div>
            </div>
          } @else {
            @switch (viewMode()) {
              @case ('grid') {
                <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6 fade-in">
                  @for (machine of allMachines(); track machine.accession_id) {
                    <app-machine-card 
                      [machine]="machine"
                      (machineSelected)="onMachineSelected($event)">
                    </app-machine-card>
                  } @empty {
                    <div class="col-span-full flex flex-col items-center justify-center py-20 text-slate-400">
                      <mat-icon class="text-6xl mb-4 text-slate-300">precision_manufacturing</mat-icon>
                      <p>No machines found</p>
                    </div>
                  }
                </div>
              }
              @case ('list') {
                <div class="flex flex-col gap-4 fade-in">
                  @for (machine of allMachines(); track machine.accession_id) {
                    <app-machine-card-mini 
                      [machine]="machine"
                      (machineSelected)="onMachineSelected($event)">
                    </app-machine-card-mini>
                  } @empty {
                    <div class="flex flex-col items-center justify-center py-20 text-slate-400">
                      <p>No machines found</p>
                    </div>
                  }
                </div>
              }
              @case ('focus') {
                @if (selectedMachine(); as machine) {
                  <app-machine-focus-view 
                    [machine]="machine"
                    (back)="setViewMode('grid')"
                  ></app-machine-focus-view>
                } @else {
                  <div class="flex flex-col items-center justify-center h-full text-slate-400 fade-in">
                    <mat-icon class="text-6xl mb-4">select_all</mat-icon>
                    <p>Select a machine from the explorer to focus</p>
                  </div>
                }
              }
            }
          }
        </div>
      </main>
    </div>
  `,
  styles: [`
    :host {
      display: block;
      height: 100%;
    }
    .fade-in {
      animation: fadeIn 0.3s ease-out;
    }
    @keyframes fadeIn {
      from { opacity: 0; transform: translateY(10px); }
      to { opacity: 1; transform: translateY(0); }
    }
  `],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class WorkcellDashboardComponent implements OnInit {
  private workcellService = inject(WorkcellViewService);

  // Layout state
  viewMode = signal<'grid' | 'list' | 'focus'>('grid');
  isLoading = signal<boolean>(true);

  // Access service state for template
  workcellGroups = this.workcellService.workcellGroups;
  selectedMachine = this.workcellService.selectedMachine;

  // Flattened machines for grid/list views
  allMachines = computed(() => {
    return this.workcellGroups().flatMap(group => group.machines);
  });

  ngOnInit(): void {
    this.workcellService.loadWorkcellGroups().subscribe({
      next: () => this.isLoading.set(false),
      error: (err) => {
        console.error('Failed to load workcells', err);
        this.isLoading.set(false);
      }
    });
  }

  setViewMode(mode: 'grid' | 'list' | 'focus') {
    this.viewMode.set(mode);
  }

  onMachineSelected(machine: MachineWithRuntime) {
    this.workcellService.selectedMachine.set(machine);
    this.viewMode.set('focus');
  }
}


  