import { Component, inject, computed } from '@angular/core';
import { MatIconModule } from '@angular/material/icon';
import { MatButtonModule } from '@angular/material/button';
import { MatTooltipModule } from '@angular/material/tooltip';

import { ModeService } from '@core/services/mode.service';
import { PlaygroundJupyterliteService } from '../../services/playground-jupyterlite.service';
import { PlaygroundAssetService } from '../../services/playground-asset.service';
import { HardwareDiscoveryButtonComponent } from '@shared/components/hardware-discovery-button/hardware-discovery-button.component';

@Component({
  selector: 'app-playground-header',
  standalone: true,
  imports: [
    MatIconModule,
    MatButtonModule,
    MatTooltipModule,
    HardwareDiscoveryButtonComponent
  ],
  template: `
    <div class="repl-header">
      <div class="header-title">
        <mat-icon>auto_stories</mat-icon>
        <h2>Playground ({{ modeLabel() }})</h2>
      </div>
      
      <div class="header-actions flex items-center gap-2">
        <app-hardware-discovery-button></app-hardware-discovery-button>
        <button 
          mat-icon-button 
          (click)="jupyterliteService.reloadNotebook()"
          matTooltip="Restart Kernel (reload notebook)"
          aria-label="Restart Kernel (reload notebook)">
          <mat-icon>restart_alt</mat-icon>
        </button>
        <button 
          mat-icon-button 
          (click)="assetService.openAssetWizard('MACHINE')"
          matTooltip="Add Machine"
          aria-label="Add Machine"
          color="primary">
          <mat-icon>precision_manufacturing</mat-icon>
        </button>
        <button 
          mat-icon-button 
          (click)="assetService.openAssetWizard('RESOURCE')"
          matTooltip="Add Resource"
          aria-label="Add Resource"
          color="primary">
          <mat-icon>science</mat-icon>
        </button>
        <button 
          mat-icon-button 
          (click)="assetService.openAssetWizard()"
          matTooltip="Browse Inventory"
          aria-label="Browse Inventory"
          color="primary">
          <mat-icon>inventory_2</mat-icon>
        </button>
      </div>
    </div>
  `,
  styles: [`
    .repl-header {
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 8px 16px;
      background: var(--mat-sys-surface-container-high);
      border-bottom: 1px solid var(--mat-sys-outline-variant);
      flex-shrink: 0;
      height: 56px;
      box-sizing: border-box;
    }

    .header-title {
      display: flex;
      align-items: center;
      gap: 12px;
    }

    .repl-header mat-icon {
      color: var(--mat-sys-primary);
    }

    .repl-header h2 {
      margin: 0;
      font-size: 1.1rem;
      font-weight: 500;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }
  `]
})
export class PlaygroundHeaderComponent {
  private modeService = inject(ModeService);
  public jupyterliteService = inject(PlaygroundJupyterliteService);
  public assetService = inject(PlaygroundAssetService);

  modeLabel = computed(() => this.modeService.modeLabel());
}
