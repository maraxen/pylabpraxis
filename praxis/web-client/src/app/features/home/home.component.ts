
import { Component, inject, OnInit, OnDestroy, signal, computed } from '@angular/core';

import { RouterLink } from '@angular/router';
import { MatCardModule } from '@angular/material/card';
import { MatIconModule } from '@angular/material/icon';
import { MatButtonModule } from '@angular/material/button';
import { MatProgressBarModule } from '@angular/material/progress-bar';
import { MatChipsModule } from '@angular/material/chips';
import { MatTooltipModule } from '@angular/material/tooltip';
import { MatBadgeModule } from '@angular/material/badge';
import { map, interval, Subscription } from 'rxjs';

import { AssetService } from '../assets/services/asset.service';
import { ProtocolService } from '../protocols/services/protocol.service';
import { ExecutionService } from '../run-protocol/services/execution.service';
import { HardwareDiscoveryButtonComponent } from '@shared/components/hardware-discovery-button/hardware-discovery-button.component';
import { SparklineComponent } from '@shared/components/sparkline/sparkline.component';
import { ModeService } from '@core/services/mode.service';
import { Machine, Resource, MachineStatus } from '../assets/models/asset.models';
import { ProtocolDefinition } from '../protocols/models/protocol.models';
import { ExecutionStatus } from '../run-protocol/models/execution.models';

interface RecentRun {
  id: string;
  name: string;
  protocolName: string;
  status: 'running' | 'completed' | 'failed' | 'pending';
  progress: number;
  startedAt: Date;
  duration?: string;
}

