import { Component, computed, inject, signal } from '@angular/core';

import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatTabsModule } from '@angular/material/tabs';
import { MarkdownModule } from 'ngx-markdown';
import { AppStore } from '../../../../core/store/app.store';
import { DiagramOverlayComponent } from '../../../../shared/components/diagram-overlay/diagram-overlay.component';

@Component({
  selector: 'app-system-topology',
  standalone: true,
  imports: [MatTabsModule, MatButtonModule, MatIconModule, MarkdownModule, DiagramOverlayComponent],
  template: `
    <div class="system-topology surface-elevated">
      <div class="header">
        <h3>System Architecture</h3>
        <p class="text-secondary">Explore the architecture across different deployment modes.</p>
      </div>
      
      <mat-tab-group animationDuration="0ms" class="topology-tabs">
        <mat-tab label="Production">
          <ng-template matTabContent>
            <div class="diagram-container">
              <button mat-icon-button class="expand-btn" (click)="expandDiagram($event)" title="Fullscreen">
                <mat-icon>fullscreen</mat-icon>
              </button>
              <markdown [data]="productionDiagram" mermaid [mermaidOptions]="mermaidOptions()"></markdown>
               <div class="legend">
                <div class="item"><span class="dot angular"></span> Frontend</div>
                <div class="item"><span class="dot api"></span> API Layer</div>
                <div class="item"><span class="dot core"></span> Core Engine</div>
              </div>
            </div>
          </ng-template>
        </mat-tab>
        <mat-tab label="Lite Mode">
          <ng-template matTabContent>
            <div class="diagram-container">
              <button mat-icon-button class="expand-btn" (click)="expandDiagram($event)" title="Fullscreen">
                <mat-icon>fullscreen</mat-icon>
              </button>
              <markdown [data]="liteDiagram" mermaid [mermaidOptions]="mermaidOptions()"></markdown>
            </div>
          </ng-template>
        </mat-tab>
        <mat-tab label="Browser (Pyodide)">
          <ng-template matTabContent>
            <div class="diagram-container">
              <button mat-icon-button class="expand-btn" (click)="expandDiagram($event)" title="Fullscreen">
                <mat-icon>fullscreen</mat-icon>
              </button>
              <markdown [data]="browserDiagram" mermaid [mermaidOptions]="mermaidOptions()"></markdown>
            </div>
          </ng-template>
        </mat-tab>
      </mat-tab-group>

      @if (expandedDiagram()) {
        <app-diagram-overlay
          [diagramHtml]="expandedDiagram()!"
          (closed)="closeExpanded()">
        </app-diagram-overlay>
      }
    </div>
  `,
  styles: [`
    .system-topology {
      border-radius: 16px;
      margin: 32px 0;
      overflow: hidden;
      border: 1px solid var(--theme-border);
    }

    .header {
      padding: 24px 24px 0;
    }

    .header h3 {
      margin: 0 0 8px;
      color: var(--theme-text-primary);
    }

    .diagram-container {
      padding: 24px;
      min-height: 400px;
      display: flex;
      flex-direction: column;
      align-items: center;
      position: relative;
    }

    .expand-btn {
      position: absolute;
      top: 32px;
      right: 32px;
      z-index: 10;
      background: var(--mat-sys-surface-container-highest);
      color: var(--theme-text-primary);
      box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
    }

    .expand-btn:hover {
      background: var(--theme-surface-elevated);
      transform: scale(1.1);
    }

    .legend {
      display: flex;
      gap: 16px;
      margin-top: 16px;
      font-size: 0.9rem;
      color: var(--theme-text-secondary);
    }

    .item {
      display: flex;
      align-items: center;
      gap: 8px;
    }

    .dot {
      width: 10px;
      height: 10px;
      border-radius: 50%;
      border: 2px solid;
    }

    .dot.angular { border-color: #ed7a9b; background: rgba(237, 122, 155, 0.2); }
    .dot.api { border-color: #73a9c2; background: rgba(115, 169, 194, 0.2); }
    .dot.core { border-color: #ed7a9b; background: rgba(237, 122, 155, 0.2); }

    /* Fix mermaid container inside tab */
    :host ::ng-deep .mermaid {
      background: none !important;
      border: none !important;
      padding: 0 !important;
      margin: 0 !important;
    }
  `]
})
export class SystemTopologyComponent {
  private store = inject(AppStore);
  expandedDiagram = signal<string | null>(null);

  expandDiagram(event: Event): void {
    const target = event.currentTarget as HTMLElement;
    const container = target.closest('.diagram-container');
    const mermaidDiv = container?.querySelector('.mermaid');

    if (mermaidDiv) {
      this.expandedDiagram.set(mermaidDiv.innerHTML);
    }
  }

  closeExpanded(): void {
    this.expandedDiagram.set(null);
  }

