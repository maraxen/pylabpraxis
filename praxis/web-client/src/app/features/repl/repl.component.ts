import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatCardModule } from '@angular/material/card';
import { MatIconModule } from '@angular/material/icon';

@Component({
    selector: 'app-repl',
    standalone: true,
    imports: [CommonModule, MatCardModule, MatIconModule],
    template: `
    <div class="repl-container">
      <mat-card class="repl-card">
        <div class="repl-header">
          <mat-icon>terminal</mat-icon>
          <h2>PyLabRobot REPL</h2>
        </div>
        <div class="repl-content">
          <p>REPL feature coming soon...</p>
        </div>
      </mat-card>
    </div>
  `,
    styles: [`
    .repl-container {
      padding: 24px;
      height: 100%;
      box-sizing: border-box;
    }
    .repl-card {
      height: 100%;
      padding: 24px;
      background: rgba(30, 30, 40, 0.8);
      border: 1px solid rgba(255, 255, 255, 0.1);
      color: white;
    }
    .repl-header {
      display: flex;
      align-items: center;
      gap: 12px;
      margin-bottom: 24px;
    }
    .repl-header mat-icon {
      color: #cd4d6e; /* Primary color approx */
    }
    .repl-header h2 {
      margin: 0;
      font-size: 1.5rem;
    }
    .repl-content {
      display: flex;
      align-items: center;
      justify-content: center;
      height: 300px;
      color: rgba(255, 255, 255, 0.5);
    }
  `]
})
export class ReplComponent { }