@Component({
  selector: 'app-home',
  standalone: true,
  imports: [
    RouterLink,
    MatCardModule,
    MatIconModule,
    MatButtonModule,
    MatProgressBarModule,
    MatChipsModule,
    MatTooltipModule,
    MatTooltipModule,
    MatBadgeModule,
    HardwareDiscoveryButtonComponent,
    SparklineComponent
  ],
  template: `
    <div class="p-6 max-w-screen-2xl mx-auto" data-tour-id="dashboard-root">
      <!-- Header with Quick Actions -->
      <header class="mb-8 flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div class="greeting">
          <h1 class="text-3xl font-bold text-sys-text-primary mb-1">Welcome back</h1>
          <p class="text-sys-text-secondary">Here's what's happening in your lab</p>
        </div>
        <div class="flex gap-3 w-full md:w-auto">
          <a mat-flat-button class="!bg-gradient-to-br !from-primary !to-primary-dark !text-white !rounded-xl !px-6 !py-6 !font-semibold flex items-center gap-2 flex-1 md:flex-none justify-center shadow-lg shadow-primary/20 hover:shadow-primary/40 transition-all hover:-translate-y-0.5" routerLink="/app/run">
            <mat-icon>play_circle</mat-icon>
            Run Protocol
          </a>
          <app-hardware-discovery-button></app-hardware-discovery-button>
          @if (!modeService.isBrowserMode()) {
            <a mat-stroked-button class="!border-[var(--theme-border)] !text-sys-text-primary !rounded-xl !px-6 !py-6 flex items-center gap-2 flex-1 md:flex-none justify-center hover:bg-[var(--mat-sys-surface-variant)] transition-all" routerLink="/app/protocols">
              <mat-icon>schedule</mat-icon>
              Schedule
            </a>
          }
        </div>
      </header>

      <!-- Stats Overview -->
      <section class="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        <div class="group relative bg-surface border border-[var(--theme-border)] rounded-2xl p-5 flex items-center gap-4 hover:bg-surface-elevated transition-all hover:-translate-y-0.5 cursor-pointer overflow-hidden" routerLink="/app/run" matTooltip="View active protocol runs">
          <!-- Glow effect -->
          <div class="absolute inset-0 bg-gradient-to-br from-primary/5 to-secondary/5 opacity-0 group-hover:opacity-100 transition-opacity duration-500"></div>
          
          <div class="w-12 h-12 rounded-xl flex items-center justify-center bg-gradient-to-br from-primary/20 to-secondary/20 relative z-10">
            <mat-icon class="text-primary">play_arrow</mat-icon>
          </div>
          <div class="flex flex-col relative z-10 flex-1">
            <span class="text-2xl font-bold text-sys-text-primary">{{ runningCount() }}</span>
            <span class="text-xs font-medium text-sys-text-tertiary uppercase tracking-wide">Running</span>
          </div>
          <div class="w-16 h-8 relative z-10">
            <app-sparkline [data]="runTrend()" color="var(--mat-sys-primary)" />
          </div>
          <div class="absolute top-4 right-4 w-2 h-2 bg-green-400 rounded-full animate-pulse shadow-[0_0_8px_rgba(74,222,128,0.6)]"></div>
        </div>

        <div class="group relative bg-surface border border-[var(--theme-border)] rounded-2xl p-5 flex items-center gap-4 hover:bg-surface-elevated transition-all hover:-translate-y-0.5 cursor-pointer overflow-hidden" routerLink="/app/assets" matTooltip="View laboratory machines">
          <div class="w-12 h-12 rounded-xl flex items-center justify-center bg-gradient-to-br from-blue-500/20 to-purple-500/20 relative z-10 shrink-0">
            <mat-icon class="text-blue-400">precision_manufacturing</mat-icon>
          </div>
          <div class="flex flex-col relative z-10 flex-1">
            <span class="text-2xl font-bold text-sys-text-primary">{{ physicalOnlineMachines() }}<span class="text-base font-normal text-sys-text-tertiary">/{{ physicalMachinesCount() }}</span></span>
            <span class="text-[10px] font-medium text-sys-text-tertiary uppercase tracking-wide">Physical Hardware</span>
          </div>
          <!-- Simulated Counter Mini -->
          <div class="flex flex-col items-end relative z-10 opacity-60">
            <span class="text-sm font-bold text-sys-text-secondary">{{ simulatedOnlineMachines() }}/{{ simulatedMachinesCount() }}</span>
            <span class="text-[8px] uppercase font-bold tracking-tighter">Simulated</span>
          </div>
        </div>

        <div class="group relative bg-surface border border-[var(--theme-border)] rounded-2xl p-5 flex items-center gap-4 hover:bg-surface-elevated transition-all hover:-translate-y-0.5 cursor-pointer overflow-hidden" routerLink="/app/protocols" matTooltip="Manage protocols">
          <div class="w-12 h-12 rounded-xl flex items-center justify-center bg-gradient-to-br from-purple-500/20 to-pink-500/20 relative z-10">
            <mat-icon class="text-purple-400">science</mat-icon>
          </div>
          <div class="flex flex-col relative z-10">
            <span class="text-2xl font-bold text-sys-text-primary">{{ totalProtocols() }}</span>
            <span class="text-xs font-medium text-sys-text-tertiary uppercase tracking-wide">Protocols</span>
          </div>
        </div>

        <div class="group relative bg-surface border border-[var(--theme-border)] rounded-2xl p-5 flex items-center gap-4 hover:bg-surface-elevated transition-all hover:-translate-y-0.5 cursor-pointer overflow-hidden" routerLink="/app/assets" matTooltip="Manage resources">
          <div class="w-12 h-12 rounded-xl flex items-center justify-center bg-gradient-to-br from-orange-500/20 to-primary/20 relative z-10">
            <mat-icon class="text-orange-400">inventory_2</mat-icon>
          </div>
          <div class="flex flex-col relative z-10">
            <span class="text-2xl font-bold text-sys-text-primary">{{ totalResources() }}</span>
            <span class="text-xs font-medium text-sys-text-tertiary uppercase tracking-wide">Resources</span>
          </div>
        </div>
      </section>

      <!-- Main Content Grid -->
      <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <!-- Live Experiments Panel -->
        <section class="lg:col-span-2 bg-surface border border-[var(--theme-border)] rounded-3xl overflow-hidden backdrop-blur-xl">
          <div class="p-5 border-b border-[var(--theme-border)] flex justify-between items-center bg-[var(--mat-sys-surface-variant)]">
            <h2 class="text-lg font-semibold text-sys-text-primary flex items-center gap-2">
              <mat-icon class="text-primary">monitor_heart</mat-icon>
              Live Experiments
            </h2>
            @if (runningCount() > 0) {
              <span class="flex items-center gap-2 text-sm font-medium text-green-400 bg-green-400/10 px-3 py-1 rounded-full border border-green-400/20">
                <span class="w-1.5 h-1.5 rounded-full bg-green-400 animate-pulse"></span>
                {{ runningCount() }} Active
              </span>
            }
          </div>

          <div class="p-4">
            @if (hasRunningExperiments()) {
              @for (run of currentRuns(); track run.id) {
                <div class="group relative bg-[var(--mat-sys-surface-variant)] border border-[var(--theme-border)] rounded-xl p-4 mb-3 hover:bg-[var(--mat-sys-surface-variant)] hover:border-[var(--theme-border)] transition-all hover:shadow-lg hover:-translate-y-0.5 cursor-pointer" 
                     [class.border-green-500-30]="run.status === 'running'"
                     routerLink="/app/run"
                     matTooltip="View run details">
                  <div class="flex justify-between items-start mb-3">
                    <div>
                      <h3 class="font-semibold text-sys-text-primary group-hover:text-primary transition-colors">{{ run.name }}</h3>
                      <span class="text-sm text-sys-text-secondary">{{ run.protocolName }}</span>
                    </div>
                    <mat-chip [class]="getStatusClass(run.status) + ' !border-0 !min-h-[24px] !text-xs !font-bold uppercase tracking-wider'">
                      {{ run.status }}
                    </mat-chip>
                  </div>

                  @if (run.status === 'running') {
                    <div class="flex items-center gap-4 mb-3">
                      <mat-progress-bar mode="determinate" [value]="run.progress" class="flex-1 rounded-full overflow-hidden !h-2"></mat-progress-bar>
                      <span class="text-sm font-bold text-primary min-w-[3rem] text-right">{{ run.progress }}%</span>
                    </div>
                  }

                  <div class="flex justify-between items-center text-sm text-sys-text-tertiary group-hover:text-sys-text-secondary transition-colors">
                    <span class="flex items-center gap-1.5">
                      <mat-icon class="!w-4 !h-4 !text-[16px]">schedule</mat-icon>
                      Started {{ formatTimeAgo(run.startedAt) }}
                    </span>
                    @if (run.status === 'running') {
                      <button mat-icon-button class="!text-sys-text-tertiary hover:!text-primary transition-colors">
                        <mat-icon>visibility</mat-icon>
                      </button>
                    }
                  </div>
                </div>
              }
            } @else {
              <div class="flex flex-col items-center justify-center py-16 text-sys-text-tertiary">
                <div class="w-16 h-16 rounded-full bg-[var(--mat-sys-surface-variant)] flex items-center justify-center mb-4">
                  <mat-icon class="!w-8 !h-8 !text-[32px] opacity-50">science</mat-icon>
                </div>
                <p class="mb-4 text-center">No experiments running right now</p>
                <a mat-stroked-button class="!border-primary !text-primary hover:!bg-primary/10 transition-all" routerLink="/app/run">Start a Protocol</a>
              </div>
            }
          </div>
        </section>

        <!-- Right Column (Activity & Links) -->
        <div class="flex flex-col gap-6">
          <!-- Recent Activity -->
          <section class="bg-surface border border-[var(--theme-border)] rounded-3xl overflow-hidden backdrop-blur-xl">
            <div class="p-5 border-b border-[var(--theme-border)] flex justify-between items-center bg-[var(--mat-sys-surface-variant)]">
              <h2 class="text-lg font-semibold text-sys-text-primary flex items-center gap-2">
                <mat-icon class="text-blue-400">history</mat-icon>
                Recent Activity
              </h2>
              <a mat-button class="!text-sys-text-secondary hover:!text-sys-text-primary" routerLink="/app/monitor">View All</a>
            </div>

            <div class="p-2">
              @if (recentRuns().length > 0) {
                @for (run of recentRuns(); track run.id) {
                  <a class="flex items-center gap-3 p-3 hover:bg-[var(--mat-sys-surface-variant)] rounded-xl transition-all cursor-pointer group no-underline hover:shadow-md hover:-translate-y-0.5"
                     [routerLink]="['/app/monitor', run.id]"
                     [matTooltip]="'View run details'"
                     matTooltipPosition="left">
                    <div class="w-10 h-10 rounded-xl flex items-center justify-center transition-transform group-hover:scale-105" [class]="getStatusBgClass(run.status)">
                      <mat-icon class="!text-sys-text-primary !w-5 !h-5 !text-[20px]">{{ getStatusIcon(run.status) }}</mat-icon>
                    </div>
                    <div class="flex-1 min-w-0">
                      <div class="font-medium text-sys-text-primary truncate group-hover:text-primary transition-colors">{{ run.name }}</div>
                      <div class="text-xs text-sys-text-tertiary truncate">{{ run.protocolName }} • {{ run.duration }}</div>
                    </div>
                    <mat-icon class="!text-sys-text-tertiary !w-4 !h-4 !text-[16px] opacity-0 group-hover:opacity-100 transition-opacity">chevron_right</mat-icon>
                  </a>
                }
              } @else {
                <div class="p-8 text-center text-sys-text-tertiary">
                  <p>No recent activity</p>
                </div>
              }
            </div>
          </section>
      </div>
    </div>
  `,
  styles: [`
    /* Custom utility overrides requiring specificity can go here, but mostly empty now */
    :host {
      display: block;
      width: 100%;
    }
    
    .border-green-500-30 {
      border-color: rgba(74, 222, 128, 0.3);
    }
  `]
})
export class HomeComponent implements OnInit, OnDestroy {
  private assetService = inject(AssetService);
  private protocolService = inject(ProtocolService);
  private executionService = inject(ExecutionService);
  public modeService = inject(ModeService);
  private subscription = new Subscription();

