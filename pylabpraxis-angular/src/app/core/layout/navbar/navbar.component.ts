import { Component, OnInit, OnDestroy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router, RouterModule } from '@angular/router'; // Import RouterModule for routerLink
import { Subscription } from 'rxjs';

// Angular Material Modules
import { MatToolbarModule } from '@angular/material/toolbar';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatMenuModule } from '@angular/material/menu'; // For user menu

// OIDC Service
import { OidcSecurityService, UserDataResult } from 'angular-auth-oidc-client';

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
    RouterModule, // Add RouterModule here
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
  userData: any = null; // Or a more specific UserProfile type
  navLinks: NavLink[] = [
    { path: '/home', label: 'Home', icon: 'home' },
    { path: '/protocols', label: 'Protocols', icon: 'science' }, // Placeholder
    { path: '/lab-assets', label: 'Lab Assets', icon: 'biotech' }, // Placeholder
    { path: '/settings', label: 'Settings', icon: 'settings' } // Placeholder
  ];

  private authSubscription: Subscription | undefined;
  private userDataSubscription: Subscription | undefined;

  constructor(
    private oidcSecurityService: OidcSecurityService,
    private router: Router
  ) { }

  ngOnInit(): void {
    this.authSubscription = this.oidcSecurityService.isAuthenticated$
      .subscribe(({ isAuthenticated }) => {
        this.isAuthenticated = isAuthenticated;
        if (isAuthenticated) {
          this.userDataSubscription = this.oidcSecurityService.userData$
            .subscribe(({ userData }: UserDataResult) => {
              this.userData = userData;
            });
        } else {
          this.userData = null;
          if (this.userDataSubscription) {
            this.userDataSubscription.unsubscribe();
          }
        }
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

  login(): void {
    this.oidcSecurityService.authorize();
  }

  logout(): void {
    this.oidcSecurityService.logoff().subscribe(() => {
      // Optional: navigate to a public page or root after logout if not handled by postLogoutRedirectUri
      // this.router.navigate(['/']);
    });
  }

  get userDisplayName(): string {
    if (!this.userData) return 'User';
    return this.userData.name || this.userData.preferred_username || 'User';
  }
}
