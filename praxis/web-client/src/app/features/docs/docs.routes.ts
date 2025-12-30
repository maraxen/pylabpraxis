import { Routes } from '@angular/router';

export const DOCS_ROUTES: Routes = [
  {
    path: '',
    loadComponent: () => import('./docs-layout.component').then(m => m.DocsLayoutComponent),
    children: [
      { path: '', redirectTo: 'getting-started', pathMatch: 'full' },
      {
        path: 'getting-started',
        loadComponent: () => import('./components/docs-page.component').then(m => m.DocsPageComponent),
        data: { section: 'getting-started', page: 'installation' }
      },
      {
        path: 'getting-started/:page',
        loadComponent: () => import('./components/docs-page.component').then(m => m.DocsPageComponent),
        data: { section: 'getting-started' }
      },
      {
        path: 'architecture',
        loadComponent: () => import('./components/docs-page.component').then(m => m.DocsPageComponent),
        data: { section: 'architecture', page: 'overview' }
      },
      {
        path: 'architecture/:page',
        loadComponent: () => import('./components/docs-page.component').then(m => m.DocsPageComponent),
        data: { section: 'architecture' }
      },
      {
        path: 'user-guide',
        loadComponent: () => import('./components/docs-page.component').then(m => m.DocsPageComponent),
        data: { section: 'user-guide', page: 'protocols' }
      },
      {
        path: 'user-guide/:page',
        loadComponent: () => import('./components/docs-page.component').then(m => m.DocsPageComponent),
        data: { section: 'user-guide' }
      },
      {
        path: 'api',
        loadComponent: () => import('./components/docs-page.component').then(m => m.DocsPageComponent),
        data: { section: 'api', page: 'rest-api' }
      },
      {
        path: 'api/:page',
        loadComponent: () => import('./components/docs-page.component').then(m => m.DocsPageComponent),
        data: { section: 'api' }
      },
      {
        path: 'development',
        loadComponent: () => import('./components/docs-page.component').then(m => m.DocsPageComponent),
        data: { section: 'development', page: 'contributing' }
      },
      {
        path: 'development/:page',
        loadComponent: () => import('./components/docs-page.component').then(m => m.DocsPageComponent),
        data: { section: 'development' }
      },
      {
        path: 'reference',
        loadComponent: () => import('./components/docs-page.component').then(m => m.DocsPageComponent),
        data: { section: 'reference', page: 'configuration' }
      },
      {
        path: 'reference/:page',
        loadComponent: () => import('./components/docs-page.component').then(m => m.DocsPageComponent),
        data: { section: 'reference' }
      }
    ]
  }
];
