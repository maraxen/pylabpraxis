import { Routes } from '@angular/router';
import { authGuard } from './core/guards/auth.guard';
import { MainLayoutComponent } from './layout/main-layout.component';
import { UnifiedShellComponent } from './layout/unified-shell.component';
import { LoginComponent } from './features/auth/login.component';
import { RegisterComponent } from './features/auth/register.component';
import { ForgotPasswordComponent } from './features/auth/forgot-password.component';
import { SplashComponent } from './features/splash/splash.component';

export const routes: Routes = [
  // Public splash page (no auth required)
  {
    path: '',
    component: SplashComponent,
    pathMatch: 'full'
  },
  // Auth pages (no auth required)
  {
    path: 'login',
    component: LoginComponent
  },
  {
    path: 'register',
    component: RegisterComponent
  },
  {
    path: 'forgot-password',
    component: ForgotPasswordComponent
  },

  // Unified Shell Routes (App + Docs)
  {
    path: '',
    component: UnifiedShellComponent,
    children: [
      // Praxis App
      {
        path: 'app',
        canActivate: [authGuard],
        children: [
          { path: '', redirectTo: 'home', pathMatch: 'full' },
          {
            path: 'home',
            loadComponent: () => import('./features/home/home.component').then(m => m.HomeComponent)
          },
          {
            path: 'assets',
            loadChildren: () => import('./features/assets/asset.routes').then(m => m.ASSET_ROUTES)
          },
          {
            path: 'protocols',
            loadChildren: () => import('./features/protocols/protocol.routes').then(m => m.PROTOCOL_ROUTES)
          },
          {
            path: 'run',
            loadChildren: () => import('./features/run-protocol/run-protocol.routes').then(m => m.RUN_PROTOCOL_ROUTES)
          },
          {
            path: 'monitor',
            children: [
              {
                path: '',
                loadComponent: () => import('./features/execution-monitor/execution-monitor.component').then(m => m.ExecutionMonitorComponent)
              },
              {
                path: ':id',
                loadComponent: () => import('./features/execution-monitor/components/run-detail.component').then(m => m.RunDetailComponent)
              }
            ]
          },
          {
            path: 'visualizer',
            loadChildren: () => import('./features/visualizer/visualizer.routes').then(m => m.VISUALIZER_ROUTES)
          },
          {
            path: 'data',
            loadChildren: () => import('./features/data/data.routes').then(m => m.DATA_ROUTES)
          },
          {
            path: 'settings',
            loadChildren: () => import('./features/settings/settings.routes').then(m => m.SETTINGS_ROUTES)
          },
          {
            path: 'stress-test',
            loadComponent: () => import('./features/stress-test/stress-test.component').then(m => m.StressTestComponent)
          },
          {
            path: 'repl',
            loadComponent: () => import('./features/repl/jupyterlite-repl.component').then(m => m.JupyterliteReplComponent)
          },
        ]
      },

      // Documentation
      {
        path: 'docs',
        loadChildren: () => import('./features/docs/docs.routes').then(m => m.DOCS_ROUTES)
      }
    ]
  },

  // Legacy/Compatibility Redirects
  { path: 'home', redirectTo: 'app/home' },
  { path: 'assets', redirectTo: 'app/assets' },
  { path: 'protocols', redirectTo: 'app/protocols' },
  { path: 'run', redirectTo: 'app/run' },
  { path: 'visualizer', redirectTo: 'app/visualizer' },
  { path: 'data', redirectTo: 'app/data' },
  { path: 'settings', redirectTo: 'app/settings' },
  { path: 'stress-test', redirectTo: 'app/stress-test' },

  // Fallback
  { path: '**', redirectTo: '' }
];