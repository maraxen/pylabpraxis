import { TestBed } from '@angular/core/testing';
import { Router, RouterStateSnapshot, ActivatedRouteSnapshot } from '@angular/router';
import { authGuard } from './auth.guard';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { KeycloakService } from '../auth/keycloak.service';
import { signal } from '@angular/core';

describe('authGuard', () => {
  let keycloakServiceMock: any;

  beforeEach(() => {
    keycloakServiceMock = {
      isAuthenticated: signal(false),
      login: vi.fn().mockResolvedValue(undefined)
    };

    TestBed.configureTestingModule({
      providers: [
        { provide: KeycloakService, useValue: keycloakServiceMock },
        { provide: Router, useValue: { navigate: vi.fn() } }
      ]
    });
  });

  const executeGuard = (url: string) => {
    const route = {} as ActivatedRouteSnapshot;
    const state = { url } as RouterStateSnapshot;
    return TestBed.runInInjectionContext(() => authGuard(route, state));
  };

  it('should allow access if user is authenticated', () => {
    keycloakServiceMock.isAuthenticated.set(true);
    const result = executeGuard('/protected');
    expect(result).toBe(true);
  });

  it('should redirect to Keycloak if user is not authenticated', () => {
    keycloakServiceMock.isAuthenticated.set(false);
    
    const result = executeGuard('/protected');

    expect(keycloakServiceMock.login).toHaveBeenCalled();
    expect(result).toBe(false);
  });
});