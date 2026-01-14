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
    <div class="praxis-card premium group cursor-pointer" [class.praxis-card-min]="compact" (click)="select.emit(protocol)">
      <div class="card-header">
        <div class="flex items-center gap-3 min-w-0">
          <div class="w-10 h-10 rounded-full flex-shrink-0 flex items-center justify-center bg-primary text-on-primary">
            <mat-icon>science</mat-icon>
          </div>
          <div class="min-w-0">
            <h3 class="card-title group-hover:text-primary transition-colors">{{ protocol.name }}</h3>
            @if (!compact && protocol.category) {
              <p class="card-subtitle">{{ protocol.category }}</p>
            }
          </div>
        </div>
      </div>

      @if (!compact) {
        <div class="card-content">
          <p class="text-sm text-sys-text-secondary line-clamp-2 min-h-[40px]">{{ protocol.description || 'No description available.' }}</p>
        </div>
        <div class="card-actions">
          <div class="flex items-center justify-between w-full gap-2">
            <div class="flex flex-wrap gap-2">
              <span class="px-2 py-0.5 rounded bg-primary/10 text-primary font-mono text-[10px] font-bold">v{{ protocol.version }}</span>
              @if (protocol.is_top_level) {
                <span class="px-2 py-0.5 rounded bg-secondary/10 text-secondary text-[10px] font-bold uppercase tracking-wider">Top Level</span>
              }
            </div>
            <app-protocol-warning-badge [protocol]="protocol"></app-protocol-warning-badge>
          </div>
        </div>
      } @else {
        <div class="card-content pt-0">
          <app-protocol-warning-badge [protocol]="protocol"></app-protocol-warning-badge>
        </div>
      }
    </div>
  `,
  styles: [`
    /* Component specific tweaks that go beyond global defaults */
    .praxis-card.praxis-card-min {
      min-width: 180px;
      max-width: 220px;
    }
    :host ::ng-deep app-protocol-warning-badge mat-icon {
      font-size: 18px;
      width: 18px;
      height: 18px;
    }
  `],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class ProtocolCardComponent {
  @Input({ required: true }) protocol!: ProtocolDefinition;
  @Input() compact = false;
  @Output() select = new EventEmitter<ProtocolDefinition>();
}
