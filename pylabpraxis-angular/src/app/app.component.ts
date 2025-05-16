import { Component, OnInit, OnDestroy, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterOutlet } from '@angular/router';
import { NavbarComponent } from './core/layout/navbar/navbar.component';
import { AuthService } from './core/auth/auth.service'; // Import your AuthService
import { Subscription } from 'rxjs';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner'; // For loading indicator

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [
    CommonModule,
    RouterOutlet,
    NavbarComponent,
    MatProgressSpinnerModule // Add MatProgressSpinnerModule for the loading indicator
  ],
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.scss']
})
export class AppComponent implements OnInit, OnDestroy {
  title = 'PylabPraxis Angular Frontend';

  // Inject AuthService using the inject function (or constructor injection)
  private authService = inject(AuthService);

  // Flag to track if OIDC setup is complete.
  // This will be used in the template to show/hide a loading indicator.
  isOidcSetupDone = false;
  private oidcSetupSubscription: Subscription | undefined;

  constructor() {
    // Constructor can be kept empty if inject() is used for authService.
    // If you prefer constructor injection:
    // constructor(private authService: AuthService) {}
  }

  ngOnInit() {
    // The OIDC initialization (AuthService.initializeOidc) is handled by APP_INITIALIZER
    // as configured in app.config.ts.

    // Subscribe to the isOidcSetupDone$ observable from AuthService.
    // This allows the AppComponent to react once the OIDC client has finished its
    // initial setup (e.g., checking for tokens, redirecting, etc.).
    this.oidcSetupSubscription = this.authService.isOidcSetupDone$.subscribe(
      (isDone) => {
        this.isOidcSetupDone = isDone;
        if (isDone) {
          console.log('AppComponent: OIDC setup is complete. Application can now render.');
          // At this point, AuthService.isAuthenticated$ and AuthService.userProfile$
          // will have their initial values. The NavbarComponent will subscribe to these
          // to update its display.
        } else {
          console.log('AppComponent: OIDC setup is in progress...');
        }
      }
    );
  }

  ngOnDestroy(): void {
    // Unsubscribe from observables to prevent memory leaks
    if (this.oidcSetupSubscription) {
      this.oidcSetupSubscription.unsubscribe();
    }
  }
}
