import { TestBed } from '@angular/core/testing';
import { AppStore } from './app.store';
import { vi, describe, beforeEach, it, expect, MockInstance } from 'vitest';
import { KeycloakService } from '../auth/keycloak.service';
import { signal } from '@angular/core';

describe('AppStore', () => {
  let store: InstanceType<typeof AppStore>;
  let setItemSpy: MockInstance;
  let removeItemSpy: MockInstance;
  let getItemSpy: MockInstance;
  
  const mockKeycloakService = {
    isAuthenticated: signal(false),
    user: signal<any>(null),
    token: signal<string | null>(null),
    login: vi.fn(),
    logout: vi.fn(),
    register: vi.fn(),
    init: vi.fn().mockResolvedValue(true)
  };

  beforeEach(() => {
    // robust LocalStorage mock
    const localStorageMock = (function() {
      let store: { [key: string]: string } = {};
      return {
        getItem: vi.fn((key: string) => store[key] || null),
        setItem: vi.fn((key: string, value: string) => {
          store[key] = value.toString();
        }),
        removeItem: vi.fn((key: string) => {
          delete store[key];
        }),
        clear: vi.fn(() => {
          store = {};
        })
      };
    })();

    Object.defineProperty(window, 'localStorage', {
      value: localStorageMock
    });
    
    setItemSpy = window.localStorage.setItem as unknown as MockInstance;
    removeItemSpy = window.localStorage.removeItem as unknown as MockInstance;
    getItemSpy = window.localStorage.getItem as unknown as MockInstance;


    // Mock matchMedia
    Object.defineProperty(window, 'matchMedia', {
      writable: true,
      value: vi.fn().mockImplementation((query: string) => ({
        matches: false,
        media: query,
        onchange: null,
        addListener: vi.fn(), // deprecated
        removeListener: vi.fn(), // deprecated
        addEventListener: vi.fn(),
        removeEventListener: vi.fn(),
        dispatchEvent: vi.fn(),
      })),
    });

    TestBed.configureTestingModule({
      providers: [
        AppStore,
        { provide: KeycloakService, useValue: mockKeycloakService }
      ]
    });

    store = TestBed.inject(AppStore);
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  it('should be created with initial state', () => {
    expect(store).toBeTruthy();
    expect(store.theme()).toBe('system');
    expect(store.sidebarOpen()).toBe(true);
    expect(store.isLoading()).toBe(false);
    expect(store.auth().isAuthenticated).toBe(false);
  });

  describe('Sidebar', () => {
    it('should toggle sidebar', () => {
      const initial = store.sidebarOpen();
      store.toggleSidebar();
      expect(store.sidebarOpen()).toBe(!initial);
      store.toggleSidebar();
      expect(store.sidebarOpen()).toBe(initial);
    });
  });

  describe('Theme', () => {
    it('should set theme and persist to localStorage', () => {
      store.setTheme('dark');
      expect(store.theme()).toBe('dark');
      expect(setItemSpy).toHaveBeenCalledWith('theme', 'dark');
    });

    it('should apply dark theme class to body when theme is dark', () => {
        store.setTheme('dark');
        expect(document.body.classList.contains('dark-theme')).toBe(true);
    });

     it('should remove dark theme class from body when theme is light', () => {
        // First set to dark
        store.setTheme('dark');
        expect(document.body.classList.contains('dark-theme')).toBe(true);
        
        // Then set to light
        store.setTheme('light');
        expect(document.body.classList.contains('dark-theme')).toBe(false);
    });
  });

  describe('Loading', () => {
    it('should update loading state', () => {
      store.setLoading(true);
      expect(store.isLoading()).toBe(true);
      store.setLoading(false);
      expect(store.isLoading()).toBe(false);
    });
  });

  describe('Authentication', () => {
    it('should delegate login to KeycloakService', () => {
      store.login('redirect-uri');
      expect(mockKeycloakService.login).toHaveBeenCalledWith('redirect-uri');
    });

    it('should delegate logout to KeycloakService', () => {
      store.logout('redirect-uri');
      expect(mockKeycloakService.logout).toHaveBeenCalledWith('redirect-uri');
    });

    it('should delegate register to KeycloakService', () => {
      store.register('redirect-uri');
      expect(mockKeycloakService.register).toHaveBeenCalledWith('redirect-uri');
    });

    it('should reflect KeycloakService state in auth computed signal', () => {
      const mockUser = { id: '1', username: 'test' } as any;
      mockKeycloakService.isAuthenticated.set(true);
      mockKeycloakService.user.set(mockUser);
      mockKeycloakService.token.set('test-token');

      expect(store.auth().isAuthenticated).toBe(true);
      expect(store.auth().user).toEqual(mockUser);
      expect(store.auth().token).toBe('test-token');
    });
  });
});