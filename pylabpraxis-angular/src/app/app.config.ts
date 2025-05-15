import { ApplicationConfig, inject } from '@angular/core';
import { provideRouter } from '@angular/router';
import { provideAnimations } from '@angular/platform-browser/animations';
import { provideHttpClient, withInterceptorsFromDi } from '@angular/common/http';
import { routes } from './app.routes';

// OIDC Client and RxJS operators
import { LogLevel, OidcSecurityService, LoginResponse, provideAuth, UserDataResult } from 'angular-auth-oidc-client'; // Added UserDataResult
import { switchMap, take, tap } from 'rxjs/operators';
import { of, firstValueFrom } from 'rxjs'; // Corrected: firstValueFrom is a top-level import from 'rxjs'

// New provideAppInitializer function
import { provideAppInitializer } from '@angular/core';

// Initializer function that will be passed to provideAppInitializer
// This function itself is the initializer.
const initializeAuthFunction = () => { // Renamed and restructured
  const oidcSecurityService = inject(OidcSecurityService);

  return firstValueFrom(
    oidcSecurityService.checkAuth()
      .pipe(
        take(1),
        tap((loginResponse: LoginResponse) => {
          console.log('APP_INITIALIZER (via provideAppInitializer): checkAuth() response. IsAuthenticated:', loginResponse.isAuthenticated);
        }),
        switchMap((loginResponse: LoginResponse) => {
          if (loginResponse.isAuthenticated) {
            return oidcSecurityService.userData$.pipe(
              take(1),
              // Correctly access preferred_username from result.userData
              tap((userDataResult: UserDataResult) => console.log('APP_INITIALIZER (via provideAppInitializer): UserData loaded:', userDataResult.userData ? userDataResult.userData.preferred_username : 'no user data'))
            );
          }
          return of(null);
        })
      )
  ).catch((error: any) => { // Added type for error
    console.error('APP_INITIALIZER (via provideAppInitializer): Error during auth initialization:', error);
    return Promise.resolve(); // Allow app to continue
  });
};

export const appConfig: ApplicationConfig = {
  providers: [
    provideRouter(routes),
    provideAnimations(),
    provideHttpClient(withInterceptorsFromDi()),

    // Use provideAuth for OIDC configuration
    provideAuth({ // Replace importProvidersFrom(AuthModule.forRoot(...))
      config: {
        authority: 'http://localhost:8080/realms/praxis-realm',
        redirectUrl: "http://localhost:4200/auth-callback",// window.location.origin + '/auth-callback',
        postLoginRoute: '/home', // Optional: Route to navigate to after login and callback processing
        clientId: 'praxis-client', // *** REPLACE WITH YOUR ACTUAL CLIENT ID ***
        scope: 'openid profile email offline_access',
        responseType: 'code',
        silentRenew: true,
        useRefreshToken: true,
        logLevel: LogLevel.Debug,
        historyCleanupOff: false,
        triggerAuthorizationResultEvent: true,
        postLogoutRedirectUri: window.location.origin,
        // Ensure this is false if using autoLoginPartialRoutesGuard
        // autoLoginAllRoutes: false, (default is false)
      },
    }),

    provideAppInitializer(initializeAuthFunction),
  ],
};
