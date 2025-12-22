import { TestBed } from '@angular/core/testing';
import { Router, RouterStateSnapshot, ActivatedRouteSnapshot } from '@angular/router';
import { authGuard } from './auth.guard';
import { AppStore } from '../store/app.store';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { signal } from '@angular/core';

describe('authGuard', () => {
  let router: Router;
  let storeMock: any;

  beforeEach(() => {
    storeMock = {
      auth: {
        isAuthenticated: vi.fn()
      }
    };

    const routerMock = {
      createUrlTree: vi.fn()
    };

    TestBed.configureTestingModule({
      providers: [
        { provide: AppStore, useValue: storeMock },
        { provide: Router, useValue: routerMock }
      ]
    });

    router = TestBed.inject(Router);
  });

  const executeGuard = (url: string) => {
    const route = {} as ActivatedRouteSnapshot;
    const state = { url } as RouterStateSnapshot;
    return TestBed.runInInjectionContext(() => authGuard(route, state));
  };

  it('should allow access if user is authenticated', () => {
    storeMock.auth.isAuthenticated.mockReturnValue(true);
    const result = executeGuard('/protected');
    expect(result).toBe(true);
  });

  it('should redirect to login with returnUrl if user is not authenticated', () => {
    storeMock.auth.isAuthenticated.mockReturnValue(false);
    const mockUrlTree = {} as any;
    vi.spyOn(router, 'createUrlTree').mockReturnValue(mockUrlTree);

    const result = executeGuard('/protected');

    expect(router.createUrlTree).toHaveBeenCalledWith(
      ['/login'],
      { queryParams: { returnUrl: '/protected' } }
    );
    expect(result).toBe(mockUrlTree);
  });
});