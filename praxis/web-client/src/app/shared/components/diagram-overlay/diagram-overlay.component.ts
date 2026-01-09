import { Component, input, Output, EventEmitter, HostListener } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';

@Component({
    selector: 'app-diagram-overlay',
    standalone: true,
    imports: [CommonModule, MatButtonModule, MatIconModule],
    template: `
    <div class="diagram-overlay" (click)="close()">
      <div class="overlay-content" (click)="$event.stopPropagation()">
        <button mat-icon-button class="close-btn" (click)="close()" title="Close">
          <mat-icon>close</mat-icon>
        </button>
        <div class="diagram-container" [innerHTML]="diagramHtml()"></div>
      </div>
    </div>
  `,
    styles: [`
    .diagram-overlay {
      position: fixed;
      inset: 0;
      background: rgba(0, 0, 0, 0.85);
      backdrop-filter: blur(4px);
      z-index: 2000;
      display: flex;
      align-items: center;
      justify-content: center;
      padding: 32px;
      animation: fadeIn 0.2s ease-out;
    }

    @keyframes fadeIn {
      from { opacity: 0; }
      to { opacity: 1; }
    }

    .overlay-content {
      background: var(--mat-sys-surface);
      border-radius: 20px;
      padding: 40px;
      padding-top: 56px;
      max-width: 95vw;
      max-height: 95vh;
      overflow: auto;
      position: relative;
      box-shadow: 0 24px 48px rgba(0, 0, 0, 0.5);
      border: 1px solid var(--theme-border);
      animation: scaleUp 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
    }

    @keyframes scaleUp {
      from { transform: scale(0.9); opacity: 0; }
      to { transform: scale(1); opacity: 1; }
    }

    .close-btn {
      position: absolute;
      top: 12px;
      right: 12px;
      background: var(--mat-sys-surface-variant);
      color: var(--theme-text-primary);
    }

    .close-btn:hover {
      background: var(--theme-surface-elevated);
    }

    .diagram-container {
      min-width: 800px;
      display: flex;
      justify-content: center;
    }

    :host ::ng-deep .mermaid {
      background: none !important;
      border: none !important;
      padding: 0 !important;
      margin: 0 !important;
    }

    /* Hide the expand button inside the overlay if it was copied */
    :host ::ng-deep .expand-btn {
      display: none !important;
    }
  `]
})
export class DiagramOverlayComponent {
    diagramHtml = input.required<string>();

    @Output() closed = new EventEmitter<void>();

    @HostListener('window:keydown.escape')
    onEscape(): void {
        this.close();
    }

    close(): void {
        this.closed.emit();
    }
}
