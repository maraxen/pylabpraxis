import { Component } from '@angular/core';
import { CommonModule } from '@angular/common'; // For ngIf, ngFor, etc.

@Component({
  selector: 'app-home',
  standalone: true,
  imports: [CommonModule],
  template: `
    <h2>Welcome to PylabPraxis (Angular)!</h2>
    <p>This is the home page. Authentication will be set up shortly.</p>
  `,
  styles: [`
    :host {
      display: block;
      padding: 20px;
    }
  `]
})
export class HomeComponent { }
