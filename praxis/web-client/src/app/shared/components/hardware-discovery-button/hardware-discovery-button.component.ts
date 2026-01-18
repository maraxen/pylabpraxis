import { Component, ChangeDetectionStrategy, inject } from '@angular/core';

import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatTooltipModule } from '@angular/material/tooltip';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatDialog } from '@angular/material/dialog';
import { HardwareDiscoveryService } from '@core/services/hardware-discovery.service';
import { HardwareDiscoveryDialogComponent } from '../hardware-discovery-dialog/hardware-discovery-dialog.component';

@Component({
  selector: 'app-hardware-discovery-button',
  standalone: true,
  imports: [
    MatButtonModule,
    MatIconModule,
    MatTooltipModule,
    MatProgressSpinnerModule
  ],
  template: `
    <button mat-icon-button 
            (click)="triggerDiscovery()" 
            [disabled]="hardwareService.isDiscovering()"
            matTooltip="Discover Hardware">
      @if (hardwareService.isDiscovering()) {
        <mat-spinner diameter="20"></mat-spinner>
      } @else {
        <mat-icon>usb</mat-icon>
      }
    </button>
  `,
  styles: [`
    :host {
      display: inline-block;
    }
    mat-spinner {
      margin: 2px;
    }
  `],
  changeDetection: ChangeDetectionStrategy.OnPush
})
export class HardwareDiscoveryButtonComponent {
  readonly hardwareService = inject(HardwareDiscoveryService);
  private readonly dialog = inject(MatDialog);

  triggerDiscovery() {
    this.dialog.open(HardwareDiscoveryDialogComponent, {
      width: '1000px',
      maxHeight: '90vh'
    });

    // Auto-scan on open if not already scanning
    if (!this.hardwareService.isDiscovering()) {
      this.hardwareService.discoverAll();
    }
  }
}
