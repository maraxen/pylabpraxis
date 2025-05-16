import { Injectable, inject } from '@angular/core';
import { createOidc, type Oidc, type OidcInitializationError } from 'oidc-spa';
import { z } from 'zod';
import { BehaviorSubject, Observable, shareReplay, from } from 'rxjs';
import { Router } from '@angular/router'; // For programmatic navigation if needed

// Zod schema for validating the structure of the decoded ID token.
const decodedIdTokenSchema = z.object({
  preferred_username: z.string(),
  name: z.string().optional(),
  email: z.string().email().optional(),
  sub: z.string().optional(), // Commonly needed subject identifier
});

// TypeScript type inferred from the Zod schema.
export type UserProfile = z.infer<typeof decodedIdTokenSchema>;

@Injectable({
  providedIn: 'root',
})
export class AuthService {
  private router = inject(Router);
  private oidcInstance: Oidc<UserProfile> | undefined;

  private isAuthenticatedSubject = new BehaviorSubject<boolean>(false);
  public isAuthenticated$: Observable<boolean> = this.isAuthenticatedSubject.asObservable().pipe(shareReplay(1));

  private userProfileSubject = new BehaviorSubject<UserProfile | null>(null);
  public userProfile$: Observable<UserProfile | null> = this.userProfileSubject.asObservable().pipe(shareReplay(1));

  // Indicates if the core OIDC setup (createOidc) has completed
  private isOidcSetupDoneSubject = new BehaviorSubject<boolean>(false);
  public isOidcSetupDone$: Observable<boolean> = this.isOidcSetupDoneSubject.asObservable().pipe(shareReplay(1));

  constructor() { }

  /**
   * Initializes the oidc-spa client. Called by APP_INITIALIZER.
   * Relies on autoLogin: true to handle redirects.
   */
  async initializeOidc(): Promise<void> {
    console.log('[AuthService] Initializing OIDC with oidc-spa (autoLogin: true)...');
    if (this.oidcInstance) {
      console.warn('[AuthService] OIDC already initialized.');
      this.isOidcSetupDoneSubject.next(true);
      return;
    }

    try {
      const oidc = await createOidc({
        issuerUri: 'http://localhost:8080/realms/test_realm',
        clientId: 'praxis',
        homeUrl: '/',
        // Keycloak redirects here; oidc-spa processes OIDC params on this URL.
        // Ensure 'http://localhost:4200/' is a Valid Redirect URI in Keycloak.
        autoLogin: true, // Key feature: initiates login if not authenticated.
        postLoginRedirectUrl: "/home", // After oidc-spa processes login at homeUrl, redirect to /home.
        debugLogs: true, // Enable oidc-spa internal logs.
        decodedIdTokenSchema, // Zod schema for ID token validation.
      }).catch((error: OidcInitializationError) => {
        console.error("[AuthService] OIDC Initialization Error (createOidc.catch):", error);
        if (!error.isAuthServerLikelyDown) {
          alert(`OIDC Configuration Error. Please contact support. Details: ${error.message}`);
        } else {
          alert("Authentication server seems to be down. Please try again later.");
        }
        this.isOidcSetupDoneSubject.next(true); // Mark setup as done (failed)
        this.isAuthenticatedSubject.next(false);
        this.userProfileSubject.next(null);
        // Prevent further app execution by returning a non-resolving promise
        return new Promise<never>(() => { });
      });

      this.oidcInstance = oidc as Oidc<UserProfile>; // oidc-spa returns Oidc<UserProfile> on success
      console.log('[AuthService] oidc-spa instance created.');

      // After createOidc (which handles URL parsing and token exchange if on callback):
      // Update authentication state based on the instance.
      if (this.oidcInstance.isUserLoggedIn) {
        // oidcInstance is now Oidc.LoggedIn<UserProfile>
        this.isAuthenticatedSubject.next(true);
        const userProfile = this.oidcInstance.getDecodedIdToken();
        this.userProfileSubject.next(userProfile);
        console.log('[AuthService] User is logged in. Profile:', userProfile?.preferred_username);
      } else {
        // oidcInstance is Oidc.NotLoggedIn
        this.isAuthenticatedSubject.next(false);
        this.userProfileSubject.next(null);
        console.log('[AuthService] User is not logged in.');
        // autoLogin: true should have already triggered a redirect if this path is hit
        // on initial load without OIDC params in URL.
      }

      this.isOidcSetupDoneSubject.next(true);
      console.log('[AuthService] OIDC initialization sequence complete.');

    } catch (error) { // Catch for any other unexpected errors during setup
      console.error('[AuthService] Broader error during OIDC initialization:', error);
      this.isOidcSetupDoneSubject.next(true);
      this.isAuthenticatedSubject.next(false);
      this.userProfileSubject.next(null);
      alert("Critical error during app startup. Authentication may be unavailable.");
    }
  }

  /**
   * Initiates logout.
   */
  async logout(): Promise<void> {
    if (!this.oidcInstance) {
      console.warn('[AuthService] OIDC not initialized. Cannot logout.');
      return;
    }

    if (this.oidcInstance.isUserLoggedIn) { // Type guard
      console.log('[AuthService] Initiating logout...');
      try {
        // The type Oidc.LoggedIn ensures 'logout' is available.
        await this.oidcInstance.logout({ redirectTo: "home" });
        // State will clear on redirect or next app init with autoLogin.
      } catch (error) {
        console.error('[AuthService] Logout failed', error);
      }
    } else {
      console.log('[AuthService] User not logged in, logout call skipped.');
    }
  }
}
