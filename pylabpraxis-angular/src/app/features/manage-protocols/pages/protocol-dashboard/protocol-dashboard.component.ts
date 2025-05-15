import { Component, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router, RouterModule } from '@angular/router'; // Import Router for navigation

// Angular Material Modules
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatCardModule } from '@angular/material/card';
import { MatDividerModule } from '@angular/material/divider';
import { MatTooltipModule } from '@angular/material/tooltip'; // For tooltips

@Component({
  selector: 'app-protocol-dashboard', // Updated selector
  standalone: true,
  imports: [
    CommonModule,
    RouterModule,
    MatButtonModule,
    MatIconModule,
    MatCardModule,
    MatDividerModule,
    MatTooltipModule
  ],
  templateUrl: './protocol-dashboard.component.html', // Updated template URL
  styleUrls: ['./protocol-dashboard.component.scss']  // Updated style URL
})
export class ProtocolDashboardComponent {
  private router = inject(Router);

  constructor() { }

  navigateToRunNewProtocol(): void {
    this.router.navigate(['/protocols/run-new']);
  }

  navigateToRunHistory(): void {
    this.router.navigate(['/protocols/history']);
  }
}
