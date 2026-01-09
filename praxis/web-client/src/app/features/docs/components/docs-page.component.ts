import { Component, computed, effect, ElementRef, HostListener, inject, signal } from '@angular/core';
import { MatButtonModule } from '@angular/material/button';
import { MatButtonToggleModule } from '@angular/material/button-toggle';
import { MatIconModule } from '@angular/material/icon';
import { AppStore } from '../../../core/store/app.store';
import { DiagramOverlayComponent } from '../../../shared/components/diagram-overlay/diagram-overlay.component';

import { HttpClient } from '@angular/common/http';
import { ActivatedRoute } from '@angular/router';
import { MarkdownModule } from 'ngx-markdown';
import { catchError, of } from 'rxjs';
import { SystemTopologyComponent } from './system-topology/system-topology.component';

@Component({
  selector: 'app-docs-page',
  standalone: true,
  imports: [
    MarkdownModule,
    SystemTopologyComponent,
    MatButtonModule,
    MatButtonToggleModule,
    MatIconModule,
    DiagramOverlayComponent
  ],
  template: `
    <div class="docs-page">
      @if (showModeSwitch()) {
        <div class="mode-switch-container">
          <mat-button-toggle-group [value]="viewMode()" (change)="viewMode.set($event.value)" aria-label="Documentation Mode">
            <mat-button-toggle value="production">Production Mode</mat-button-toggle>
            <mat-button-toggle value="browser">Browser Mode</mat-button-toggle>
          </mat-button-toggle-group>
        </div>
      }

      @if (loading()) {
        <div class="loading">
          <div class="loading-spinner"></div>
          <p>Loading documentation...</p>
        </div>
      } @else if (error()) {
        <div class="error">
          <h2>Page Not Found</h2>
          <p>{{ error() }}</p>
        </div>
      } @else {
        <div class="docs-header-actions">
           @if (sourcePath()) {
            <button class="source-btn" (click)="viewSource()" [attr.title]="sourcePath()">
              <i class="material-icons">code</i>
              <span>View Source</span>
            </button>
          }
        </div>
        <article class="docs-article">
          @if (showSystemTopology()) {
            <app-system-topology></app-system-topology>
          }
          <markdown [data]="markdownContent()" mermaid [mermaidOptions]="mermaidOptions()" (ready)="onMarkdownReady()"></markdown>
        </article>

        @if (expandedDiagram()) {
          <app-diagram-overlay
            [diagramHtml]="expandedDiagram()!"
            (closed)="closeExpanded()">
          </app-diagram-overlay>
        }
      }
    </div>
  `,
  styles: [`
    .docs-page {
      max-width: 900px;
      margin: 0 auto;
      padding: 32px 48px;
      position: relative;
    }

    .mode-switch-container {
      display: flex;
      justify-content: center;
      margin-bottom: 32px;
    }

    .docs-header-actions {
      position: absolute;
      top: 32px;
      right: 48px;
      z-index: 10;
    }

    .source-btn {
      display: flex;
      align-items: center;
      gap: 8px;
      padding: 6px 12px;
      border-radius: 8px;
      background: var(--mat-sys-surface-variant);
      border: 1px solid var(--theme-border);
      color: var(--theme-text-secondary);
      font-size: 0.8rem;
      cursor: pointer;
      transition: all 0.2s;
    }

    .source-btn:hover {
      background: var(--theme-surface-elevated);
      border-color: var(--primary-color);
      color: var(--theme-text-primary);
    }

    .source-btn i {
      font-size: 1.1rem;
    }

    .loading {
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      min-height: 300px;
      color: var(--theme-text-secondary);
    }

    .loading-spinner {
      width: 40px;
      height: 40px;
      border: 3px solid var(--theme-border);
      border-top-color: var(--primary-color);
      border-radius: 50%;
      animation: spin 1s linear infinite;
      margin-bottom: 16px;
    }

    @keyframes spin {
      to { transform: rotate(360deg); }
    }

    .error {
      text-align: center;
      padding: 48px;
      color: var(--theme-text-secondary);
    }

    .error h2 {
      color: var(--theme-text-primary);
      margin-bottom: 8px;
    }

    /* Markdown Styling */
    .docs-article {
      color: var(--theme-text-primary);
      line-height: 1.7;
    }

    :host ::ng-deep {
      h1 {
        font-size: 2.5rem;
        font-weight: 700;
        color: var(--theme-text-primary);
        margin: 0 0 16px;
        padding-bottom: 16px;
        border-bottom: 1px solid var(--theme-border);
      }

      h2 {
        font-size: 1.75rem;
        font-weight: 600;
        color: var(--theme-text-primary);
        margin: 48px 0 16px;
      }

      h3 {
        font-size: 1.25rem;
        font-weight: 600;
        color: var(--theme-text-primary);
        margin: 32px 0 12px;
      }

      h4 {
        font-size: 1rem;
        font-weight: 600;
        color: var(--theme-text-primary);
        margin: 24px 0 8px;
      }

      p {
        margin: 0 0 16px;
        color: var(--theme-text-secondary);
      }

      a {
        color: var(--primary-color);
        text-decoration: none;
        transition: opacity 0.2s;
      }

      a:hover {
        opacity: 0.8;
        text-decoration: underline;
      }

      code {
        font-family: 'JetBrains Mono', 'Fira Code', monospace;
        font-size: 0.9em;
        background: var(--mat-sys-surface-variant);
        padding: 2px 6px;
        border-radius: 4px;
        color: var(--primary-color);
      }

      kbd {
        display: inline-block;
        padding: 2px 6px;
        font-family: 'JetBrains Mono', 'Fira Code', monospace;
        font-size: 0.85em;
        line-height: 1.2;
        color: var(--theme-text-primary);
        vertical-align: middle;
        background-color: var(--mat-sys-surface-container);
        border: 1px solid var(--theme-border);
        border-radius: 6px;
        box-shadow: 0 2px 0 var(--theme-border);
        margin: 0 2px;
      }

      pre {
        background: var(--mat-sys-surface-container);
        border: 1px solid var(--theme-border);
        border-radius: 12px;
        padding: 20px;
        overflow-x: auto;
        margin: 16px 0 24px;
      }

      pre code {
        background: none;
        padding: 0;
        color: var(--theme-text-primary);
        font-size: 0.85rem;
        line-height: 1.6;
      }

      ul, ol {
        margin: 0 0 16px;
        padding-left: 24px;
      }

      li {
        margin-bottom: 8px;
        color: var(--theme-text-secondary);
      }

      table {
        width: 100%;
        border-collapse: collapse;
        margin: 16px 0 24px;
        font-size: 0.9rem;
      }

      th {
        text-align: left;
        padding: 12px 16px;
        background: var(--mat-sys-surface-variant);
        border: 1px solid var(--theme-border);
        color: var(--theme-text-primary);
        font-weight: 600;
      }

      td {
        padding: 12px 16px;
        border: 1px solid var(--theme-border);
        color: var(--theme-text-secondary);
      }

      tr:hover td {
        background: var(--mat-sys-surface-variant);
      }

      blockquote {
        margin: 16px 0;
        padding: 16px 20px;
        background: var(--mat-sys-surface-variant);
        border-left: 4px solid var(--primary-color);
        border-radius: 0 8px 8px 0;
      }

      blockquote p {
        margin: 0;
        color: var(--theme-text-secondary);
      }

      hr {
        border: none;
        height: 1px;
        background: var(--theme-border);
        margin: 32px 0;
      }

      /* Admonitions (note, warning, etc.) */
      .admonition {
        padding: 16px 20px;
        margin: 16px 0;
        border-radius: 8px;
        border-left: 4px solid;
      }

      .admonition.note {
        background: rgba(59, 130, 246, 0.1);
        border-color: #3b82f6;
      }

      .admonition.warning {
        background: rgba(245, 158, 11, 0.1);
        border-color: #f59e0b;
      }

      .admonition.danger {
        background: rgba(239, 68, 68, 0.1);
        border-color: #ef4444;
      }

      .admonition-title {
        font-weight: 600;
        margin-bottom: 8px;
        color: var(--theme-text-primary);
      }

      .mermaid {
        background: linear-gradient(145deg, var(--mat-sys-surface-variant) 0%, transparent 100%);
        border: 1px solid var(--theme-border);
        border-radius: 16px;
        padding: 32px;
        margin: 24px 0;
        display: flex;
        justify-content: center;
        overflow-x: auto;
        position: relative;
      }

      .diagram-wrapper {
        position: relative;
        margin: 24px 0;
      }

      .diagram-wrapper .mermaid {
        margin: 0;
      }

      .expand-btn {
        position: absolute;
        top: 12px;
        right: 12px;
        z-index: 20;
        background: var(--mat-sys-surface-container-highest) !important;
        color: var(--theme-text-primary) !important;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
        opacity: 0.7;
        transition: all 0.2s ease !important;
        border: none;
        border-radius: 8px;
        padding: 8px;
        cursor: pointer;
        display: flex;
        align-items: center;
        justify-content: center;
      }

      .expand-btn:hover {
        opacity: 1;
        transform: scale(1.05);
        background: var(--theme-surface-elevated) !important;
      }

      .expand-btn i {
        font-size: 20px !important;
      }
    }

    @media (max-width: 768px) {
      .docs-page {
        padding: 24px 20px;
      }

      :host ::ng-deep {
        h1 {
          font-size: 2rem;
        }

        h2 {
          font-size: 1.5rem;
        }

        pre {
          padding: 16px;
          border-radius: 8px;
        }

        table {
          display: block;
          overflow-x: auto;
        }
      }
    }
  `]
})
export class DocsPageComponent {
  private route = inject(ActivatedRoute);
  private http = inject(HttpClient);
  private store = inject(AppStore);
  private el = inject(ElementRef);

