import { Component, inject, OnInit, OnDestroy, signal, computed, ChangeDetectionStrategy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatIconModule } from '@angular/material/icon';
import { MatButtonModule } from '@angular/material/button';
import { MatCardModule } from '@angular/material/card';
import { MatTooltipModule } from '@angular/material/tooltip';
import { Router, RouterLink } from '@angular/router';
import { Subscription } from 'rxjs';
import { AssetService } from '../../services/asset.service';
import { Machine, Resource, ResourceStatus, MachineStatus } from '../../models/asset.models';


@Component({
  selector: 'app-asset-dashboard',
  standalone: true,
  imports: [
    CommonModule,
    MatIconModule,
    MatButtonModule,
    MatCardModule,
    MatTooltipModule,
    RouterLink,
    RouterLink
  ],
  template: `
    <div class="h-full flex flex-col gap-6 overflow-y-auto">
      <!-- Stats Cards -->
      <section class="grid grid-cols-1 md:grid-cols-3 gap-4">
        <!-- Machine Health Card -->
        <div class="group relative bg-white/5 border border-white/10 rounded-2xl p-5 flex items-center gap-4 hover:bg-white/10 transition-all cursor-pointer" 
             (click)="navigateTo('machine')">
          <div class="w-12 h-12 rounded-xl flex items-center justify-center bg-gradient-to-br from-blue-500/20 to-cyan-500/20">
            <mat-icon class="text-blue-400">precision_manufacturing</mat-icon>
          </div>
          <div class="flex flex-col">
            <span class="text-2xl font-bold text-white">
              {{ onlineMachinesCount() }}<span class="text-lg font-normal text-white/40">/{{ totalMachinesCount() }}</span>
            </span>
            <span class="text-xs font-medium text-white/50 uppercase tracking-wide">Machines Online</span>
          </div>
          @if (machinesAttentionCount() > 0) {
            <div class="absolute top-4 right-4 flex items-center gap-1.5 px-2 py-1 rounded-full bg-red-400/10 border border-red-400/20">
              <span class="w-1.5 h-1.5 rounded-full bg-red-400 animate-pulse"></span>
              <span class="text-xs font-bold text-red-400">{{ machinesAttentionCount() }} Issues</span>
            </div>
          }
        </div>

        <!-- Resource Inventory Card -->
        <div class="group relative bg-white/5 border border-white/10 rounded-2xl p-5 flex items-center gap-4 hover:bg-white/10 transition-all cursor-pointer"
             (click)="navigateTo('resource')">
          <div class="w-12 h-12 rounded-xl flex items-center justify-center bg-gradient-to-br from-orange-500/20 to-amber-500/20">
            <mat-icon class="text-orange-400">inventory_2</mat-icon>
          </div>
          <div class="flex flex-col">
            <span class="text-2xl font-bold text-white">{{ totalResourcesCount() }}</span>
            <span class="text-xs font-medium text-white/50 uppercase tracking-wide">Total Items</span>
          </div>
          @if (lowStockCount() > 0) {
            <div class="absolute top-4 right-4 flex items-center gap-1.5 px-2 py-1 rounded-full bg-amber-400/10 border border-amber-400/20">
              <mat-icon class="text-amber-400 !w-3 !h-3 !text-[12px]">warning</mat-icon>
              <span class="text-xs font-bold text-amber-400">{{ lowStockCount() }} Low Stock</span>
            </div>
          }
        </div>

        <!-- Definitions Card -->
        <div class="group relative bg-white/5 border border-white/10 rounded-2xl p-5 flex items-center gap-4 hover:bg-white/10 transition-all cursor-pointer"
             (click)="navigateTo('definition')">
          <div class="w-12 h-12 rounded-xl flex items-center justify-center bg-gradient-to-br from-purple-500/20 to-pink-500/20">
            <mat-icon class="text-purple-400">library_books</mat-icon>
          </div>
          <div class="flex flex-col">
            <span class="text-2xl font-bold text-white">{{ totalDefinitionsCount() }}</span>
            <span class="text-xs font-medium text-white/50 uppercase tracking-wide">Definitions</span>
          </div>
        </div>
      </section>

      <!-- Main Content Grid -->
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
        
        <!-- Quick Actions -->
        <section class="bg-white/5 border border-white/10 rounded-2xl overflow-hidden flex flex-col">
          <div class="p-4 border-b border-white/10 flex items-center justify-between">
            <h3 class="text-lg font-semibold text-white flex items-center gap-2">
              <mat-icon class="text-green-400">bolt</mat-icon>
              Quick Actions
            </h3>
          </div>
          <div class="p-4 grid grid-cols-2 gap-3">
             <button mat-stroked-button class="!border-white/10 !text-white/80 !justify-start !px-4 !py-6 hover:!bg-white/5 hover:!border-primary/50 hover:!text-primary transition-all group" (click)="triggerAction('add-machine')">
               <mat-icon class="mr-2 group-hover:text-primary transition-colors">add_circle</mat-icon>
               Add Machine
             </button>
             <button mat-stroked-button class="!border-white/10 !text-white/80 !justify-start !px-4 !py-6 hover:!bg-white/5 hover:!border-primary/50 hover:!text-primary transition-all group" (click)="triggerAction('add-resource')">
               <mat-icon class="mr-2 group-hover:text-primary transition-colors">add_box</mat-icon>
               Add Resource
             </button>
             <button mat-stroked-button class="!border-white/10 !text-white/80 !justify-start !px-4 !py-6 hover:!bg-white/5 hover:!border-primary/50 hover:!text-primary transition-all group" (click)="triggerAction('discover')">
               <mat-icon class="mr-2 group-hover:text-primary transition-colors">usb</mat-icon>
               Discover Hardware
             </button>
             <button mat-stroked-button class="!border-white/10 !text-white/80 !justify-start !px-4 !py-6 hover:!bg-white/5 hover:!border-primary/50 hover:!text-primary transition-all group" (click)="navigateTo('definition')">
               <mat-icon class="mr-2 group-hover:text-primary transition-colors">search</mat-icon>
               Browse Definitions
             </button>
          </div>
        </section>

        <!-- Alerts & Attention -->
        <section class="bg-white/5 border border-white/10 rounded-2xl overflow-hidden flex flex-col h-full">
          <div class="p-4 border-b border-white/10 flex items-center justify-between">
            <h3 class="text-lg font-semibold text-white flex items-center gap-2">
              <mat-icon class="text-amber-400">notifications_active</mat-icon>
              Needs Attention
            </h3>
            @if (allAlerts().length > 0) {
              <span class="text-xs font-bold text-amber-400 bg-amber-400/10 px-2 py-1 rounded-full">{{ allAlerts().length }} Items</span>
            }
          </div>
          
          <div class="flex-1 overflow-y-auto max-h-[300px] p-2">
            @if (allAlerts().length > 0) {
              <div class="flex flex-col gap-2">
                @for (alert of allAlerts(); track alert.id) {
                  <div class="flex items-center gap-3 p-3 rounded-xl bg-white/5 border border-white/5 hover:bg-white/10 transition-colors cursor-pointer group"
                       (click)="navigateTo(alert.type === 'machine' ? 'machine' : 'resource')">
                    <div class="w-10 h-10 rounded-lg flex items-center justify-center shrink-0" 
                         [class.bg-red-400-20]="alert.severity === 'error'"
                         [class.bg-amber-400-20]="alert.severity === 'warning'">
                      <mat-icon [class.text-red-400]="alert.severity === 'error'"
                                [class.text-amber-400]="alert.severity === 'warning'">
                        {{ alert.icon }}
                      </mat-icon>
                    </div>
                    
                    <div class="flex-1 min-w-0">
                      <div class="flex items-center justify-between mb-1">
                        <span class="font-medium text-white truncate max-w-[70%] group-hover:text-primary transition-colors">{{ alert.name }}</span>
                        <span class="text-xs uppercase font-bold tracking-wider opacity-60 ml-2">{{ alert.type }}</span>
                      </div>
                      <p class="text-xs text-white/50 truncate">{{ alert.message }}</p>
                    </div>

                    <mat-icon class="text-white/20 group-hover:text-white/60">chevron_right</mat-icon>
                  </div>
                }
              </div>
            } @else {
              <div class="h-full flex flex-col items-center justify-center text-white/30 p-8">
                <mat-icon class="text-4xl mb-2 opacity-50">check_circle</mat-icon>
                <p>All systems operational</p>
              </div>
            }
          </div>
        </section>
      </div>
    </div>
  `,
  styles: [`
    :host {
      display: block;
      height: 100%;
    }
    .bg-red-400-20 { background-color: rgba(248, 113, 113, 0.2); }
    .bg-amber-400-20 { background-color: rgba(251, 191, 36, 0.2); }
  `],
  changeDetection: ChangeDetectionStrategy.OnPush
})
export class AssetDashboardComponent implements OnInit, OnDestroy {
  private assetService = inject(AssetService);
  private router = inject(Router);
  private subscription = new Subscription();

