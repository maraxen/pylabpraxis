import { Routes } from '@angular/router';
// Import the autoLoginPartialRoutesGuard
import { autoLoginPartialRoutesGuard } from 'angular-auth-oidc-client';

export const routes: Routes = [
  {
    path: 'home',
    loadComponent: () => import('./core/pages/home/home.component').then(m => m.HomeComponent),
    title: 'Home',
    canActivate: [autoLoginPartialRoutesGuard] // Protect this route
  },
  // Example of a route that does NOT require login (e.g., a public landing page or unauthorized page)
  // {
  //   path: 'public-info',
  //   loadComponent: () => import('./features/public/public-info.component').then(m => m.PublicInfoComponent),
  //   title: 'Public Information'
  // },
  {
    path: 'unauthorized', // A route to redirect to if authorization fails (optional)
    loadComponent: () => import('./core/pages/unauthorized/unauthorized.component').then(m => m.UnauthorizedComponent),
    title: 'Unauthorized Access'
  },
  { path: '', redirectTo: '/home', pathMatch: 'full' }, // Default route redirects to home
  // Consider adding a wildcard route for 404s if all routes are not covered
  // { path: '**', redirectTo: '/home' } // Or to a PageNotFoundComponent
];