  expandedDiagram = signal<string | null>(null);

  mermaidOptions = computed(() => {
    const theme = this.store.theme();
    let isDark = theme === 'dark';

    if (theme === 'system') {
      isDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
    }

    return {
      theme: 'base' as const,
      flowchart: {
        htmlLabels: true,
        useMaxWidth: false,
        nodeSpacing: 60,
        rankSpacing: 60,
        curve: 'basis' as const
      },
      themeVariables: {
        fontFamily: '"Roboto Flex", sans-serif',
        fontSize: '18px',
        darkMode: isDark,
        background: 'transparent',
        mainBkg: 'transparent',
        primaryColor: 'var(--mat-sys-primary-container)',
        primaryTextColor: 'var(--mat-sys-on-primary-container)',
        primaryBorderColor: 'var(--mat-sys-outline)',
        lineColor: 'var(--mat-sys-outline)',
        secondaryColor: 'var(--mat-sys-secondary-container)',
        tertiaryColor: 'var(--mat-sys-tertiary-container)',
        nodeBkg: 'var(--mat-sys-surface-container-high)',
        textColor: 'var(--mat-sys-on-surface)',
        noteBkgColor: 'var(--mat-sys-surface-container-low)',
        noteTextColor: 'var(--mat-sys-on-surface)',
        noteBorderColor: 'var(--mat-sys-outline)',

        // Sequence Diagram specific
        actorBkg: 'var(--mat-sys-surface-container-high)',
        actorBorder: 'var(--mat-sys-outline)',
        actorTextColor: 'var(--mat-sys-on-surface)',
        actorLineColor: 'var(--mat-sys-outline)',
        signalColor: 'var(--mat-sys-on-surface)',
        signalTextColor: 'var(--mat-sys-on-surface)',
        labelBoxBkgColor: 'var(--mat-sys-surface-container-high)',
        labelBoxBorderColor: 'var(--mat-sys-outline)',
        labelTextColor: 'var(--mat-sys-on-surface)',
        loopTextColor: 'var(--mat-sys-on-surface)',
        sequenceNumberColor: 'var(--mat-sys-on-primary-container)',
      }
    };
  });

