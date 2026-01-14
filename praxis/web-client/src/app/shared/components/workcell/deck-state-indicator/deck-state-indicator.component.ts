import { ChangeDetectionStrategy, Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';

export type DeckStateSource = 'live' | 'simulated' | 'cached' | 'definition';

@Component({
  selector: 'app-deck-state-indicator',
  standalone: true,
  imports: [CommonModule],
  template: `
    <span class="state-indicator" [class]="source">
      @switch (source) {
        @case ('live') {
          <span class="icon">🟢</span> LIVE
        }
        @case ('simulated') {
          <span class="icon">🔵</span> SIMULATED
        }
        @case ('cached') {
          <span class="icon">⚪</span> OFFLINE
        }
        @case ('definition') {
          <span class="icon">📐</span> STATIC
        }
      }
    </span>
  `,
  styles: [`
    :host {
      display: inline-block;
      vertical-align: middle;
    }

    .state-indicator {
      display: inline-flex;
      align-items: center;
      gap: 6px;
      padding: 4px 12px;
      border-radius: 16px;
      font-size: 11px;
      font-weight: 700;
      letter-spacing: 0.5px;
      text-transform: uppercase;
      transition: all 0.3s ease;
      white-space: nowrap;
      border: 1px solid transparent;
    }

    .state-indicator.live {
      background: rgba(34, 197, 94, 0.1);
      color: #22c55e; /* Green 500 */
      border-color: rgba(34, 197, 94, 0.3);
      box-shadow: 0 0 12px rgba(34, 197, 94, 0.2);
      animation: pulse-green 2s infinite;
    }

    .state-indicator.simulated {
      background: rgba(59, 130, 246, 0.1);
      color: #3b82f6; /* Blue 500 */
      border-color: rgba(59, 130, 246, 0.3);
    }

    .state-indicator.cached {
      background: rgba(255, 255, 255, 0.05);
      color: var(--theme-text-secondary, #94a3b8);
      border-color: var(--theme-border, rgba(255, 255, 255, 0.1));
    }

    .state-indicator.definition {
      background: transparent;
      color: var(--theme-text-tertiary, #64748b);
      border-color: var(--theme-border-light, rgba(255, 255, 255, 0.05));
      border-style: dashed;
    }

    .state-indicator .icon {
      font-size: 8px; /* Scale down emoji/icon slightly */
      line-height: 1;
      filter: drop-shadow(0 0 2px currentColor);
    }

    @keyframes pulse-green {
      0% {
        box-shadow: 0 0 0 0 rgba(34, 197, 94, 0.4);
      }
      70% {
        box-shadow: 0 0 0 6px rgba(34, 197, 94, 0);
      }
      100% {
        box-shadow: 0 0 0 0 rgba(34, 197, 94, 0);
      }
    }
  `],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class DeckStateIndicatorComponent {
  @Input({ required: true }) source!: DeckStateSource;
}
