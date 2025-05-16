import { Component, OnInit, OnDestroy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router, RouterModule } from '@angular/router';
import { Subscription } from 'rxjs';
import { map } from 'rxjs/operators'; // Import map operator

// Angular Material Modules
import { MatToolbarModule } from '@angular/material/toolbar';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatMenuModule } from '@angular/material/menu';

// Import your AuthService
import { AuthService, UserProfile } from '../../auth/auth.service'; // Ensure this path is correct

interface NavLink {
  path: string;
  label: string;
  icon?: string;
}

@Component({
  selector: 'app-navbar',
  standalone: true,
  imports: [
    CommonModule,
    RouterModule,
    MatToolbarModule,
    MatButtonModule,
    MatIconModule,
    MatMenuModule
  ],
  templateUrl: './navbar.component.html',
  styleUrls: ['./navbar.component.scss']
})
export class NavbarComponent implements OnInit, OnDestroy {
  isAuthenticated = false;
  userData: UserProfile | null = null; // Use UserProfile type from AuthService
  navLinks: NavLink[] = [
    { path: '/home', label: 'Home', icon: 'home' },
    { path: '/protocols', label: 'Protocols', icon: 'science' },
    { path: '/lab-assets', label: 'Lab Assets', icon: 'biotech' },
    { path: '/settings', label: 'Settings', icon: 'settings' }
  ];

  private authSubscription: Subscription | undefined;
  private userDataSubscription: Subscription | undefined;

  constructor(
    private authService: AuthService, // Use AuthService
    private router: Router
  ) { }

  ngOnInit(): void {
    // Subscribe to isAuthenticated$ from AuthService
    this.authSubscription = this.authService.isAuthenticated$.subscribe(isAuthenticated => {
      this.isAuthenticated = isAuthenticated;
    });

    // Subscribe to userProfile$ from AuthService
    this.userDataSubscription = this.authService.userProfile$.subscribe(userProfile => {
      this.userData = userProfile;
    });
  }

  ngOnDestroy(): void {
    if (this.authSubscription) {
      this.authSubscription.unsubscribe();
    }
    if (this.userDataSubscription) {
      this.userDataSubscription.unsubscribe();
    }
  }

  // The oidc-spa library used by AuthService is configured with autoLogin: true.
  // This means it should automatically redirect to the login page if the user is not authenticated
  // when trying to access a protected resource or upon initialization.
  // If you need an explicit login button:
  async login(): Promise<void> {
    // The current AuthService (using oidc-spa with autoLogin:true)
    // might not require an explicit login() method call here as it handles login automatically.
    // If 'autoLogin' was false in oidc-spa config, or for a specific manual trigger,
    // you'd need to expose a login method in AuthService:
    // await this.authService.login(); // You would need to implement login() in AuthService
    // For now, with autoLogin:true, this button might just navigate to a protected route
    // or you can remove the explicit login button if auto-redirect is sufficient.
    // If you still want a button, consider its purpose.
    // Perhaps navigate to home which might trigger auth if not logged in.
    this.router.navigate(['/home']);
    console.log('Login action triggered. Auto-login with oidc-spa should handle the redirect if not authenticated.');
  }

  async logout(): Promise<void> {
    await this.authService.logout();
    // Navigation after logout is typically handled by post_logout_redirect_uri
    // or the redirectTo option in authService.logout().
  }

  get userDisplayName(): string {
    if (!this.userData) return 'User';
    // Adjust according to the UserProfile structure from AuthService
    return this.userData.name || this.userData.preferred_username || 'User';
  }
}