  markdownContent = signal<string>('');
  sourcePath = signal<string | null>(null);
  loading = signal(true);
  error = signal<string | null>(null);
  viewMode = signal<'production' | 'browser'>('production');
  showModeSwitch = signal(false);

  showSystemTopology = signal(false);

  constructor() {
    effect(() => {
      const params = this.route.snapshot.params;
      const data = this.route.snapshot.data;
      const mode = this.viewMode();

      const section = data['section'] || params['section'];
      const page = params['page'] || data['page'] || 'index';

      this.loadMarkdown(section, page, mode);

      // Only show mode switch for architecture pages where it matters
      this.showModeSwitch.set(section === 'architecture' && (page === 'overview' || page === 'backend'));

      // We are handling topology in the markdown files now via mode switching
      this.showSystemTopology.set(false);
    }, { allowSignalWrites: true });

    // Also react to route changes
    this.route.params.subscribe(() => {
      const params = this.route.snapshot.params;
      const data = this.route.snapshot.data;

      const section = data['section'] || params['section'];
      const page = params['page'] || data['page'] || 'index';

      this.loadMarkdown(section, page, this.viewMode());
      this.showModeSwitch.set(section === 'architecture' && (page === 'overview' || page === 'backend'));
      this.showSystemTopology.set(false);
    });
  }

