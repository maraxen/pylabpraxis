
import { patchState, signalStore, withMethods, withState, withComputed } from '@ngrx/signals';
import { computed, inject } from '@angular/core';
import { KeycloakService } from '../auth/keycloak.service';

type Theme = 'light' | 'dark' | 'system';

type AppState = {
  theme: Theme;
  sidebarOpen: boolean;
  isLoading: boolean;
  simulationMode: boolean;  // Global simulation mode for protocol execution
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

const initialState: AppState = {
  theme: getSavedTheme(),
  sidebarOpen: true,
  isLoading: false,
  simulationMode: getSavedSimulationMode(),
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

    return {
      toggleSidebar() {
        patchState(store, { sidebarOpen: !store.sidebarOpen() });
      },
      setTheme(theme: Theme) {
        patchState(store, { theme });
        try {
          localStorage.setItem('theme', theme);
          // Apply theme immediately
          document.body.classList.remove('light-theme', 'dark-theme');
          if (theme === 'system') {
            const systemDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
            if (systemDark) {
              document.body.classList.add('dark-theme');
            } else {
              document.body.classList.add('light-theme');
            }
          } else if (theme === 'dark') {
            document.body.classList.add('dark-theme');
          } else if (theme === 'light') {
            document.body.classList.add('light-theme');
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
  })
);
