import { Injectable, inject, signal } from '@angular/core';
import Keycloak from 'keycloak-js';
import { environment } from '../../../environments/environment';

export interface KeycloakUser {
  id: string;
  username: string;
  email: string;
  firstName: string;
  lastName: string;
  roles: string[];
}

@Injectable({
  providedIn: 'root'
})
export class KeycloakService {
  private keycloak: Keycloak | null = null;

  // Reactive signals for auth state
  private _isAuthenticated = signal(false);
  private _user = signal<KeycloakUser | null>(null);
  private _token = signal<string | null>(null);

  // Public readonly signals
  readonly isAuthenticated = this._isAuthenticated.asReadonly();
  readonly user = this._user.asReadonly();
  readonly token = this._token.asReadonly();

  /**
   * Initialize Keycloak. Call this in APP_INITIALIZER.
   * @param options Configuration options
   */
  async init(options?: { onLoad?: 'login-required' | 'check-sso' }): Promise<boolean> {
    this.keycloak = new Keycloak({
      url: environment.keycloak.url,
      realm: environment.keycloak.realm,
      clientId: environment.keycloak.clientId
    });

    try {
      // Create a timeout promise
      const timeoutPromise = new Promise<boolean>((_, reject) => {
        setTimeout(() => reject(new Error('Keycloak initialization timed out')), 10000);
      });

      // Race between init and timeout
      const authenticated = await Promise.race([
        this.keycloak.init({
          onLoad: options?.onLoad || 'check-sso',
          silentCheckSsoRedirectUri: window.location.origin + '/silent-check-sso.html',
          pkceMethod: 'S256',
          checkLoginIframe: false // Disable iframe checks for development
        }),
        timeoutPromise
      ]) as boolean;

      if (authenticated) {
        await this.updateUserState();
        this.setupTokenRefresh();
      }

      this._isAuthenticated.set(authenticated);
      return authenticated;
    } catch (error) {
      console.error('Keycloak initialization failed:', error);
      this._isAuthenticated.set(false);
      return false; // APP_INITIALIZER should not fail app startup
    }
  }

  /**
   * Redirect to Keycloak login page
   */
  login(redirectUri?: string): Promise<void> {
    if (!this.keycloak) {
      throw new Error('Keycloak not initialized');
    }
    return this.keycloak.login({
      redirectUri: redirectUri || window.location.origin + '/app/home'
    });
  }

  /**
   * Redirect to Keycloak registration page
   */
  register(redirectUri?: string): Promise<void> {
    if (!this.keycloak) {
      throw new Error('Keycloak not initialized');
    }
    return this.keycloak.register({
      redirectUri: redirectUri || window.location.origin + '/app/home'
    });
  }

  /**
   * Logout and redirect to Keycloak logout
   */
  logout(redirectUri?: string): Promise<void> {
    if (!this.keycloak) {
      throw new Error('Keycloak not initialized');
    }

    this._isAuthenticated.set(false);
    this._user.set(null);
    this._token.set(null);

    return this.keycloak.logout({
      redirectUri: redirectUri || window.location.origin
    });
  }

  /**
   * Get the current access token
   */
  async getToken(): Promise<string | null> {
    if (!this.keycloak || !this.keycloak.authenticated) {
      return null;
    }

    try {
      // Refresh token if it's about to expire (within 30 seconds)
      await this.keycloak.updateToken(30);
      this._token.set(this.keycloak.token || null);
      return this.keycloak.token || null;
    } catch (error) {
      console.error('Failed to refresh token:', error);
      this.login(); // Redirect to login if refresh fails
      return null;
    }
  }

  /**
   * Check if user has a specific role
   */
  hasRole(role: string): boolean {
    return this.keycloak?.hasRealmRole(role) || false;
  }

  /**
   * Check if user has any of the specified roles
   */
  hasAnyRole(roles: string[]): boolean {
    return roles.some(role => this.hasRole(role));
  }

  /**
   * Get Keycloak account management URL
   */
  getAccountUrl(): string | undefined {
    return this.keycloak?.createAccountUrl();
  }

  private async updateUserState(): Promise<void> {
    if (!this.keycloak || !this.keycloak.authenticated) {
      this._user.set(null);
      this._token.set(null);
      return;
    }

    try {
      const profile = await this.keycloak.loadUserProfile();
      const tokenParsed = this.keycloak.tokenParsed;

      this._user.set({
        id: tokenParsed?.sub || '',
        username: profile.username || '',
        email: profile.email || '',
        firstName: profile.firstName || '',
        lastName: profile.lastName || '',
        roles: tokenParsed?.realm_access?.roles || []
      });

      this._token.set(this.keycloak.token || null);
    } catch (error) {
      console.error('Failed to load user profile:', error);
    }
  }

  private setupTokenRefresh(): void {
    if (!this.keycloak) return;

    // Set up automatic token refresh
    this.keycloak.onTokenExpired = () => {
      this.keycloak?.updateToken(30)
        .then((refreshed) => {
          if (refreshed) {
            this._token.set(this.keycloak?.token || null);
          }
        })
        .catch(() => {
          console.error('Token refresh failed');
          this.logout();
        });
    };

    // Handle auth state changes
    this.keycloak.onAuthSuccess = () => {
      this._isAuthenticated.set(true);
      this.updateUserState();
    };

    this.keycloak.onAuthLogout = () => {
      this._isAuthenticated.set(false);
      this._user.set(null);
      this._token.set(null);
    };
  }
}
