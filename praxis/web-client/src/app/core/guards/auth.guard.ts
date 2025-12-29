
import { inject } from '@angular/core';
import { Router, CanActivateFn } from '@angular/router';
import { KeycloakService } from '../auth/keycloak.service';
import { environment } from '../../../environments/environment';

// Check if we're in demo mode
const isDemoMode = (environment as { demo?: boolean }).demo === true;

export const authGuard: CanActivateFn = (route, state) => {
  // Demo mode: allow all access without auth
  if (isDemoMode) {
    return true;
  }

  const keycloakService = inject(KeycloakService);
  const router = inject(Router);

  if (keycloakService.isAuthenticated()) {
    return true;
  }

  // Redirect to Keycloak login
  keycloakService.login(window.location.origin + state.url);
  return false;
};
