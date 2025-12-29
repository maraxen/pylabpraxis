
import { Component, inject, OnInit, OnDestroy, signal, computed } from '@angular/core';
import { CommonModule } from '@angular/common';
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
import { Machine, Resource } from '../assets/models/asset.models';
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
    CommonModule,
    RouterLink,
    MatCardModule,
    MatIconModule,
    MatButtonModule,
    MatProgressBarModule,
    MatChipsModule,
    MatTooltipModule,
    MatBadgeModule
  ],
  template: `
    <div class="dashboard">
      <!-- Header with Quick Actions -->
      <header class="dashboard-header">
        <div class="header-content">
          <div class="greeting">
            <h1 class="title">Welcome back</h1>
            <p class="subtitle">Here's what's happening in your lab</p>
          </div>
          <div class="quick-actions">
            <a mat-flat-button class="action-primary" routerLink="/app/run">
              <mat-icon>play_circle</mat-icon>
              Run Protocol
            </a>
            <a mat-stroked-button class="action-secondary" routerLink="/app/protocols">
              <mat-icon>schedule</mat-icon>
              Schedule
            </a>
          </div>
        </div>
      </header>

      <!-- Stats Overview -->
      <section class="stats-grid">
        <div class="stat-card active-runs clickable" routerLink="/app/run" matTooltip="View active protocol runs">
          <div class="stat-icon">
            <mat-icon>play_arrow</mat-icon>
          </div>
          <div class="stat-content">
            <span class="stat-value">{{ runningCount() }}</span>
            <span class="stat-label">Running</span>
          </div>
          <div class="stat-indicator pulse"></div>
        </div>

        <div class="stat-card instruments clickable" routerLink="/app/assets" matTooltip="View laboratory instruments">
          <div class="stat-icon">
            <mat-icon>precision_manufacturing</mat-icon>
          </div>
          <div class="stat-content">
            <span class="stat-value">{{ activeMachines() }}/{{ totalMachines() }}</span>
            <span class="stat-label">Instruments Online</span>
          </div>
        </div>

        <div class="stat-card protocols clickable" routerLink="/app/protocols" matTooltip="Manage protocols">
          <div class="stat-icon">
            <mat-icon>science</mat-icon>
          </div>
          <div class="stat-content">
            <span class="stat-value">{{ totalProtocols() }}</span>
            <span class="stat-label">Protocols</span>
          </div>
        </div>

        <div class="stat-card resources clickable" routerLink="/app/assets" matTooltip="Manage resources">
          <div class="stat-icon">
            <mat-icon>inventory_2</mat-icon>
          </div>
          <div class="stat-content">
            <span class="stat-value">{{ totalResources() }}</span>
            <span class="stat-label">Resources</span>
          </div>
        </div>
      </section>

      <!-- Main Content Grid -->
      <div class="content-grid">
        <!-- Live Experiments Panel -->
        <section class="panel live-experiments">
          <div class="panel-header">
            <h2>
              <mat-icon>monitor_heart</mat-icon>
              Live Experiments
            </h2>
            @if (runningCount() > 0) {
              <span class="live-badge">
                <span class="live-dot"></span>
                {{ runningCount() }} Active
              </span>
            }
          </div>

          <div class="panel-content">
            @if (hasRunningExperiments()) {
              @for (run of currentRuns(); track run.id) {
                <div class="experiment-card clickable" 
                     [class.running]="run.status === 'running'"
                     routerLink="/app/run"
                     matTooltip="View run details">
                  <div class="experiment-header">
                    <div class="experiment-info">
                      <h3>{{ run.name }}</h3>
                      <span class="protocol-name">{{ run.protocolName }}</span>
                    </div>
                    <mat-chip [class]="'status-' + run.status">
                      {{ run.status | titlecase }}
                    </mat-chip>
                  </div>

                  @if (run.status === 'running') {
                    <div class="progress-section">
                      <mat-progress-bar mode="determinate" [value]="run.progress"></mat-progress-bar>
                      <span class="progress-label">{{ run.progress }}%</span>
                    </div>
                  }

                  <div class="experiment-footer">
                    <span class="time-info">
                      <mat-icon>schedule</mat-icon>
                      Started {{ formatTimeAgo(run.startedAt) }}
                    </span>
                    @if (run.status === 'running') {
                      <button mat-icon-button routerLink="/app/run">
                        <mat-icon>visibility</mat-icon>
                      </button>
                    }
                  </div>
                </div>
              }
            } @else {
              <div class="empty-state">
                <mat-icon>science</mat-icon>
                <p>No experiments running</p>
                <a mat-stroked-button routerLink="/app/run">Start a Protocol</a>
              </div>
            }
          </div>
        </section>

        <!-- Recent Activity Panel -->
        <section class="panel recent-activity">
          <div class="panel-header">
            <h2>
              <mat-icon>history</mat-icon>
              Recent Activity
            </h2>
            <a mat-button routerLink="/app/protocols">View All</a>
          </div>

          <div class="panel-content">
            @if (recentRuns().length > 0) {
              @for (run of recentRuns(); track run.id) {
                <div class="activity-item">
                  <div class="activity-icon" [class]="'status-bg-' + run.status">
                    <mat-icon>{{ getStatusIcon(run.status) }}</mat-icon>
                  </div>
                  <div class="activity-content">
                    <span class="activity-name">{{ run.name }}</span>
                    <span class="activity-meta">{{ run.protocolName }} • {{ run.duration }}</span>
                  </div>
                  <mat-chip [class]="'status-chip-' + run.status" size="small">
                    {{ run.status | titlecase }}
                  </mat-chip>
                </div>
              }
            } @else {
              <div class="empty-state small">
                <mat-icon>history</mat-icon>
                <p>No recent activity</p>
              </div>
            }
          </div>
        </section>

        <!-- Quick Links Panel -->
        <section class="panel quick-links">
          <div class="panel-header">
            <h2>
              <mat-icon>apps</mat-icon>
              Quick Links
            </h2>
          </div>

          <div class="panel-content links-grid">
            <a class="quick-link" routerLink="/app/assets">
              <mat-icon>precision_manufacturing</mat-icon>
              <span>Instruments</span>
            </a>
            <a class="quick-link" routerLink="/app/protocols">
              <mat-icon>assignment</mat-icon>
              <span>Protocols</span>
            </a>
            <a class="quick-link" routerLink="/app/visualizer">
              <mat-icon>view_in_ar</mat-icon>
              <span>Visualizer</span>
            </a>
            <a class="quick-link" routerLink="/app/settings">
              <mat-icon>settings</mat-icon>
              <span>Settings</span>
            </a>
          </div>
        </section>
      </div>
    </div>
  `,
  styles: [`
    .dashboard {
      padding: 1.5rem;
      max-width: 1400px;
      margin: 0 auto;
    }

    .clickable {
      cursor: pointer;
    }

    /* Header */
    .dashboard-header {
      margin-bottom: 2rem;
    }

    .header-content {
      display: flex;
      justify-content: space-between;
      align-items: center;
      flex-wrap: wrap;
      gap: 1rem;
    }

    .greeting .title {
      font-size: 2rem;
      font-weight: 700;
      color: var(--theme-text-primary, #fff);
      margin: 0;
    }

    .greeting .subtitle {
      color: var(--theme-text-secondary, rgba(255,255,255,0.7));
      margin: 0.25rem 0 0 0;
    }

    .quick-actions {
      display: flex;
      gap: 0.75rem;
    }

    .action-primary {
      background: linear-gradient(135deg, var(--primary-color, #ED7A9B) 0%, #d85a7f 100%) !important;
      color: white !important;
      padding: 0.75rem 1.5rem !important;
      border-radius: 12px !important;
      font-weight: 600;
      display: flex;
      align-items: center;
      gap: 0.5rem;
    }

    .action-secondary {
      border-color: var(--theme-border, rgba(255,255,255,0.2)) !important;
      color: var(--theme-text-primary, white) !important;
      padding: 0.75rem 1.5rem !important;
      border-radius: 12px !important;
      display: flex;
      align-items: center;
      gap: 0.5rem;
    }

    /* Stats Grid */
    .stats-grid {
      display: grid;
      grid-template-columns: repeat(4, 1fr);
      gap: 1rem;
      margin-bottom: 2rem;
    }

    .stat-card {
      background: var(--theme-surface, rgba(255,255,255,0.05));
      border: 1px solid var(--theme-border, rgba(255,255,255,0.1));
      border-radius: 16px;
      padding: 1.25rem;
      display: flex;
      align-items: center;
      gap: 1rem;
      position: relative;
      overflow: hidden;
      transition: all 0.3s ease;
    }

    .stat-card:hover {
      background: var(--theme-surface-elevated, rgba(255,255,255,0.08));
      transform: translateY(-2px);
    }

    .stat-icon {
      width: 48px;
      height: 48px;
      border-radius: 12px;
      display: flex;
      align-items: center;
      justify-content: center;
      background: linear-gradient(135deg, var(--aurora-primary, rgba(237,122,155,0.2)) 0%, var(--aurora-secondary, rgba(115,169,194,0.2)) 100%);
    }

    .stat-icon mat-icon {
      font-size: 24px;
      width: 24px;
      height: 24px;
      color: var(--primary-color, #ED7A9B);
    }

    .stat-content {
      display: flex;
      flex-direction: column;
    }

    .stat-value {
      font-size: 1.5rem;
      font-weight: 700;
      color: var(--theme-text-primary, white);
    }

    .stat-label {
      font-size: 0.85rem;
      color: var(--theme-text-tertiary, rgba(255,255,255,0.5));
    }

    .stat-indicator.pulse {
      position: absolute;
      top: 1rem;
      right: 1rem;
      width: 8px;
      height: 8px;
      background: #4ade80;
      border-radius: 50%;
      animation: pulse 2s infinite;
    }

    @keyframes pulse {
      0%, 100% { opacity: 1; transform: scale(1); }
      50% { opacity: 0.5; transform: scale(1.2); }
    }

    /* Content Grid */
    .content-grid {
      display: grid;
      grid-template-columns: 2fr 1fr;
      grid-template-rows: auto auto;
      gap: 1.5rem;
    }

    .live-experiments {
      grid-row: span 2;
    }

    /* Panel Styling */
    .panel {
      background: var(--theme-surface, rgba(255,255,255,0.05));
      border: 1px solid var(--theme-border, rgba(255,255,255,0.1));
      border-radius: 20px;
      overflow: hidden;
    }

    .panel-header {
      padding: 1.25rem 1.5rem;
      border-bottom: 1px solid var(--theme-border, rgba(255,255,255,0.1));
      display: flex;
      justify-content: space-between;
      align-items: center;
    }

    .panel-header h2 {
      font-size: 1.1rem;
      font-weight: 600;
      color: var(--theme-text-primary, white);
      margin: 0;
      display: flex;
      align-items: center;
      gap: 0.5rem;
    }

    .panel-header h2 mat-icon {
      font-size: 20px;
      width: 20px;
      height: 20px;
      color: var(--primary-color, #ED7A9B);
    }

    .live-badge {
      display: flex;
      align-items: center;
      gap: 0.5rem;
      font-size: 0.85rem;
      color: #4ade80;
      background: rgba(74, 222, 128, 0.1);
      padding: 0.35rem 0.75rem;
      border-radius: 20px;
    }

    .live-dot {
      width: 6px;
      height: 6px;
      background: #4ade80;
      border-radius: 50%;
      animation: pulse 2s infinite;
    }

    .panel-content {
      padding: 1rem;
    }

    /* Experiment Card */
    .experiment-card {
      background: var(--theme-surface-elevated, rgba(255,255,255,0.03));
      border: 1px solid var(--theme-border-light, rgba(255,255,255,0.05));
      border-radius: 12px;
      padding: 1rem;
      margin-bottom: 0.75rem;
      transition: all 0.3s ease;
    }

    .experiment-card:hover {
      background: var(--theme-surface-elevated, rgba(255,255,255,0.08));
      transform: translateY(-2px);
      box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    }

    .experiment-card.running {
      border-color: rgba(74, 222, 128, 0.3);
    }

    .experiment-card:last-child {
      margin-bottom: 0;
    }

    .experiment-header {
      display: flex;
      justify-content: space-between;
      align-items: flex-start;
      margin-bottom: 0.75rem;
    }

    .experiment-info h3 {
      font-size: 1rem;
      font-weight: 600;
      color: var(--theme-text-primary, white);
      margin: 0;
    }

    .protocol-name {
      font-size: 0.85rem;
      color: var(--theme-text-tertiary, rgba(255,255,255,0.5));
    }

    .progress-section {
      display: flex;
      align-items: center;
      gap: 1rem;
      margin-bottom: 0.75rem;
    }

    .progress-section mat-progress-bar {
      flex: 1;
      border-radius: 4px;
    }

    .progress-label {
      font-size: 0.85rem;
      font-weight: 600;
      color: var(--primary-color, #ED7A9B);
      min-width: 40px;
    }

    .experiment-footer {
      display: flex;
      justify-content: space-between;
      align-items: center;
    }

    .time-info {
      display: flex;
      align-items: center;
      gap: 0.35rem;
      font-size: 0.8rem;
      color: var(--theme-text-tertiary, rgba(255,255,255,0.5));
    }

    .time-info mat-icon {
      font-size: 14px;
      width: 14px;
      height: 14px;
    }

    /* Status Chips */
    .status-running { background: rgba(74, 222, 128, 0.2) !important; color: #4ade80 !important; }
    .status-completed { background: rgba(96, 165, 250, 0.2) !important; color: #60a5fa !important; }
    .status-failed { background: rgba(248, 113, 113, 0.2) !important; color: #f87171 !important; }
    .status-pending { background: rgba(251, 191, 36, 0.2) !important; color: #fbbf24 !important; }

    /* Activity Items */
    .activity-item {
      display: flex;
      align-items: center;
      gap: 0.75rem;
      padding: 0.75rem 0;
      border-bottom: 1px solid var(--theme-border-light, rgba(255,255,255,0.05));
    }

    .activity-item:last-child {
      border-bottom: none;
    }

    .activity-icon {
      width: 36px;
      height: 36px;
      border-radius: 10px;
      display: flex;
      align-items: center;
      justify-content: center;
    }

    .activity-icon mat-icon {
      font-size: 18px;
      width: 18px;
      height: 18px;
      color: white;
    }

    .status-bg-completed { background: rgba(96, 165, 250, 0.3); }
    .status-bg-failed { background: rgba(248, 113, 113, 0.3); }
    .status-bg-running { background: rgba(74, 222, 128, 0.3); }
    .status-bg-pending { background: rgba(251, 191, 36, 0.3); }

    .activity-content {
      flex: 1;
      display: flex;
      flex-direction: column;
    }

    .activity-name {
      font-size: 0.9rem;
      font-weight: 500;
      color: var(--theme-text-primary, white);
    }

    .activity-meta {
      font-size: 0.8rem;
      color: var(--theme-text-tertiary, rgba(255,255,255,0.5));
    }

    .status-chip-completed { background: rgba(96, 165, 250, 0.15) !important; color: #60a5fa !important; font-size: 0.7rem !important; }
    .status-chip-failed { background: rgba(248, 113, 113, 0.15) !important; color: #f87171 !important; font-size: 0.7rem !important; }
    .status-chip-running { background: rgba(74, 222, 128, 0.15) !important; color: #4ade80 !important; font-size: 0.7rem !important; }

    /* Quick Links */
    .links-grid {
      display: grid;
      grid-template-columns: repeat(2, 1fr);
      gap: 0.75rem;
    }

    .quick-link {
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      gap: 0.5rem;
      padding: 1.25rem;
      background: var(--theme-surface-elevated, rgba(255,255,255,0.03));
      border: 1px solid var(--theme-border-light, rgba(255,255,255,0.05));
      border-radius: 12px;
      text-decoration: none;
      color: var(--theme-text-primary, white);
      transition: all 0.3s ease;
    }

    .quick-link:hover {
      background: var(--primary-color, #ED7A9B);
      border-color: var(--primary-color, #ED7A9B);
      transform: translateY(-2px);
    }

    .quick-link mat-icon {
      font-size: 24px;
      width: 24px;
      height: 24px;
      color: var(--primary-color, #ED7A9B);
      transition: color 0.3s ease;
    }

    .quick-link:hover mat-icon {
      color: white;
    }

    .quick-link span {
      font-size: 0.85rem;
      font-weight: 500;
    }

    /* Empty States */
    .empty-state {
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      padding: 3rem 1rem;
      color: var(--theme-text-tertiary, rgba(255,255,255,0.5));
    }

    .empty-state.small {
      padding: 1.5rem;
    }

    .empty-state mat-icon {
      font-size: 48px;
      width: 48px;
      height: 48px;
      opacity: 0.5;
      margin-bottom: 1rem;
    }

    .empty-state p {
      margin: 0 0 1rem 0;
    }

    /* Responsive */
    @media (max-width: 1024px) {
      .stats-grid {
        grid-template-columns: repeat(2, 1fr);
      }

      .content-grid {
        grid-template-columns: 1fr;
      }

      .live-experiments {
        grid-row: auto;
      }
    }

    @media (max-width: 640px) {
      .dashboard {
        padding: 1rem;
      }

      .header-content {
        flex-direction: column;
        align-items: flex-start;
      }

      .quick-actions {
        width: 100%;
      }

      .action-primary, .action-secondary {
        flex: 1;
        justify-content: center;
      }

      .stats-grid {
        grid-template-columns: 1fr 1fr;
      }

      .greeting .title {
        font-size: 1.5rem;
      }
    }
  `]
})
export class HomeComponent implements OnInit, OnDestroy {
  private assetService = inject(AssetService);
  private protocolService = inject(ProtocolService);
  private executionService = inject(ExecutionService);
  private subscription = new Subscription();

  // Stats signals
  totalMachines = signal(0);
  activeMachines = signal(0);
  totalProtocols = signal(0);
  totalResources = signal(0);

  // Runs signals
  currentRuns = signal<RecentRun[]>([]);
  recentRuns = signal<RecentRun[]>([]);

  // Computed
  runningCount = computed(() => this.currentRuns().filter(r => r.status === 'running').length);
  hasRunningExperiments = computed(() => this.currentRuns().length > 0);

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
        this.totalMachines.set(machines.length);
        this.activeMachines.set(machines.filter(m => m.status !== 'offline' && m.status !== 'error').length);
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
    // Simulated recent runs for demo
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
      case 'completed': return 'check_circle';
      case 'failed': return 'error';
      case 'running': return 'play_arrow';
      default: return 'schedule';
    }
  }

  formatTimeAgo(date: Date): string {
    const now = new Date();
    const diff = Math.floor((now.getTime() - date.getTime()) / 1000);

    if (diff < 60) return 'just now';
    if (diff < 3600) return `${Math.floor(diff / 60)} min ago`;
    if (diff < 86400) return `${Math.floor(diff / 3600)} hours ago`;
    return `${Math.floor(diff / 86400)} days ago`;
  }
}