  // Stats signals
  totalProtocols = signal(0);
  totalResources = signal(0);
  allMachines = signal<Machine[]>([]);

  // Trend data for sparkline (mock data representing run activity over last 7 days)
  runTrend = signal([2, 1, 3, 2, 4, 3, 5]);

  // Runs signals
  currentRuns = signal<RecentRun[]>([]);
  recentRuns = signal<RecentRun[]>([]);

  // Computed
  runningCount = computed(() => this.currentRuns().filter(r => r.status === 'running').length);
  hasRunningExperiments = computed(() => this.currentRuns().length > 0);

  physicalMachinesCount = computed(() => this.allMachines().filter(m => !m.is_simulation_override).length);
  simulatedMachinesCount = computed(() => this.allMachines().filter(m => m.is_simulation_override).length);

  physicalOnlineMachines = computed(() =>
    this.allMachines().filter(m => !m.is_simulation_override && m.status !== MachineStatus.OFFLINE && m.status !== MachineStatus.ERROR).length
  );
  simulatedOnlineMachines = computed(() =>
    this.allMachines().filter(m => m.is_simulation_override && m.status !== MachineStatus.OFFLINE && m.status !== MachineStatus.ERROR).length
  );

  ngOnInit() {
    this.loadStats();
    this.loadRuns();
    this.subscribeToExecution();
  }

