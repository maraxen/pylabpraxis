
import { patchState, signalStore, withMethods, withState, withComputed, withHooks } from '@ngrx/signals';
import { computed, inject } from '@angular/core';
import { OverlayContainer } from '@angular/cdk/overlay';
import { KeycloakService } from '../auth/keycloak.service';

type Theme = 'light' | 'dark' | 'system';

type AppState = {
  theme: Theme;
  sidebarOpen: boolean;
  isLoading: boolean;
  simulationMode: boolean;  // Global simulation mode for protocol execution
  maintenanceEnabled: boolean; // Global maintenance feature toggle
  infiniteConsumables: boolean; // Auto-replenish consumables in simulation
};

const getSavedTheme = (): Theme => {
  try {
    return (localStorage.getItem('theme') as Theme) || 'system';
  } catch {
    return 'system';
  }
};

const getSavedSimulationMode = (): boolean => {
  try {
    const saved = localStorage.getItem('simulationMode');
    return saved === null ? true : saved === 'true';  // Default ON
  } catch {
    return true;
  }
};

const getSavedMaintenanceEnabled = (): boolean => {
  try {
    const saved = localStorage.getItem('maintenanceEnabled');
    return saved === null ? true : saved === 'true'; // Default ON
  } catch {
    return true;
  }
};

const getSavedInfiniteConsumables = (): boolean => {
  try {
    const saved = localStorage.getItem('infiniteConsumables');
    return saved === null ? true : saved === 'true'; // Default ON (especially for browser mode)
  } catch {
    return true;
  }
};

const initialState: AppState = {
  theme: getSavedTheme(),
  sidebarOpen: true,
  isLoading: false,
  simulationMode: getSavedSimulationMode(),
  maintenanceEnabled: getSavedMaintenanceEnabled(),
  infiniteConsumables: getSavedInfiniteConsumables(),
};

export const AppStore = signalStore(
  { providedIn: 'root' },
  withState(initialState),
  withComputed(() => {
    const keycloakService = inject(KeycloakService);

    return {
      // Auth state is now derived from KeycloakService
      auth: computed(() => ({
        user: keycloakService.user(),
        isAuthenticated: keycloakService.isAuthenticated(),
        token: keycloakService.token()
      }))
    };
  }),
  withMethods((store) => {
    const keycloakService = inject(KeycloakService);
    const overlayContainer = inject(OverlayContainer);

    return {
      toggleSidebar() {
        patchState(store, { sidebarOpen: !store.sidebarOpen() });
      },
      setTheme(theme: Theme) {
        patchState(store, { theme });
        try {
          localStorage.setItem('theme', theme);
          // Apply theme immediately
          const applyThemeClass = (t: Theme) => {
            const containerElement = overlayContainer.getContainerElement();
            const rootElements = [document.body, document.documentElement, containerElement];

            rootElements.forEach(el => el.classList.remove('light-theme', 'dark-theme'));

            if (t === 'system') {
              const systemDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
              const effectiveTheme = systemDark ? 'dark-theme' : 'light-theme';
              rootElements.forEach(el => el.classList.add(effectiveTheme));
            } else {
              const themeClass = `${t}-theme`;
              rootElements.forEach(el => el.classList.add(themeClass));
            }
          };

          applyThemeClass(theme);

          // Handle system preference changes
          const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
          const listener = () => {
            if (store.theme() === 'system') {
              applyThemeClass('system');
            }
          };

          mediaQuery.removeEventListener('change', listener);
          if (theme === 'system') {
            mediaQuery.addEventListener('change', listener);
          }
        } catch (e) {
          console.error('Failed to save theme preference', e);
        }
      },
      setLoading(isLoading: boolean) {
        patchState(store, { isLoading });
      },
      toggleSimulationMode() {
        const newMode = !store.simulationMode();
        patchState(store, { simulationMode: newMode });
        try {
          localStorage.setItem('simulationMode', String(newMode));
        } catch (e) {
          console.error('Failed to save simulation mode preference', e);
        }
      },
      setSimulationMode(simulationMode: boolean) {
        patchState(store, { simulationMode });
        try {
          localStorage.setItem('simulationMode', String(simulationMode));
        } catch (e) {
          console.error('Failed to save simulation mode preference', e);
        }
      },
      setMaintenanceEnabled(enabled: boolean) {
        patchState(store, { maintenanceEnabled: enabled });
        try {
          localStorage.setItem('maintenanceEnabled', String(enabled));
        } catch (e) {
          console.error('Failed to save maintenance enabled preference', e);
        }
      },
      setInfiniteConsumables(enabled: boolean) {
        patchState(store, { infiniteConsumables: enabled });
        try {
          localStorage.setItem('infiniteConsumables', String(enabled));
        } catch (e) {
          console.error('Failed to save infinite consumables preference', e);
        }
      },
      // Login now delegates to Keycloak
      login(redirectUri?: string) {
        return keycloakService.login(redirectUri);
      },
      // Logout now delegates to Keycloak
      logout(redirectUri?: string) {
        return keycloakService.logout(redirectUri);
      },
      // Register via Keycloak
      register(redirectUri?: string) {
        return keycloakService.register(redirectUri);
      }
    };
  }),
  withMethods((store) => ({
    initTheme() {
      store.setTheme(store.theme());
    }
  })),
  withHooks({
    onInit({ initTheme }) {
      initTheme();
    }
  })
);
