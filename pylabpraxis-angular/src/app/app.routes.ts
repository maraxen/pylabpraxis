import { inject } from '@angular/core';
import { Routes, Router, UrlTree, CanActivateFn } from '@angular/router';
import { Observable } from 'rxjs';
import { map, switchMap, filter, take } from 'rxjs/operators';
import { AuthService } from './core/auth/auth.service'; // Adjust path if necessary

/**
 * Authentication Guard (CanActivateFn)
 *
 * This guard protects routes by:
 * 1. Waiting for the OIDC client setup to be complete (via `authService.isOidcSetupDone$`).
 * 2. Checking if the user is authenticated (via `authService.isAuthenticated$`).
 *
 * If OIDC setup is not complete, it waits.
 * If the user is authenticated after setup, it allows access to the route.
 * If the user is NOT authenticated after setup, it creates a UrlTree to redirect
 * to the application's root path ('/'). The `AuthService` (using `oidc-spa`
 * with `autoLogin: true` and `homeUrl: '/'`) is expected to initiate the
 * login flow with the identity provider (Keycloak) when the root path is accessed
 * by an unauthenticated user.
 */
export const authGuard: CanActivateFn = (route, state): Observable<boolean | UrlTree> | Promise<boolean | UrlTree> | boolean | UrlTree => {
  const authService = inject(AuthService);
  const router = inject(Router);

  // Wait for OIDC setup to be fully completed.
  return authService.isOidcSetupDone$.pipe(
    filter(isDone => isDone), // Only proceed when isDone is true.
    take(1), // Take the first true emission to avoid re-processing on subsequent emissions.
    switchMap(() => {
      // OIDC setup is complete, now check the current authentication status.
      return authService.isAuthenticated$.pipe(
        take(1), // Get the current definitive authentication state.
        map(isAuthenticated => {
          if (isAuthenticated) {
            console.log('[AuthGuard] Access GRANTED. User is authenticated.');
            return true; // User is authenticated, allow access to the route.
          } else {
            // User is not authenticated.
            // Redirect to the root path ('/').
            // The AuthService (oidc-spa with autoLogin:true at homeUrl:'/')
            // should then handle the redirection to the identity provider (Keycloak).
            console.log('[AuthGuard] Access DENIED. User not authenticated. Redirecting to / to initiate auth flow.');
            return router.createUrlTree(['/']);
          }
        })
      );
    })
  );
};

// Define the application routes
export const routes: Routes = [
  {
    path: 'home',
    loadComponent: () => import('./core/pages/home/home.component').then(m => m.HomeComponent),
    title: 'Home - PylabPraxis',
    canActivate: [authGuard] // Protect the home route
  },
  // The '/auth-callback' route is generally not needed with oidc-spa when autoLogin is true
  // and homeUrl is configured, as oidc-spa handles the callback at homeUrl.
  // It will parse OIDC parameters from the URL at homeUrl and then redirect to postLoginRedirectUrl.
  {
    path: 'protocols',
    loadChildren: () => import('./features/manage-protocols/manage-protocols.routes').then(m => m.MANAGE_PROTOCOLS_ROUTES),
    canActivate: [authGuard] // Protect the protocols feature module
  },
  {
    path: 'lab-assets',
    loadComponent: () => import('./features/manage-assets/manage-assets.component').then(m => m.ManageAssetsComponent),
    title: 'Lab Assets - PylabPraxis',
    canActivate: [authGuard] // Protect the lab assets route
  },
  {
    path: 'settings',
    loadComponent: () => import('./features/settings-overview/settings-overview.component').then(m => m.SettingsOverviewComponent),
    title: 'Settings - PylabPraxis',
    canActivate: [authGuard] // Protect the settings route
  },
  {
    path: 'unauthorized', // Page for users who are logged in but lack permissions for a resource
    loadComponent: () => import('./core/pages/unauthorized/unauthorized.component').then(m => m.UnauthorizedComponent),
    title: 'Unauthorized - PylabPraxis'
    // This route should typically be accessible without the authGuard,
    // as it's a destination for already authenticated users who lack specific roles/permissions.
  },
  {
    path: '', // Root path
    redirectTo: '/home', // Redirect to '/home'
    pathMatch: 'full'
    // When an unauthenticated user hits '/', they are redirected to '/home'.
    // The authGuard on '/home' will then redirect them back to '/' if not authenticated.
    // At '/', oidc-spa (with autoLogin:true and homeUrl:'/') will initiate login with Keycloak.
    // After successful login, Keycloak redirects to '/', oidc-spa processes tokens,
    // and then redirects to postLoginRedirectUrl ('/home').
  },
  {
    path: '**', // Wildcard route for Page Not Found
    loadComponent: () => import('./core/pages/page-not-found/page-not-found.component').then(m => m.PageNotFoundComponent),
    title: 'Page Not Found - PylabPraxis'
  }
];
