import { ApplicationConfig, provideBrowserGlobalErrorListeners, APP_INITIALIZER } from '@angular/core';
import { provideRouter, withComponentInputBinding } from '@angular/router';
import { provideAnimationsAsync } from '@angular/platform-browser/animations/async';
import { provideHttpClient, withInterceptors, HttpRequest, HttpHandlerFn } from '@angular/common/http';
import { inject } from '@angular/core';
import { routes } from './app.routes';
import { errorInterceptor } from './core/http/error.interceptor';
import { demoInterceptor } from './core/interceptors/demo.interceptor';
import { importProvidersFrom } from '@angular/core';
import { FormlyModule } from '@ngx-formly/core';
import { FormlyMaterialModule } from '@ngx-formly/material';
import { MatSnackBarModule } from '@angular/material/snack-bar';
import { AssetSelectorComponent } from './shared/formly-types/asset-selector.component';
import { RepeatTypeComponent } from './shared/formly-types/repeat-section.component';
import { ChipsTypeComponent } from './shared/formly-types/chips.component';
import { KeycloakService } from './core/auth/keycloak.service';
import { KeyboardService } from './core/services/keyboard.service';
import { environment } from '../environments/environment';
import { from, switchMap, of } from 'rxjs';

// Check if we're in demo mode
const isDemoMode = (environment as { demo?: boolean }).demo === true;

/**
 * Initialize Keycloak on app startup (skipped in demo mode)
 */
function initializeKeycloak(keycloakService: KeycloakService) {
  return () => {
    // if (isDemoMode) {
    //   console.log('[Demo Mode] Skipping Keycloak initialization (handled by KeycloakService)');
    //   // return Promise.resolve();
    // }
    return keycloakService.init({ onLoad: 'check-sso' });
  };
}

/**
 * Initialize Keyboard shortcuts and Command Palette
 */
function initializeKeyboard(keyboardService: KeyboardService) {
  return () => Promise.resolve();
}

/**
 * HTTP interceptor that adds Keycloak Bearer token to requests (skipped in demo mode)
 */
const keycloakInterceptor = (req: HttpRequest<unknown>, next: HttpHandlerFn) => {
  // Skip token in demo mode
  if (isDemoMode) {
    return next(req);
  }

  const keycloakService = inject(KeycloakService);

  // Skip token for non-API requests
  if (!req.url.includes('/api/')) {
    return next(req);
  }

  // Get token and add to request
  return from(keycloakService.getToken()).pipe(
    switchMap(token => {
      if (token) {
        const clonedReq = req.clone({
          setHeaders: {
            Authorization: `Bearer ${token}`
          }
        });
        return next(clonedReq);
      }
      return next(req);
    })
  );
};

export const appConfig: ApplicationConfig = {
  providers: [
    provideBrowserGlobalErrorListeners(),
    provideRouter(routes, withComponentInputBinding()),
    provideAnimationsAsync(),
    // Demo interceptor runs FIRST to catch API requests before they hit proxy
    provideHttpClient(withInterceptors([demoInterceptor, keycloakInterceptor, errorInterceptor])),
    {
      provide: APP_INITIALIZER,
      useFactory: initializeKeycloak,
      deps: [KeycloakService],
      multi: true
    },
    {
      provide: APP_INITIALIZER,
      useFactory: initializeKeyboard,
      deps: [KeyboardService],
      multi: true
    },
    importProvidersFrom(
      MatSnackBarModule,
      FormlyModule.forRoot({
        types: [
          { name: 'asset-selector', component: AssetSelectorComponent },
          { name: 'chips', component: ChipsTypeComponent },
          { name: 'repeat', component: RepeatTypeComponent },
        ],
        wrappers: [
          // { name: 'section', component: SectionWrapperComponent }
        ],
        validationMessages: [
          { name: 'required', message: 'This field is required' },
          { name: 'min', message: 'Value should be greater than or equal to minimum' },
          { name: 'max', message: 'Value should be less than or equal to maximum' },
          { name: 'minLength', message: 'Minimum length is required' },
          { name: 'maxLength', message: 'Maximum length exceeded' },
          { name: 'pattern', message: 'Value does not match required pattern' },
        ],
      }),
      FormlyMaterialModule
    )
  ]
};