  ngOnDestroy() {
    this.subscription.unsubscribe();
  }

  private loadStats() {
    // Load machines
    this.subscription.add(
      this.assetService.getMachines().subscribe((machines: Machine[]) => {
        this.allMachines.set(machines);
      })
    );

    // Load resources
    this.subscription.add(
      this.assetService.getResources().subscribe((resources: Resource[]) => {
        this.totalResources.set(resources.length);
      })
    );

    // Load protocols
    this.subscription.add(
      this.protocolService.getProtocols().subscribe((protocols: ProtocolDefinition[]) => {
        this.totalProtocols.set(protocols.length);
      })
    );
  }

  private loadRuns() {
    // Simulated recent runs for browser mode
    // In production, this would come from a runs API
    this.recentRuns.set([
      {
        id: '1',
        name: 'Serial Dilution Run #42',
        protocolName: 'Serial Dilution',
        status: 'completed',
        progress: 100,
        startedAt: new Date(Date.now() - 2 * 60 * 60 * 1000),
        duration: '45 min'
      },
      {
        id: '2',
        name: 'PCR Setup Batch 7',
        protocolName: 'PCR Setup',
        status: 'completed',
        progress: 100,
        startedAt: new Date(Date.now() - 5 * 60 * 60 * 1000),
        duration: '32 min'
      },
      {
        id: '3',
        name: 'Cell Culture Transfer',
        protocolName: 'Cell Transfer',
        status: 'failed',
        progress: 67,
        startedAt: new Date(Date.now() - 8 * 60 * 60 * 1000),
        duration: '18 min'
      }
    ]);
  }