  // Signals
  machines = signal<Machine[]>([]);
  resources = signal<Resource[]>([]);
  totalDefinitionsCount = signal(0); // Placeholder count

  // Computed Stats
  totalMachinesCount = computed(() => this.machines().length);
  onlineMachinesCount = computed(() =>
    this.machines().filter(m => m.status !== MachineStatus.OFFLINE && m.status !== MachineStatus.ERROR).length
  );
  machinesAttentionCount = computed(() =>
    this.machines().filter(m => m.status === MachineStatus.ERROR || m.status === MachineStatus.OFFLINE).length
  );

  totalResourcesCount = computed(() => this.resources().length);
  lowStockCount = computed(() =>
    this.resources().filter(r => r.status === ResourceStatus.DEPLETED || r.status === ResourceStatus.EXPIRED).length
  );

  // Consolidated Alerts
  allAlerts = computed(() => {
    const alerts: any[] = [];

    // Machine Alerts
    this.machines().forEach(m => {
      if (m.status === MachineStatus.ERROR) {
        alerts.push({
          id: m.accession_id,
          type: 'machine',
          name: m.name,
          message: 'Machine reported an error state',
          severity: 'error',
          icon: 'error'
        });
      } else if (m.status === MachineStatus.OFFLINE) {
        alerts.push({
          id: m.accession_id,
          type: 'machine',
          name: m.name,
          message: 'Machine is offline',
          severity: 'error',
          icon: 'cloud_off'
        });
      }
    });

    // Resource Alerts
    this.resources().forEach(r => {
      if (r.status === ResourceStatus.DEPLETED) {
        alerts.push({
          id: r.accession_id,
          type: 'resource',
          name: 'Resource Depleted', // Ideally fetch definition name, simple for now
          message: 'Resource has been depleted',
          severity: 'warning',
          icon: 'remove_circle'
        });
      } else if (r.status === ResourceStatus.EXPIRED) {
        alerts.push({
          id: r.accession_id,
          type: 'resource',
          name: 'Resource Expired',
          message: 'Resource expiration date passed',
          severity: 'warning',
          icon: 'event_busy'
        });
      }
    });

    return alerts;
  });

  ngOnInit() {
    this.refreshData();
  }

  ngOnDestroy() {
    this.subscription.unsubscribe();
  }

  refreshData() {
    this.subscription.add(
      this.assetService.getMachines().subscribe(data => this.machines.set(data))
    );
    this.subscription.add(
      this.assetService.getResources().subscribe(data => this.resources.set(data))
    );
    // Fetch definition counts separately if needed, for now placeholders
    this.subscription.add(
      this.assetService.getResourceDefinitions().subscribe(data => {
        // Just update a count for now
        this.totalDefinitionsCount.set(data.length);
      })
    );
  }

  navigateTo(type: 'machine' | 'resource' | 'definition') {
    this.router.navigate([], {
      queryParams: { type: type },
      queryParamsHandling: 'merge'
    });
  }

  triggerAction(action: string) {
    // Dispatch custom event that parent AssetsComponent listens to?
    // Or navigate/open dialog directly?
    // Using custom event is cleaner to keep dialog logic in parent
    const event = new CustomEvent('asset-dashboard-action', { detail: action });
    window.dispatchEvent(event);
  }
}
