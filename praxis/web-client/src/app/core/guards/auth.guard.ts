
import { inject } from '@angular/core';
import { Router, CanActivateFn } from '@angular/router';
import { KeycloakService } from '../auth/keycloak.service';
import { ModeService } from '../services/mode.service';

export const authGuard: CanActivateFn = (route, state) => {
  const modeService = inject(ModeService);

  // Browser/Demo modes: allow all access without auth
  if (modeService.isBrowserMode()) {
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
