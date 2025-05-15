import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-unauthorized',
  standalone: true,
  imports: [CommonModule],
  template: `
    <h2>Unauthorized Access</h2>
    <p>You do not have permission to view this page, or your session may have expired.</p>
    <p><a routerLink="/home">Go to Home</a></p>
  `,
  styles: [`
    :host {
      display: block;
      padding: 20px;
      text-align: center;
    }
  `]
})
export class UnauthorizedComponent { }
