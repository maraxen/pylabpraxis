import { Routes } from '@angular/router';
import { autoLoginPartialRoutesGuard } from 'angular-auth-oidc-client';

export const routes: Routes = [
  {
    path: 'home',
    loadComponent: () => import('./core/pages/home/home.component').then(m => m.HomeComponent),
    title: 'Home - PylabPraxis',
    canActivate: [autoLoginPartialRoutesGuard]
  },
  {
    path: 'auth-callback',
    loadComponent: () => import('./core/pages/auth-callback/auth-callback.component').then(m => m.AuthCallbackComponent),
    title: 'Authenticating...'
  },
  {
    path: 'protocols', // Main path for the protocols feature
    // Load the children routes from the manage-protocols.routes.ts file
    loadChildren: () => import('./features/manage-protocols/manage-protocols.routes').then(m => m.MANAGE_PROTOCOLS_ROUTES),
    // No component here as children define the actual components
    // canActivate: [autoLoginPartialRoutesGuard] // Guard can be on parent or individual children
  },
  {
    path: 'lab-assets',
    loadComponent: () => import('./features/manage-assets/manage-assets.component').then(m => m.ManageAssetsComponent),
    title: 'Lab Assets - PylabPraxis',
    canActivate: [autoLoginPartialRoutesGuard]
  },
  {
    path: 'settings',
    loadComponent: () => import('./features/settings-overview/settings-overview.component').then(m => m.SettingsOverviewComponent),
    title: 'Settings - PylabPraxis',
    canActivate: [autoLoginPartialRoutesGuard]
  },
  {
    path: 'unauthorized',
    loadComponent: () => import('./core/pages/unauthorized/unauthorized.component').then(m => m.UnauthorizedComponent),
    title: 'Unauthorized - PylabPraxis'
  },
  { path: '', redirectTo: '/home', pathMatch: 'full' },
  {
    path: '**',
    loadComponent: () => import('./core/pages/page-not-found/page-not-found.component').then(m => m.PageNotFoundComponent),
    title: 'Page Not Found - PylabPraxis'
  }
];
