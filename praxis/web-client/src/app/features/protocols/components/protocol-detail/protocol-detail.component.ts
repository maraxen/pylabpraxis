import { Component, ChangeDetectionStrategy, inject, signal, Input } from '@angular/core';

import { MatCardModule } from '@angular/material/card';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatChipsModule } from '@angular/material/chips';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { ProtocolService } from '../../services/protocol.service';
import { ProtocolDefinition } from '../../models/protocol.models';
import { Router } from '@angular/router';
import { finalize } from 'rxjs/operators'; // Import finalize

@Component({
  selector: 'app-protocol-detail',
  standalone: true,
  imports: [
    MatCardModule,
    MatButtonModule,
    MatIconModule,
    MatChipsModule,
    MatProgressSpinnerModule
],
  template: `
    @if (!isLoading()) {
      <div class="protocol-detail-container">
        <div class="header">
          <button mat-icon-button (click)="goBack()">
            <mat-icon>arrow_back</mat-icon>
          </button>
          <h1>{{ protocol()?.name || 'Loading...' }}</h1>
          <span class="spacer"></span>
          <button mat-flat-button color="primary" (click)="runProtocol()" [disabled]="!protocol()">
            <mat-icon>play_arrow</mat-icon>
            Run Protocol
          </button>
        </div>
        @if (protocol()) {
          <div class="content">
            <mat-card class="info-card">
              <mat-card-header>
                <mat-card-title>Information</mat-card-title>
              </mat-card-header>
              <mat-card-content>
                <div class="info-grid">
                  <div class="info-item">
                    <span class="label">Accession ID:</span>
                    <span class="value">{{ protocol()?.accession_id }}</span>
                  </div>
                  <div class="info-item">
                    <span class="label">Version:</span>
                    <span class="value">{{ protocol()?.version }}</span>
                  </div>
                  <div class="info-item">
                    <span class="label">Category:</span>
                    <span class="value">{{ protocol()?.category || 'N/A' }}</span>
                  </div>
                  <div class="info-item">
                    <span class="label">Type:</span>
                    <span class="value">{{ protocol()?.is_top_level ? 'Top Level' : 'Sub-Protocol' }}</span>
                  </div>
                </div>
                <div class="description-section">
                  <h3>Description</h3>
                  <p>{{ protocol()?.description || 'No description provided.' }}</p>
                </div>
              </mat-card-content>
            </mat-card>
            <!-- Placeholder for future sections like Parameters Preview or Source Code -->
          </div>
        }
        @if (!protocol() && !isLoading()) {
          <div class="no-protocol-found">
            <p>Protocol not found.</p>
            <button mat-flat-button color="primary" (click)="goBack()">Back to Library</button>
          </div>
        }
      </div>
    } @else {
      <div class="loading-container">
        <mat-spinner diameter="40"></mat-spinner>
      </div>
    }
    
    `,
  styles: [`
    .protocol-detail-container {
      padding: 32px;
      height: 100%;
      display: flex;
      flex-direction: column;
      background: var(--mat-sys-surface);
      border-radius: 24px;
    }

    .header {
      display: flex;
      align-items: center;
      margin-bottom: 24px;
      gap: 24px;
      border-bottom: 1px solid var(--theme-border);
      padding-bottom: 16px;
    }

    h1 {
      margin: 0;
      font-size: 1.75rem;
      font-weight: 600;
      flex: 1;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }

    .spacer {
      display: none; /* Replaced by flex: 1 on h1 */
    }

    .content {
      flex: 1;
      overflow-y: auto;
      padding-top: 8px;
    }

    .info-card {
      margin-bottom: 24px;
      border-radius: 16px;
      border: 1px solid var(--mat-sys-outline-variant);
      background: var(--mat-sys-surface-container-low);
    }

    .info-grid {
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
      gap: 24px;
      margin-bottom: 32px;
    }

    .info-item {
      display: flex;
      flex-direction: column;
    }

    .label {
      font-size: 0.75rem;
      font-weight: 600;
      text-transform: uppercase;
      letter-spacing: 0.05em;
      color: var(--mat-sys-color-on-surface-variant);
      margin-bottom: 6px;
      opacity: 0.8;
    }

    .value {
      font-weight: 500;
      font-size: 1rem;
    }

    .description-section h3 {
      font-size: 0.875rem;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 0.05em;
      margin-bottom: 12px;
      color: var(--mat-sys-color-on-surface-variant);
    }

    .description-section p {
      white-space: pre-wrap;
      line-height: 1.6;
      font-size: 1rem;
      margin: 0;
      color: var(--mat-sys-on-surface);
    }

    .loading-container, .no-protocol-found {
      display: flex;
      justify-content: center;
      align-items: center;
      height: 100%;
      flex-direction: column;
    }
  `],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class ProtocolDetailComponent {
  private protocolService = inject(ProtocolService);
  private router = inject(Router);

  protocol = signal<ProtocolDefinition | null>(null);
  isLoading = signal(true); // New loading signal

  @Input()
  set id(protocolId: string) {
    this.loadProtocol(protocolId);
  }

  private loadProtocol(id: string): void {
    this.isLoading.set(true); // Set loading true before API call
    this.protocolService.getProtocols().pipe(
      finalize(() => this.isLoading.set(false)) // Set loading false after API call completes
    ).subscribe(
      (protocols) => {
        const found = protocols.find(p => p.accession_id === id);
        if (found) {
          this.protocol.set(found);
        } else {
          console.error('Protocol not found');
          // No navigation here, just show "Protocol not found" message
        }
      },
      (error) => {
        console.error('Error fetching protocol details:', error);
      }
    );
  }

  goBack() {
    this.router.navigate(['/protocols']);
  }

  runProtocol() {
    const p = this.protocol();
    if (p) {
      this.router.navigate(['/run'], { queryParams: { protocolId: p.accession_id } });
    }
  }
}