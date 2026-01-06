import { Component, Input, Output, EventEmitter, ChangeDetectionStrategy } from '@angular/core';

import { MatCardModule } from '@angular/material/card';
import { MatIconModule } from '@angular/material/icon';
import { MatChipsModule } from '@angular/material/chips';
import { ProtocolDefinition } from '@features/protocols/models/protocol.models';
import { ProtocolWarningBadgeComponent } from '@shared/components/protocol-warning-badge/protocol-warning-badge.component';

@Component({
  selector: 'app-protocol-card',
  standalone: true,
  imports: [
    MatCardModule,
    MatIconModule,
    MatChipsModule,
    ProtocolWarningBadgeComponent
],
  template: `
    <mat-card class="protocol-card" [class.compact]="compact" (click)="select.emit(protocol)">
      <mat-card-header>
        <mat-icon mat-card-avatar class="card-icon">science</mat-icon>
        <mat-card-title>{{ protocol.name }}</mat-card-title>
        @if (!compact && protocol.category) {
          <mat-card-subtitle>{{ protocol.category }}</mat-card-subtitle>
        }
      </mat-card-header>
      @if (!compact) {
        <mat-card-content>
          <p class="description">{{ protocol.description || 'No description available.' }}</p>
        </mat-card-content>
        <mat-card-actions>
          <div class="actions-row">
            <mat-chip-set aria-label="Protocol tags">
              <mat-chip [highlighted]="true">v{{ protocol.version }}</mat-chip>
              @if (protocol.is_top_level) {
                <mat-chip>Top Level</mat-chip>
              }
            </mat-chip-set>
            <app-protocol-warning-badge [protocol]="protocol"></app-protocol-warning-badge>
          </div>
        </mat-card-actions>
      } @else {
        <!-- Compact mode: show badge inline -->
        <div class="compact-badge">
          <app-protocol-warning-badge [protocol]="protocol"></app-protocol-warning-badge>
        </div>
      }
    </mat-card>
  `,
  styles: [`
    .protocol-card {
      cursor: pointer;
      transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .protocol-card:hover {
      transform: translateY(-4px);
      box-shadow: 0 8px 24px rgba(0, 0, 0, 0.2);
    }
    .protocol-card.compact {
      min-width: 180px;
      max-width: 220px;
    }
    .card-icon {
      font-size: 24px;
      width: 40px;
      height: 40px;
      display: flex;
      align-items: center;
      justify-content: center;
      background: var(--sys-primary);
      color: var(--sys-on-primary);
      border-radius: 50%;
    }
    .description {
      display: -webkit-box;
      -webkit-line-clamp: 2;
      -webkit-box-orient: vertical;
      overflow: hidden;
      text-overflow: ellipsis;
      min-height: 40px;
      color: var(--sys-on-surface-variant);
    }
    mat-card-actions {
      padding: 0 16px 16px;
    }
    .actions-row {
      display: flex;
      justify-content: space-between;
      align-items: center;
      width: 100%;
    }
    .compact-badge {
      padding: 8px 16px;
    }
  `],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class ProtocolCardComponent {
  @Input({ required: true }) protocol!: ProtocolDefinition;
  @Input() compact = false;
  @Output() select = new EventEmitter<ProtocolDefinition>();
}