  private loadMarkdown(section: string, page: string, mode: string): void {
    this.loading.set(true);
    this.error.set(null);
    this.sourcePath.set(null);

    // Try to load mode-specific file first: page-mode.md
    const modePath = `assets/docs/${section}/${page}-${mode}.md`;
    // Default fallback
    const defaultPath = `assets/docs/${section}/${page}.md`;

    this.http.get(modePath, { responseType: 'text' })
      .pipe(
        catchError(() => {
          // If mode specific not found, try default
          return this.http.get(defaultPath, { responseType: 'text' }).pipe(
            catchError(() => {
               // If default not found with section, try root default
               return this.http.get(`assets/docs/${page}.md`, { responseType: 'text' }).pipe(
                 catchError(() => of(null))
               );
            })
          );
        })
      )
      .subscribe({
        next: (content) => {
          if (content) {
            let processedContent = content;

            // Parse source metadata (Source: path/to/file)
            const sourceMatch = content.match(/^Source:\s*(.+)$/m);
            if (sourceMatch) {
              this.sourcePath.set(sourceMatch[1].trim());
              processedContent = processedContent.replace(/^Source:\s*.+$/m, '').trim();
            }

            // We removed the special system diagram stripping since we are using mode-specific files
            this.markdownContent.set(processedContent);
            this.loading.set(false);
          } else {
            this.error.set(`Documentation page "${section}/${page}" not found.`);
            this.loading.set(false);
          }
        },
        error: () => {
          this.error.set(`Failed to load documentation.`);
          this.loading.set(false);
        }
      });
  }

  viewSource(): void {
    const path = this.sourcePath();
    if (path) {
      // Open source file on GitHub
      const githubRepo = 'https://github.com/maraxen/pylabpraxis/blob/main/';
      window.open(`${githubRepo}${path}`, '_blank');
    }
  }

  onMarkdownReady(): void {
    // Inject expand buttons into Mermaid diagrams
    setTimeout(() => {
      const article = this.el.nativeElement.querySelector('.docs-article');
      if (!article) return;

      const diagrams = article.querySelectorAll('.mermaid');
      diagrams.forEach((d: HTMLElement) => {
        // Skip if already wrapped or has button
        if (d.parentElement?.classList.contains('diagram-wrapper')) return;

        const wrapper = document.createElement('div');
        wrapper.className = 'diagram-wrapper';

        d.parentNode?.insertBefore(wrapper, d);
        wrapper.appendChild(d);

        const btn = document.createElement('button');
        btn.className = 'expand-btn';
        btn.title = 'Fullscreen';
        btn.innerHTML = '<i class="material-icons">fullscreen</i>';

        btn.onclick = (e) => {
          e.stopPropagation();
          // We need to get the innerHTML of the mermaid div
          this.expandedDiagram.set(d.innerHTML);
        };

        wrapper.appendChild(btn);
      });
    }, 100);
  }

  closeExpanded(): void {
    this.expandedDiagram.set(null);
  }

  @HostListener('window:keydown.escape')
  onEscape(): void {
    this.closeExpanded();
  }
}
