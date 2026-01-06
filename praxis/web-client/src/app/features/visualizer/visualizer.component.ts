import { Component, ChangeDetectionStrategy, signal, computed, effect } from '@angular/core';

import { DeckViewComponent } from '@shared/components/deck-view/deck-view.component';
import { PlrResource, PlrDeckData } from '@core/models/plr.models';

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
            <p>Select a deck to visualize</p>
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
                  <app-deck-view 
                    [resource]="deck.data.resource"
                    [state]="deck.data.state">
                  </app-deck-view>
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
    }
    
    app-deck-view {
      height: 100%;
    }
  `],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class VisualizerComponent {
  // Signals
  decks = signal<DeckWindow[]>([]);
  openDecks = computed(() => this.decks().filter(d => d.visible));

  constructor() {
    // Load persisted state or default
    const saved = localStorage.getItem('praxis_workcell_layout');

    // Demo data creation
    const demoDeck = this.createDemoDeck();

    if (saved) {
      try {
        const savedState = JSON.parse(saved);
        // Merge saved visibility with fresh data
        // For MVP just resetting to demo
        this.decks.set([
          { id: 'deck-1', title: 'Hamilton STAR', data: demoDeck, visible: true },
          { id: 'deck-2', title: 'Opentrons Flex', data: demoDeck, visible: false }
        ]);
      } catch (e) {
        this.setDefaultState(demoDeck);
      }
    } else {
      this.setDefaultState(demoDeck);
    }

    // Persist changes
    effect(() => {
      const state = this.decks().map(d => ({ id: d.id, visible: d.visible }));
      localStorage.setItem('praxis_workcell_layout', JSON.stringify(state));
    });
  }

  setDefaultState(data: PlrDeckData) {
    this.decks.set([
      { id: 'deck-1', title: 'Hamilton STAR', data: data, visible: true },
      { id: 'deck-2', title: 'Opentrons Flex', data: data, visible: false } // Placeholder for second machine
    ]);
  }

  toggleDeck(id: string) {
    this.decks.update(decks =>
      decks.map(d => d.id === id ? { ...d, visible: !d.visible } : d)
    );
  }

  createDemoDeck(): PlrDeckData {
    return {
      resource: {
        name: 'deck',
        type: 'Deck',
        location: { x: 0, y: 0, z: 0 },
        size_x: 600,
        size_y: 400,
        size_z: 0,
        children: [
          {
            name: 'plate_1',
            type: 'Plate',
            location: { x: 100, y: 100, z: 0 },
            size_x: 127.76,
            size_y: 85.48,
            size_z: 14,
            children: [],
            color: 'rgba(100, 150, 255, 0.2)'
          },
          {
            name: 'tips_1',
            type: 'TipRack',
            location: { x: 300, y: 100, z: 0 },
            size_x: 127.76,
            size_y: 85.48,
            size_z: 60,
            children: [],
            color: 'rgba(255, 150, 100, 0.2)'
          },
          {
            name: 'trash',
            type: 'Trash',
            location: { x: 500, y: 50, z: 0 },
            size_x: 80,
            size_y: 80,
            size_z: 100,
            children: [],
            color: 'rgba(100, 100, 100, 0.1)'
          }
        ]
      },
      state: {}
    };
  }
}