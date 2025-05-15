import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
// It's generally good practice for the OidcSecurityService to handle navigation
// after callback processing via postLoginRoute.
// import { Router } from '@angular/router';
// import { OidcSecurityService } from 'angular-auth-oidc-client';

@Component({
  selector: 'app-auth-callback',
  standalone: true,
  imports: [CommonModule, MatProgressSpinnerModule],
  template: `
    <div style="display: flex; flex-direction: column; align-items: center; justify-content: center; height: 80vh;">
      <mat-spinner diameter="50"></mat-spinner>
      <p style="margin-top: 20px;">Processing login...</p>
    </div>
  `,
  // No specific styles needed beyond what MatProgressSpinner provides
})
export class AuthCallbackComponent implements OnInit {
  // The OidcSecurityService and APP_INITIALIZER handle the core logic.
  // This component is primarily a routing target.
  constructor(
    // private router: Router,
    // private oidcSecurityService: OidcSecurityService
  ) { }

  ngOnInit(): void {
    console.log('AuthCallbackComponent loaded. OIDC client should be processing the callback.');
    // Normally, you don't need to do much here.
    // The OidcSecurityService, when checkAuth() is called (by APP_INITIALIZER),
    // will process the URL, exchange the code, and then navigate to postLoginRoute.
    // If for some reason auto-navigation to postLoginRoute fails,
    // you might add a manual check and redirect here, but it's usually not needed.
    //
    // Example of a fallback (generally not required if postLoginRoute is set):
    // this.oidcSecurityService.isAuthenticated$.subscribe(({ isAuthenticated }) => {
    //   if (isAuthenticated) {
    //     this.router.navigate([this.oidcSecurityService.getConfiguration().postLoginRoute || '/home']);
    //   }
    // });
  }
}
