import { Component, ChangeDetectionStrategy, Input, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { PlrDeckData } from '@core/models/plr.models';
import { DeckViewComponent } from '@shared/components/deck-view/deck-view.component';

@Component({
  selector: 'app-deck-visualizer',
  standalone: true,
  imports: [CommonModule, DeckViewComponent],
  template: `
    <div class="deck-visualizer-wrapper">
      <div class="visualizer-header">
        <h4>Deck Configuration Visualizer</h4>
      </div>

      <div class="view-container">
        <app-deck-view
          *ngIf="data()"
          [resource]="data()!.resource"
          [state]="data()!.state">
        </app-deck-view>
        
        <div *ngIf="!data()" class="empty-state">
          No deck data available
        </div>
      </div>
    </div>
  `,
  styles: [`
    :host {
      display: block;
      width: 100%;
      height: 100%;
    }

    .deck-visualizer-wrapper {
      display: flex;
      flex-direction: column;
      height: 100%;
      background: var(--sys-surface-container-low);
      border-radius: 12px;
      padding: 16px;
      border: 1px solid var(--sys-outline-variant);
    }

    .visualizer-header {
      margin-bottom: 16px;
    }

    .visualizer-header h4 {
      margin: 0;
      color: var(--sys-on-surface);
    }

    .view-container {
      flex: 1;
      min-height: 0;
      overflow: hidden;
      border-radius: 8px;
      background: white;
      display: flex;
      flex-direction: column;
    }
    
    app-deck-view {
      flex: 1;
      overflow: auto;
    }

    .empty-state {
      display: flex;
      align-items: center;
      justify-content: center;
      height: 100%;
      color: var(--sys-outline);
    }
  `],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class DeckVisualizerComponent {
  // Inputs
  @Input({ required: true }) set layoutData(value: PlrDeckData | null) {
    this.data.set(value);
  }

  // Signals
  data = signal<PlrDeckData | null>(null);
}