  mermaidOptions = computed(() => {
    const theme = this.store.theme();
    let isDark = theme === 'dark';
    if (theme === 'system') {
      isDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
    }
    const common = {
      fontFamily: '"Roboto Flex", sans-serif',
      fontSize: '16px',
    };

    return {
      theme: 'base' as const,
      flowchart: {
        htmlLabels: true,
        useMaxWidth: false,
        nodeSpacing: 60,
        rankSpacing: 60,
        curve: 'basis' as const
      },
      themeVariables: isDark ? {
        ...common,
        darkMode: true,
        background: 'transparent',
        mainBkg: 'transparent',
        primaryColor: '#2a2a3c', primaryTextColor: '#ffffff', primaryBorderColor: '#ed7a9b',
        secondaryColor: '#1a1a2e', secondaryTextColor: '#ffffff', secondaryBorderColor: '#73a9c2',
        lineColor: 'rgba(255, 255, 255, 0.6)', textColor: '#ffffff'
      } : {
        ...common,
        darkMode: false,
        background: 'transparent',
        mainBkg: 'transparent',
        primaryColor: '#fbf9e6', primaryTextColor: '#020617', primaryBorderColor: '#ed7a9b',
        secondaryColor: '#ffffff', secondaryTextColor: '#020617', secondaryBorderColor: '#73a9c2',
        lineColor: '#1e293b', textColor: '#020617'
      }
    };
  });

  productionDiagram = `
\`\`\`mermaid
graph TD
    subgraph Frontend ["Frontend (Angular)"]
        UI[Web UI]
        Store[NgRx Store]
        Services[Frontend Services]
    end
    style Frontend fill:transparent,stroke:#ed7a9b,stroke-width:2px

    subgraph API ["API Layer"]
        Server[FastAPI Server]
        WS[WebSocket Handler]
    end
    style API fill:transparent,stroke:#73a9c2,stroke-width:2px

    subgraph Core ["Core Engine"]
        Orch[Orchestrator]
        Sched[Scheduler]
        Proto[Protocol Engine]
        Asset[Asset Manager]
    end
    style Core fill:transparent,stroke:#ed7a9b,stroke-width:2px

    subgraph Runtime ["Runtime"]
        WCR[WorkcellRuntime]
        PLR[PyLabRobot]
        Sim[Simulators]
    end
    style Runtime fill:transparent,stroke:#73a9c2,stroke-width:2px

    subgraph Data ["Data Layer"]
        PG[(PostgreSQL)]
        Redis[(Redis)]
    end
    style Data fill:transparent,stroke:#73a9c2,stroke-width:2px

    UI --> Server
    UI --> WS
    Store --> Services
    Services --> Server
    Server --> Orch
    WS --> Orch
    Orch --> Proto
    Orch --> Sched
    Orch --> WCR
    WCR --> PLR
    Server --> PG
    Orch --> Redis
\`\`\`
`;

  liteDiagram = `
\`\`\`mermaid
graph TD
    subgraph Frontend_Lite ["Frontend (Angular)"]
        UI_L[Web UI]
        Store_L[NgRx Store]
    end
    style Frontend_Lite fill:transparent,stroke:#ed7a9b,stroke-width:2px

    subgraph API_Lite ["Local API"]
        Server_L[FastAPI Process]
    end
    style API_Lite fill:transparent,stroke:#73a9c2,stroke-width:2px

    subgraph Core_Lite ["Core Engine"]
        Orch_L[Orchestrator]
        Asset_L[Asset Manager]
    end
    style Core_Lite fill:transparent,stroke:#ed7a9b,stroke-width:2px

    subgraph Runtime_Lite ["Runtime"]
        WCR_L[WorkcellRuntime]
        PLR_L[PyLabRobot]
    end
    style Runtime_Lite fill:transparent,stroke:#73a9c2,stroke-width:2px

    subgraph Data_Lite ["Data Layer"]
        SQLite[(SQLite)]
    end
    style Data_Lite fill:transparent,stroke:#73a9c2,stroke-width:2px

    UI_L --> Server_L
    Store_L --> Server_L
    Server_L --> Orch_L
    Server_L --> Asset_L
    Orch_L --> WCR_L
    Asset_L --> WCR_L
    WCR_L --> PLR_L
    Server_L --> SQLite
    WCR_L --> SQLite
\`\`\`
`;

  browserDiagram = `
\`\`\`mermaid
graph TD
    subgraph Frontend_Browser ["Frontend (Browser Only)"]
        UI_B[Web UI]
        Store_B[NgRx Store]
        IO_Shim[IO Shim Service]
    end
    style Frontend_Browser fill:transparent,stroke:#ed7a9b,stroke-width:2px

    subgraph WebWorker ["Web Worker (Pyodide)"]
        PyBridge[Python Bridge]
        Core_B[Core Engine]
        PLR_B[PyLabRobot]
    end
    style WebWorker fill:transparent,stroke:#73a9c2,stroke-width:2px

    subgraph BrowserData ["Browser Storage"]
        IDB[(IndexedDB)]
        LocalStorage[(LocalStorage)]
    end
    style BrowserData fill:transparent,stroke:#ed7a9b,stroke-width:2px

    subgraph Hardware ["Physical Hardware"]
        USB[WebSerial / USB]
        Bluetooth[WebBluetooth]
    end
    style Hardware fill:transparent,stroke:#73a9c2,stroke-width:2px

    UI_B --> Store_B
    Store_B --> PyBridge
    PyBridge --> Core_B
    Core_B --> PLR_B
    PLR_B --> IO_Shim
    IO_Shim --> USB
    Store_B --> IDB
\`\`\`
`;
}
