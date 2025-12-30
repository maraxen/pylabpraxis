import { Component, computed, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatTabsModule } from '@angular/material/tabs';
import { MarkdownModule } from 'ngx-markdown';
import { AppStore } from '../../../../core/store/app.store';

@Component({
    selector: 'app-system-topology',
    standalone: true,
    imports: [CommonModule, MatTabsModule, MarkdownModule],
    template: `
    <div class="system-topology surface-elevated">
      <div class="header">
        <h3>System Architecture</h3>
        <p class="text-secondary">Explore the architecture across different deployment modes.</p>
      </div>
      
      <mat-tab-group animationDuration="0ms" class="topology-tabs">
        <mat-tab label="Production">
          <div class="diagram-container">
            <markdown [data]="productionDiagram" mermaid [mermaidOptions]="mermaidOptions()"></markdown>
             <div class="legend">
              <div class="item"><span class="dot angular"></span> Frontend</div>
              <div class="item"><span class="dot api"></span> API Layer</div>
              <div class="item"><span class="dot core"></span> Core Engine</div>
            </div>
          </div>
        </mat-tab>
        <mat-tab label="Lite Mode">
          <div class="diagram-container">
            <markdown [data]="liteDiagram" mermaid [mermaidOptions]="mermaidOptions()"></markdown>
          </div>
        </mat-tab>
        <mat-tab label="Browser (Pyodide)">
          <div class="diagram-container">
            <markdown [data]="browserDiagram" mermaid [mermaidOptions]="mermaidOptions()"></markdown>
          </div>
        </mat-tab>
      </mat-tab-group>
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

    mermaidOptions = computed(() => {
        const theme = this.store.theme();
        let isDark = theme === 'dark';
        if (theme === 'system') {
            isDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
        }
        const common = {
            fontFamily: '"Roboto Flex", sans-serif',
            fontSize: '16px',
            flowchart: { nodeSpacing: 60, rankSpacing: 60, curve: 'basis' }
        };

        return {
            theme: 'base' as const,
            flowchart: { htmlLabels: true, useMaxWidth: false },
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
                primaryColor: '#f1f5f9', primaryTextColor: '#020617', primaryBorderColor: '#ed7a9b',
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
    style Frontend fill:transparent,stroke:#ed7a9b,stroke-width:2px,color:#fff

    subgraph API ["API Layer"]
        Server[FastAPI Server]
        WS[WebSocket Handler]
    end
    style API fill:transparent,stroke:#73a9c2,stroke-width:2px,color:#fff

    subgraph Core ["Core Engine"]
        Orch[Orchestrator]
        Sched[Scheduler]
        Proto[Protocol Engine]
        Asset[Asset Manager]
    end
    style Core fill:transparent,stroke:#ed7a9b,stroke-width:2px,color:#fff

    subgraph Runtime ["Runtime"]
        WCR[WorkcellRuntime]
        PLR[PyLabRobot]
        Sim[Simulators]
    end
    style Runtime fill:transparent,stroke:#73a9c2,stroke-width:2px,color:#fff

    subgraph Data ["Data Layer"]
        PG[(PostgreSQL)]
        Redis[(Redis)]
    end
    style Data fill:transparent,stroke:#73a9c2,stroke-width:2px,color:#fff

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
    style Frontend_Lite fill:transparent,stroke:#ed7a9b,stroke-width:2px,color:#fff

    subgraph API_Lite ["Local API"]
        Server_L[FastAPI Process]
    end
    style API_Lite fill:transparent,stroke:#73a9c2,stroke-width:2px,color:#fff

    subgraph Core_Lite ["Core Engine"]
        Orch_L[Orchestrator]
        Asset_L[Asset Manager]
    end
    style Core_Lite fill:transparent,stroke:#ed7a9b,stroke-width:2px,color:#fff

    subgraph Runtime_Lite ["Runtime"]
        WCR_L[WorkcellRuntime]
        PLR_L[PyLabRobot]
    end
    style Runtime_Lite fill:transparent,stroke:#73a9c2,stroke-width:2px,color:#fff

    subgraph Data_Lite ["Data Layer"]
        SQLite[(SQLite)]
    end
    style Data_Lite fill:transparent,stroke:#73a9c2,stroke-width:2px,color:#fff

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
    style Frontend_Browser fill:transparent,stroke:#ed7a9b,stroke-width:2px,color:#fff

    subgraph WebWorker ["Web Worker (Pyodide)"]
        PyBridge[Python Bridge]
        Core_B[Core Engine]
        PLR_B[PyLabRobot]
    end
    style WebWorker fill:transparent,stroke:#73a9c2,stroke-width:2px,color:#fff

    subgraph BrowserData ["Browser Storage"]
        IDB[(IndexedDB)]
        LocalStorage[(LocalStorage)]
    end
    style BrowserData fill:transparent,stroke:#ed7a9b,stroke-width:2px,color:#fff

    subgraph Hardware ["Physical Hardware"]
        USB[WebSerial / USB]
        Bluetooth[WebBluetooth]
    end
    style Hardware fill:transparent,stroke:#73a9c2,stroke-width:2px,color:#fff

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
