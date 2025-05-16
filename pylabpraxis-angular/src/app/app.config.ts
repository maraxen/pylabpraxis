import { ApplicationConfig, inject } from '@angular/core'; // Added inject
import { provideRouter } from '@angular/router';
import { provideAnimations } from '@angular/platform-browser/animations';
import { provideHttpClient, withInterceptorsFromDi } from '@angular/common/http';
import { routes } from './app.routes';

// Import our AuthService
import { AuthService } from './core/auth/auth.service'; // Assuming this is the correct path

// New provideAppInitializer function
import { provideAppInitializer } from '@angular/core';

// This function IS the initializer that provideAppInitializer expects.
// It uses inject() to get AuthService and calls its async init method.
const initializeAuthFunction = (): Promise<void> => {
  const authService = inject(AuthService);
  return authService.initializeOidc(); // Directly return the Promise from initializeOidc
};

export const appConfig: ApplicationConfig = {
  providers: [
    provideRouter(routes),
    provideAnimations(),
    provideHttpClient(withInterceptorsFromDi()),

    // AuthService is already providedIn: 'root', so no need to provide it here again.

    // Pass the initializer function directly to provideAppInitializer
    provideAppInitializer(initializeAuthFunction),
    // Note: No need to provide APP_INITIALIZER here, as provideAppInitializer handles it.
  ],
};
