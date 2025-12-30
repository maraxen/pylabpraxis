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
    }

    .loading {
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      min-height: 300px;
      color: rgba(255, 255, 255, 0.6);
    }

    .loading-spinner {
      width: 40px;
      height: 40px;
      border: 3px solid rgba(255, 255, 255, 0.1);
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
      color: rgba(255, 255, 255, 0.6);
    }

    .error h2 {
      color: white;
      margin-bottom: 8px;
    }

    /* Markdown Styling */
    .docs-article {
      color: rgba(255, 255, 255, 0.9);
      line-height: 1.7;
    }

    :host ::ng-deep {
      h1 {
        font-size: 2.5rem;
        font-weight: 700;
        color: white;
        margin: 0 0 16px;
        padding-bottom: 16px;
        border-bottom: 1px solid rgba(255, 255, 255, 0.1);
      }

      h2 {
        font-size: 1.75rem;
        font-weight: 600;
        color: white;
        margin: 48px 0 16px;
      }

      h3 {
        font-size: 1.25rem;
        font-weight: 600;
        color: white;
        margin: 32px 0 12px;
      }

      h4 {
        font-size: 1rem;
        font-weight: 600;
        color: white;
        margin: 24px 0 8px;
      }

      p {
        margin: 0 0 16px;
        color: rgba(255, 255, 255, 0.85);
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
        background: rgba(255, 255, 255, 0.1);
        padding: 2px 6px;
        border-radius: 4px;
        color: #f8c555;
      }

      pre {
        background: rgba(0, 0, 0, 0.4);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 12px;
        padding: 20px;
        overflow-x: auto;
        margin: 16px 0 24px;
      }

      pre code {
        background: none;
        padding: 0;
        color: rgba(255, 255, 255, 0.9);
        font-size: 0.85rem;
        line-height: 1.6;
      }

      ul, ol {
        margin: 0 0 16px;
        padding-left: 24px;
      }

      li {
        margin-bottom: 8px;
        color: rgba(255, 255, 255, 0.85);
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
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        color: white;
        font-weight: 600;
      }

      td {
        padding: 12px 16px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        color: rgba(255, 255, 255, 0.85);
      }

      tr:hover td {
        background: rgba(255, 255, 255, 0.02);
      }

      blockquote {
        margin: 16px 0;
        padding: 16px 20px;
        background: rgba(255, 255, 255, 0.05);
        border-left: 4px solid var(--primary-color);
        border-radius: 0 8px 8px 0;
      }

      blockquote p {
        margin: 0;
        color: rgba(255, 255, 255, 0.8);
      }

      hr {
        border: none;
        height: 1px;
        background: rgba(255, 255, 255, 0.1);
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
      }

      /* Mermaid diagrams */
      .mermaid {
        background: linear-gradient(145deg, rgba(255, 255, 255, 0.05) 0%, rgba(255, 255, 255, 0.01) 100%);
        border: 1px solid rgba(255, 255, 255, 0.05);
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
        primaryColor: '#f1f5f9',         // Slate 100
        primaryTextColor: '#020617',     // Slate 950
        primaryBorderColor: '#ed7a9b',

        // Secondary
        secondaryColor: '#ffffff',
        secondaryTextColor: '#020617',
        secondaryBorderColor: '#73a9c2',

        // Lines and Text
        lineColor: '#1e293b',            // Slate 800
        textColor: '#020617',
        noteBkgColor: '#f8fafc',
        noteTextColor: '#020617',
        noteBorderColor: '#73a9c2'
      }
    };
  });

  markdownContent = signal<string>('');
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
            if (section === 'architecture' && page === 'overview') {
              // Strip out the System Diagram section + mermaid block
              // We'll replace it with the component
              // Regex matches "## System Diagram" until "## Layer Responsibilities"
              processedContent = content.replace(/## System Diagram[\s\S]*?(?=## Layer Responsibilities)/, '');
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
}
