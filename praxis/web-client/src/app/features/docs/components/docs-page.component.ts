import { Component, inject, signal, effect, computed } from '@angular/core';
import { AppStore } from '../../../core/store/app.store';
import { CommonModule } from '@angular/common';
import { ActivatedRoute } from '@angular/router';
import { MarkdownModule } from 'ngx-markdown';
import { HttpClient } from '@angular/common/http';
import { SystemTopologyComponent } from './system-topology/system-topology.component';
import { catchError, of } from 'rxjs';

@Component({
  selector: 'app-docs-page',
  standalone: true,
  imports: [CommonModule, MarkdownModule, SystemTopologyComponent],
  template: `
    <div class="docs-page">
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
          <markdown [data]="markdownContent()" mermaid [mermaidOptions]="mermaidOptions()"></markdown>
        </article>
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

      /* Mermaid diagrams */
      .mermaid {
        background: linear-gradient(145deg, var(--mat-sys-surface-variant) 0%, transparent 100%);
        border: 1px solid var(--theme-border);
        border-radius: 16px;
        padding: 32px;
        margin: 24px 0;
        display: flex;
        justify-content: center;
        overflow-x: auto;
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

  mermaidOptions = computed(() => {
    const theme = this.store.theme();
    let isDark = theme === 'dark';

    if (theme === 'system') {
      isDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
    }

    const common = {
      fontFamily: '"Roboto Flex", sans-serif',
      fontSize: '18px',
      flowchart: {
        nodeSpacing: 60,
        rankSpacing: 60,
        curve: 'basis'
      }
    };

    return {
      theme: 'base' as const,
      flowchart: {
        htmlLabels: true,
        useMaxWidth: false,
      },
      themeVariables: isDark ? {
        ...common,
        darkMode: true,
        background: 'transparent',
        mainBkg: 'transparent',

        // Primary (Standard Nodes)
        primaryColor: '#2a2a3c',         // Surface Container High
        primaryTextColor: '#ffffff',
        primaryBorderColor: '#ed7a9b',   // Rose Pompadour

        // Secondary (e.g. subgraphs)
        secondaryColor: '#1a1a2e',       // Surface Container Low
        secondaryTextColor: '#ffffff',
        secondaryBorderColor: '#73a9c2', // Moonstone Blue

        // Tertiary
        tertiaryColor: '#1e1e2d',
        tertiaryTextColor: '#ffffff',
        tertiaryBorderColor: '#ed7a9b',

        // Lines and Text
        lineColor: 'rgba(255, 255, 255, 0.6)',
        textColor: '#ffffff',
        noteBkgColor: '#2a2a3c',
        noteTextColor: '#ffffff',
        noteBorderColor: '#73a9c2'
      } : {
        ...common,
        darkMode: false,
        background: 'transparent',
        mainBkg: 'transparent',

        // Primary
        primaryColor: '#fbf9e6',         // Cream
        primaryTextColor: '#020617',     // Slate 950
        primaryBorderColor: '#ed7a9b',

        // Secondary
        secondaryColor: '#ffffff',
        secondaryTextColor: '#020617',
        secondaryBorderColor: '#73a9c2',

        // Lines and Text
        lineColor: '#1e293b',            // Slate 800
        textColor: '#020617',
        noteBkgColor: '#fffdf5',         // Lightest cream
        noteTextColor: '#020617',
        noteBorderColor: '#73a9c2'
      }
    };
  });

  markdownContent = signal<string>('');
  sourcePath = signal<string | null>(null);
  loading = signal(true);
  error = signal<string | null>(null);

  showSystemTopology = signal(false);

  constructor() {
    effect(() => {
      const params = this.route.snapshot.params;
      const data = this.route.snapshot.data;

      const section = data['section'] || params['section'];
      const page = params['page'] || data['page'] || 'index';

      this.loadMarkdown(section, page);

      this.showSystemTopology.set(section === 'architecture' && page === 'overview');
    }, { allowSignalWrites: true });

    // Also react to route changes
    this.route.params.subscribe(() => {
      const params = this.route.snapshot.params;
      const data = this.route.snapshot.data;

      const section = data['section'] || params['section'];
      const page = params['page'] || data['page'] || 'index';

      this.loadMarkdown(section, page);
      this.showSystemTopology.set(section === 'architecture' && page === 'overview');
    });
  }

  private loadMarkdown(section: string, page: string): void {
    this.loading.set(true);
    this.error.set(null);
    this.sourcePath.set(null);

    // Try to load from assets
    const path = `assets/docs/${section}/${page}.md`;

    this.http.get(path, { responseType: 'text' })
      .pipe(
        catchError(() => {
          // If not found, try without section
          return this.http.get(`assets/docs/${page}.md`, { responseType: 'text' }).pipe(
            catchError(() => of(null))
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

            if (section === 'architecture' && page === 'overview') {
              // Strip out the System Diagram section + mermaid block
              // We'll replace it with the component
              // Regex matches "## System Diagram" until "## Layer Responsibilities"
              processedContent = processedContent.replace(/## System Diagram[\s\S]*?(?=## Layer Responsibilities)/, '');
            }
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
}
