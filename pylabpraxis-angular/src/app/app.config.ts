import { ApplicationConfig, importProvidersFrom, provideAppInitializer } from '@angular/core';
import { provideRouter } from '@angular/router';
import { provideAnimations } from '@angular/platform-browser/animations';
import { provideHttpClient, withInterceptorsFromDi } from '@angular/common/http';
import { routes } from './app.routes';

// OIDC Client and RxJS operators

import { provideAuth, LogLevel, OidcSecurityService, LoginResponse } from 'angular-auth-oidc-client';
import { switchMap, take, tap } from 'rxjs/operators';
import { of } from 'rxjs';

export function initializeAuth(oidcSecurityService: OidcSecurityService): () => Promise<any> {
  return () =>
    oidcSecurityService.checkAuth() // checkAuth() processes the auth result after redirect
      .pipe(
        take(1), // Ensure the observable completes after the first emission
        tap((loginResponse: LoginResponse) => {
          console.log('provideAppInitializer: checkAuth() response. IsAuthenticated:', loginResponse.isAuthenticated);
          // If authenticated, userData will be available via oidcSecurityService.userData$
        }),
        // Optional: If you need to ensure userData is loaded before app proceeds after login
        switchMap((loginResponse: LoginResponse) => {
          if (loginResponse.isAuthenticated) {
            return oidcSecurityService.userData$.pipe(
              take(1), // Take the first emission of userData
              tap(userData => console.log('provideAppInitializer: UserData loaded:', userData ? userData.preferred_username : 'no user data'))
            );
          }
          return of(null); // If not authenticated, or no further action needed, just complete
        })
      )
      .lastValueFrom() // APP_INITIALIZER expects a Promise
      .catch(error => {
        console.error('provideAppInitializer: Error during auth initialization:', error);
        // Allow app to continue even if auth init fails, guards will handle access
        return Promise.resolve();
      });
}


export const appConfig: ApplicationConfig = {
  providers: [
    provideRouter(routes), // Provide the router configuration
    provideAnimations(), // Enable animations
    provideHttpClient(withInterceptorsFromDi()), // Provide HttpClient with interceptor support

    // Import providers from AuthModule.forRoot()
    // IMPORTANT: Replace the authority, redirectUrl, postLogoutRedirectUri, and clientId
    // with your actual Keycloak configuration.
    provideAuth({
      config: {
        // URL of the Identity Provider (Keycloak)
        authority: 'http://localhost:8080/realms/praxis-realm',

        // URL of the SPA to redirect to after login
        redirectUrl: window.location.origin + '/home',

        // URL of the SPA to redirect to after logout
        postLogoutRedirectUri: window.location.origin,

        // The Client ID of your SPA application in Keycloak
        clientId: 'praxis-client',

        // Scopes being requested from the Identity Provider
        scope: 'openid profile email offline_access',

        // Type of response expected from the OIDC provider
        responseType: 'code', // PKCE flow

        // Enables silent token refresh
        silentRenew: true,
        useRefreshToken: true,

        logLevel: LogLevel.Debug, // Change to LogLevel.Warn or LogLevel.Error for production

        // Ensure history cleanup is enabled
        historyCleanupOff: false,

        triggerAuthorizationResultEvent: true, // Trigger events for authorization result
      },
    }),

    // Add APP_INITIALIZER to handle auth check before app starts
    {
      provide: APP_INITIALIZER,
      useFactory: initializeAuth,
      deps: [OidcSecurityService], // Dependencies for the factory function
      multi: true,
    },
  ],
};
