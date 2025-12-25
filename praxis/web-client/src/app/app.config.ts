import { ApplicationConfig, provideBrowserGlobalErrorListeners, APP_INITIALIZER } from '@angular/core';
import { provideRouter, withComponentInputBinding } from '@angular/router';
import { provideAnimationsAsync } from '@angular/platform-browser/animations/async';
import { provideHttpClient, withInterceptors, HttpRequest, HttpHandlerFn } from '@angular/common/http';
import { inject } from '@angular/core';
import { routes } from './app.routes';
import { errorInterceptor } from './core/http/error.interceptor';
import { importProvidersFrom } from '@angular/core';
import { FormlyModule } from '@ngx-formly/core';
import { FormlyMaterialModule } from '@ngx-formly/material';
import { MatSnackBarModule } from '@angular/material/snack-bar';
import { AssetSelectorComponent } from './shared/formly-types/asset-selector.component';
import { RepeatTypeComponent } from './shared/formly-types/repeat-section.component';
import { ChipsTypeComponent } from './shared/formly-types/chips.component';
import { KeycloakService } from './core/auth/keycloak.service';
import { KeyboardService } from './core/services/keyboard.service';
import { from, switchMap } from 'rxjs';

/**
 * Initialize Keycloak on app startup
 */
function initializeKeycloak(keycloakService: KeycloakService) {
  return () => keycloakService.init({ onLoad: 'check-sso' });
}

/**
 * Initialize Keyboard shortcuts and Command Palette
 */
function initializeKeyboard(keyboardService: KeyboardService) {
  return () => Promise.resolve();
}

/**
 * HTTP interceptor that adds Keycloak Bearer token to requests
 */
const keycloakInterceptor = (req: HttpRequest<unknown>, next: HttpHandlerFn) => {
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
    provideHttpClient(withInterceptors([keycloakInterceptor, errorInterceptor])),
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
