import { Component, OnInit, OnDestroy } from '@angular/core'; // Import OnInit, OnDestroy
import { RouterOutlet } from '@angular/router';
import { CommonModule } from '@angular/common'; // Import CommonModule for async pipe
import { Subscription } from 'rxjs'; // Import Subscription

// Angular Material Modules
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner'; // For loading indicator

// OIDC Client
import { OidcSecurityService, LoginResponse } from 'angular-auth-oidc-client';

// Import NavbarComponent
import { NavbarComponent } from './core/layout/navbar/navbar.component';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [
    CommonModule, // Add CommonModule
    RouterOutlet,
    MatProgressSpinnerModule, // Add MatProgressSpinnerModule
    NavbarComponent
  ],
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.scss']
})
export class AppComponent implements OnInit, OnDestroy {
  title = 'pylabpraxis-angular';
  isAuthenticated = false; // To track authentication status
  userData: any = null; // To store user data
  isLoading = true; // To show a loading spinner initially

  private authSubscription: Subscription | undefined;
  private userDataSubscription: Subscription | undefined;

  // Inject OidcSecurityService
  constructor(private oidcSecurityService: OidcSecurityService) { }

  ngOnInit() {
    // checkAuth() processes the auth result and returns an observable.
    // It's crucial to call this to complete the login flow after redirect.
    this.authSubscription = this.oidcSecurityService
      .checkAuth()
      .subscribe((loginResponse: LoginResponse) => {
        this.isAuthenticated = loginResponse.isAuthenticated;
        this.userData = loginResponse.userData;
        this.isLoading = false; // Hide spinner after auth check
        console.log('AppComponent: Authentication status:', this.isAuthenticated);
        console.log('AppComponent: User data:', this.userData);
        // You can add further logic here, like navigating based on auth state,
        // but the autoLoginPartialRoutesGuard will handle redirects for protected routes.
      });

    // Optionally, subscribe to isAuthenticated stream for real-time updates
    // This is more robust than just the checkAuth() result if state changes later (e.g. silent renew)
    this.oidcSecurityService.isAuthenticated$.subscribe(({ isAuthenticated }) => {
      this.isAuthenticated = isAuthenticated;
      console.log('AppComponent: isAuthenticated$ changed to:', isAuthenticated);
      if (isAuthenticated) {
        this.oidcSecurityService.userData$.subscribe(({ userData }) => {
          this.userData = userData;
          console.log('AppComponent: userData$ updated:', userData);
        });
      } else {
        this.userData = null;
      }
    });
  }

  ngOnDestroy() {
    // Unsubscribe to prevent memory leaks
    if (this.authSubscription) {
      this.authSubscription.unsubscribe();
    }
    if (this.userDataSubscription) {
      this.userDataSubscription.unsubscribe();
    }
  }

  login() {
    // The autoLoginPartialRoutesGuard will handle login for protected routes.
    // This manual login can be used for a login button if you have public pages.
    this.oidcSecurityService.authorize();
  }

  logout() {
    this.oidcSecurityService
      .logoff()
      .subscribe((result) => console.log('Logout result:', result));
  }
}