  private subscribeToExecution() {
    // Watch for active runs from ExecutionService
    const currentRun = this.executionService.currentRun();
    if (currentRun) {
      this.currentRuns.set([{
        id: currentRun.runId,
        name: currentRun.protocolName,
        protocolName: currentRun.protocolName,
        status: this.mapExecutionStatus(currentRun.status),
        progress: currentRun.progress,
        startedAt: new Date()
      }]);
    }
  }

  private mapExecutionStatus(status: ExecutionStatus): 'running' | 'completed' | 'failed' | 'pending' {
    switch (status) {
      case ExecutionStatus.RUNNING: return 'running';
      case ExecutionStatus.COMPLETED: return 'completed';
      case ExecutionStatus.FAILED: return 'failed';
      case ExecutionStatus.CANCELLED: return 'failed';
      default: return 'pending';
    }
  }

  getStatusIcon(status: string): string {
    switch (status) {
      case 'running': return 'play_arrow';
      case 'completed': return 'check_circle';
      case 'failed': return 'error';
      case 'pending': return 'schedule';
      default: return 'help';
    }
  }

  formatTimeAgo(date: Date): string {
    const now = new Date();
    const diffInSeconds = Math.floor((now.getTime() - date.getTime()) / 1000);

    if (diffInSeconds < 60) return 'just now';
    if (diffInSeconds < 3600) return `${Math.floor(diffInSeconds / 60)}m ago`;
    if (diffInSeconds < 86400) return `${Math.floor(diffInSeconds / 3600)}h ago`;
    return `${Math.floor(diffInSeconds / 86400)}d ago`;
  }

  getStatusClass(status: string): string {
    switch (status) {
      case 'running': return '!bg-green-400/10 !text-green-400';
      case 'completed': return '!bg-blue-400/10 !text-blue-400';
      case 'failed': return '!bg-red-400/10 !text-red-400';
      case 'pending': return '!bg-amber-400/10 !text-amber-400';
      default: return '!bg-[var(--mat-sys-surface-variant)] !text-sys-text-primary';
    }
  }

  getStatusBgClass(status: string): string {
    switch (status) {
      case 'running': return 'bg-green-400/20';
      case 'completed': return 'bg-blue-400/20';
      case 'failed': return 'bg-red-400/20';
      case 'pending': return 'bg-amber-400/20';
      default: return 'bg-[var(--mat-sys-surface-variant)]';
    }
  }

}
