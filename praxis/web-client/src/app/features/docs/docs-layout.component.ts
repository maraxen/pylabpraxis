import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterOutlet, RouterLink, RouterLinkActive } from '@angular/router';
import { MatIconModule } from '@angular/material/icon';

interface DocSection {
  title: string;
  basePath: string;
  pages: { title: string; slug: string; icon?: string }[];
}

@Component({
  selector: 'app-docs-layout',
  standalone: true,
  imports: [CommonModule, RouterOutlet, RouterLink, RouterLinkActive, MatIconModule],
  template: `
    <div class="docs-layout">
      <!-- Docs Sidebar -->
      <aside class="docs-sidebar">
        <div class="docs-sidebar-content">
          @for (section of docSections; track section.basePath) {
            <div class="docs-nav-section">
              <h3 class="section-title">{{ section.title }}</h3>
              <ul class="section-pages">
                @for (page of section.pages; track page.slug) {
                  <li>
                    <a
                      class="page-link"
                      [routerLink]="['/docs', section.basePath, page.slug]"
                      routerLinkActive="active">
                      @if (page.icon) {
                        <mat-icon>{{ page.icon }}</mat-icon>
                      }
                      <span>{{ page.title }}</span>
                    </a>
                  </li>
                }
              </ul>
            </div>
          }
        </div>
      </aside>

      <!-- Docs Content -->
      <main class="docs-content">
        <router-outlet></router-outlet>
      </main>
    </div>
  `,
  styles: [`
    .docs-layout {
      display: flex;
      height: 100%;
      min-height: 0;
    }

    /* Docs Sidebar */
    .docs-sidebar {
      width: 280px;
      min-width: 280px;
      /* background: rgba(255, 255, 255, 0.02); */
      background: transparent;
      border-right: 1px solid var(--theme-border);
      overflow-y: auto;
    }

    .docs-sidebar-content {
      padding: 24px 16px;
    }

    .docs-nav-section {
      margin-bottom: 24px;
    }

    .section-title {
      font-size: 0.75rem;
      font-weight: 600;
      text-transform: uppercase;
      letter-spacing: 0.05em;
      color: var(--theme-text-tertiary);
      margin: 0 0 12px 8px;
    }

    .section-pages {
      list-style: none;
      margin: 0;
      padding: 0;
    }

    .page-link {
      display: flex;
      align-items: center;
      gap: 10px;
      padding: 10px 12px;
      margin: 2px 0;
      border-radius: 8px;
      color: var(--theme-text-secondary);
      text-decoration: none;
      font-size: 0.9rem;
      transition: all 0.2s ease;
    }

    .page-link mat-icon {
      font-size: 18px;
      width: 18px;
      height: 18px;
      opacity: 0.7;
    }

    .page-link:hover {
      background: var(--theme-surface-elevated);
      color: var(--theme-text-primary);
    }

    .page-link.active {
      background: var(--aurora-primary);
      color: var(--theme-text-primary);
    }

    .page-link.active mat-icon {
      color: var(--primary-color);
    }

    /* Docs Content */
    .docs-content {
      flex: 1;
      overflow-y: auto;
      min-width: 0;
    }

    /* Responsive */
    @media (max-width: 1024px) {
      .docs-sidebar {
        width: 240px;
        min-width: 240px;
      }
    }

    @media (max-width: 768px) {
      .docs-layout {
        flex-direction: column;
      }

      .docs-sidebar {
        width: 100%;
        min-width: 100%;
        max-height: 200px;
        border-right: none;
        border-bottom: 1px solid var(--theme-border);
      }

      .docs-sidebar-content {
        display: flex;
        flex-wrap: wrap;
        gap: 16px;
        padding: 16px;
      }

      .docs-nav-section {
        margin-bottom: 0;
      }
    }
  `]
})
export class DocsLayoutComponent {
  docSections: DocSection[] = [
    {
      title: 'Getting Started',
      basePath: 'getting-started',
      pages: [
        { title: 'Installation', slug: 'installation', icon: 'download' },
        { title: 'Quick Start', slug: 'quickstart', icon: 'rocket_launch' },
        { title: 'Demo Mode', slug: 'demo-mode', icon: 'play_circle' }
      ]
    },
    {
      title: 'Architecture',
      basePath: 'architecture',
      pages: [
        { title: 'Overview', slug: 'overview', icon: 'architecture' },
        { title: 'Backend', slug: 'backend', icon: 'dns' },
        { title: 'Frontend', slug: 'frontend', icon: 'web' },
        { title: 'State Management', slug: 'state-management', icon: 'memory' },
        { title: 'Execution Flow', slug: 'execution-flow', icon: 'swap_calls' }
      ]
    },
    {
      title: 'User Guide',
      basePath: 'user-guide',
      pages: [
        { title: 'Protocols', slug: 'protocols', icon: 'science' },
        { title: 'Assets', slug: 'assets', icon: 'inventory_2' },
        { title: 'Hardware Discovery', slug: 'hardware-discovery', icon: 'usb' },
        { title: 'Data Visualization', slug: 'data-visualization', icon: 'bar_chart' }
      ]
    },
    {
      title: 'API Reference',
      basePath: 'api',
      pages: [
        { title: 'REST API', slug: 'rest-api', icon: 'api' },
        { title: 'WebSocket API', slug: 'websocket-api', icon: 'sync_alt' },
        { title: 'Services', slug: 'services', icon: 'hub' }
      ]
    },
    {
      title: 'Development',
      basePath: 'development',
      pages: [
        { title: 'Contributing', slug: 'contributing', icon: 'group' },
        { title: 'Testing', slug: 'testing', icon: 'bug_report' },
        { title: 'Code Style', slug: 'code-style', icon: 'code' }
      ]
    },
    {
      title: 'Reference',
      basePath: 'reference',
      pages: [
        { title: 'Configuration', slug: 'configuration', icon: 'settings' },
        { title: 'CLI Commands', slug: 'cli-commands', icon: 'terminal' },
        { title: 'Troubleshooting', slug: 'troubleshooting', icon: 'help' }
      ]
    }
  ];
}
