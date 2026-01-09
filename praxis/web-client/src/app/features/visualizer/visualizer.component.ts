import { Component, ChangeDetectionStrategy, signal, computed, effect, inject } from '@angular/core';

import { DeckViewComponent } from '@shared/components/deck-view/deck-view.component';
import { PlrResource, PlrDeckData } from '@core/models/plr.models';
import { AssetService } from '@features/assets/services/asset.service';
import { Machine } from '@features/assets/models/asset.models';

interface DeckWindow {
  id: string;
  title: string;
  data: PlrDeckData;
  visible: boolean;
}

@Component({
  selector: 'app-visualizer',
  standalone: true,
  imports: [DeckViewComponent],
  template: `
    <div class="workcell-container">
      <!-- Sidebar -->
      <aside class="sidebar">
        <h3>Workcell</h3>
        <div class="deck-list">
          @if (decks().length === 0) {
            <div class="no-machines">
              No machines found
            </div>
          }
          @for (deck of decks(); track deck.id) {
            <button 
              class="deck-toggle" 
              [class.active]="deck.visible"
              (click)="toggleDeck(deck.id)">
              <span class="status-indicator"></span>
              {{ deck.title }}
            </button>
          }
        </div>
      </aside>

      <!-- Main Canvas -->
      <main class="canvas" data-tour-id="visualizer-canvas">
        @if (openDecks().length === 0) {
          <div class="empty-state">
            <p>Select a deck to visualize or add a machine in Assets</p>
          </div>
        } @else {
          <div class="windows-grid">
            @for (deck of openDecks(); track deck.id) {
              <div class="deck-window">
                <header class="window-header">
                  <span>{{ deck.title }}</span>
                  <button class="close-btn" (click)="toggleDeck(deck.id)">×</button>
                </header>
                <div class="window-content">
                  @if (deck.data.resource) {
                    <app-deck-view 
                      [resource]="deck.data.resource"
                      [state]="deck.data.state">
                    </app-deck-view>
                  } @else {
                    <div class="no-data">
                      No deck state available
                    </div>
                  }
                </div>
              </div>
            }
          </div>
        }
      </main>
    </div>
  `,
  styles: [`
    :host {
      display: block;
      height: 100%;
    }

    .workcell-container {
      display: flex;
      height: 100%;
      background: var(--sys-surface);
    }

    .sidebar {
      width: 250px;
      background: var(--sys-surface-container);
      border-right: 1px solid var(--sys-outline-variant);
      padding: 16px;
      display: flex;
      flex-direction: column;
    }

    .sidebar h3 {
      margin-top: 0;
      font-size: 1.1rem;
      color: var(--sys-on-surface);
      margin-bottom: 16px;
    }

    .deck-list {
      display: flex;
      flex-direction: column;
      gap: 8px;
    }
    
    .no-machines {
      color: var(--sys-on-surface-variant);
      font-style: italic;
      font-size: 0.9rem;
      padding: 8px;
    }

    .deck-toggle {
      display: flex;
      align-items: center;
      gap: 12px;
      padding: 10px 12px;
      border: none;
      background: transparent;
      color: var(--sys-on-surface-variant);
      cursor: pointer;
      border-radius: 8px;
      text-align: left;
      font-weight: 500;
      transition: background 0.2s;
    }

    .deck-toggle:hover {
      background: var(--sys-surface-container-high);
    }

    .deck-toggle.active {
      background: var(--sys-primary-container);
      color: var(--sys-on-primary-container);
    }

    .status-indicator {
      width: 8px;
      height: 8px;
      border-radius: 50%;
      background: var(--sys-outline);
    }

    .deck-toggle.active .status-indicator {
      background: var(--sys-primary);
    }

    .canvas {
      flex: 1;
      padding: 20px;
      overflow: auto;
      background: var(--sys-background);
      position: relative;
    }

    .empty-state {
      height: 100%;
      display: flex;
      align-items: center;
      justify-content: center;
      color: var(--sys-outline);
    }

    .windows-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
      gap: 20px;
      align-items: start;
    }

    .deck-window {
      background: var(--sys-surface-container-lowest);
      border: 1px solid var(--sys-outline-variant);
      border-radius: 12px;
      overflow: hidden;
      display: flex;
      flex-direction: column;
      box-shadow: 0 2px 8px rgba(0,0,0,0.05);
      min-height: 400px;
    }

    .window-header {
      padding: 12px 16px;
      background: var(--sys-surface-container-low);
      border-bottom: 1px solid var(--sys-outline-variant);
      display: flex;
      justify-content: space-between;
      align-items: center;
      font-weight: 500;
    }

    .close-btn {
      background: none;
      border: none;
      font-size: 1.2rem;
      cursor: pointer;
      color: var(--sys-on-surface-variant);
      padding: 0 4px;
    }

    .close-btn:hover {
      color: var(--sys-error);
    }

    .window-content {
      flex: 1;
      position: relative;
      height: 400px; /* Fixed height for now */
      overflow: hidden;
      display: flex;
      align-items: center;
      justify-content: center;
    }
    
    .no-data {
      color: var(--sys-outline);
      font-style: italic;
    }
    
    app-deck-view {
      height: 100%;
      width: 100%;
    }
  `],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class VisualizerComponent {
  private assetService = inject(AssetService);

  // Signals
  decks = signal<DeckWindow[]>([]);
  openDecks = computed(() => this.decks().filter(d => d.visible));

  constructor() {
    this.loadMachines();

    // Persist changes
    effect(() => {
      const state = this.decks().map(d => ({ id: d.id, visible: d.visible }));
      if (state.length > 0) {
        localStorage.setItem('praxis_workcell_layout', JSON.stringify(state));
      }
    });
  }

  private loadMachines() {
    this.assetService.getMachines().subscribe((machines: Machine[]) => {
      const saved = localStorage.getItem('praxis_workcell_layout');
      let savedState: any[] = [];
      try {
        if (saved) savedState = JSON.parse(saved);
      } catch (e) {
        console.warn('Failed to parse saved layout', e);
      }

      const deckWindows: DeckWindow[] = machines.map((m: Machine) => {
        // Try to find saved visibility
        const savedMachine = savedState.find((s: any) => s.id === m.accession_id);
        const isVisible = savedMachine ? savedMachine.visible : false;

        // Use PLR state or legacy definition
        let deckData: PlrDeckData = { resource: null as any, state: {} };

        if (m.plr_state) {
          deckData = { resource: m.plr_state, state: {} };
        } else if (m.plr_definition) {
          deckData = { resource: m.plr_definition, state: {} };
        }

        return {
          id: m.accession_id,
          title: m.name,
          data: deckData,
          visible: isVisible
        };
      });

      // If no persisted state and we have machines, open the first one by default
      if (!saved && deckWindows.length > 0) {
        deckWindows[0].visible = true;
      }

      this.decks.set(deckWindows);
    });
  }

  toggleDeck(id: string) {
    this.decks.update(decks =>
      decks.map(d => d.id === id ? { ...d, visible: !d.visible } : d)
    );
  }
}